# objectcheckerpanorama.py
import xml.etree.ElementTree as ET
import requests
import ipaddress
import logging
import re
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PanoramaObjectChecker:
    def __init__(self, panorama_ip='10.1.3.6', api_key='LUFRPT1JZzRoQTdGakxybGx2MnFPNFN0NmtpTncxZmc9SENZbzFwbWNDZm4xdDVYRHpYZko0UnROSFRqT3lySXR3QXU2YW1lYXE1aEd3a1E5UXprZ3N5Z2M0T25ROE5KUw=='):
        self.panorama_ip = panorama_ip
        self.api_key = api_key
        self.base_url = f"https://{self.panorama_ip}/api"
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.timeout = 30  # seconds
        
    def _make_api_request(self, method='GET', url_suffix='', params=None, data=None):
        """Helper method to make API requests to Panorama"""
        try:
            url = f"{self.base_url}{url_suffix}"
            params = params or {}
            params['key'] = self.api_key
            
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    verify=False,
                    timeout=self.timeout
                )
            else:
                response = requests.post(
                    url,
                    params=params,
                    data=data,
                    headers=self.headers,
                    verify=False,
                    timeout=self.timeout
                )
                
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"Failed to connect to Panorama: {str(e)}")
    
    def _validate_address(self, address, obj_type):
        """Validate address based on type"""
        if address == "any":
            return True
            
        if obj_type == "ip-netmask":
            try:
                ipaddress.ip_network(address, strict=False)
                return True
            except ValueError:
                return False
                
        elif obj_type == "ip-range":
            ip_range_pattern = r'^(\d{1,3}\.){3}\d{1,3}\-(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_range_pattern, address):
                return False
            start_ip, end_ip = address.split('-')
            try:
                # Validate both IPs
                ipaddress.ip_address(start_ip)
                ipaddress.ip_address(end_ip)
                # Ensure start IP is less than end IP
                if ipaddress.ip_address(start_ip) >= ipaddress.ip_address(end_ip):
                    return False
                return True
            except ValueError:
                return False
                
        elif obj_type == "fqdn":
            fqdn_pattern = r'^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$'
            return re.match(fqdn_pattern, address) is not None
            
        elif obj_type == "wildcard":
            parts = address.split('/')
            if len(parts) != 2:
                return False
            ip_part, mask_part = parts
            try:
                ipaddress.ip_address(ip_part)
                ipaddress.ip_address(mask_part)
                return True
            except ValueError:
                return False
                
        return False
    
    def _escape_xml(self, text):
        """Helper method to escape XML special characters"""
        if not text:
            return text
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))
    
    def _extract_error_message(self, xml_response):
        """Extract error message from Panorama XML response"""
        try:
            root = ET.fromstring(xml_response)
            # Try to find the most specific error message
            for elem in root.findall('.//line'):
                if elem.text and elem.text.strip():
                    return elem.text.strip()
            # Fallback to the general message
            msg = root.find('.//msg')
            if msg is not None and msg.text:
                return msg.text.strip()
            return xml_response
        except Exception:
            return xml_response
    
    def object_exists(self, address):
        """
        Check if address objects exist in Panorama
        Returns:
            dict: {
                'exists': bool, 
                'objects': list of dicts if exists (each with 'object_name' and 'object_details')
            }
        """
        try:
            matching_objects = []
            # Check both shared and device-group objects
            xpaths = [
                "/config/shared/address",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address"
            ]
            
            for xpath in xpaths:
                response = self._make_api_request(
                    'GET',
                    "",
                    params={
                        'type': 'config',
                        'action': 'get',
                        'xpath': xpath
                    }
                )
                
                # Parse XML response
                root = ET.fromstring(response.text)
                
                # Search for the address in all objects
                for elem in root.findall('.//entry'):
                    object_name = elem.get('name')
                    object_details = {
                        'name': object_name,
                        'description': elem.findtext('description', ''),
                        'disabled': elem.findtext('disabled', 'no') == 'yes',
                        'type': None,
                        'value': None,
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    # Check all possible types
                    for obj_type in ['ip-netmask', 'ip-range', 'fqdn', 'wildcard']:
                        value = elem.findtext(obj_type)
                        if value is not None:
                            object_details['type'] = obj_type
                            object_details['value'] = value
                            if value == address:
                                matching_objects.append({
                                    'object_name': object_name,
                                    'object_details': object_details
                                })
                                break
            
            if matching_objects:
                return {
                    'exists': True,
                    'objects': matching_objects
                }
            else:
                return {'exists': False}
                
        except Exception as e:
            logger.error(f"Error checking address object: {str(e)}")
            return {'exists': False, 'error': str(e)}

    # Add this method to the PanoramaObjectChecker class
    # Add this method to the PanoramaObjectChecker class
    def object_name_exists(self, name):
        """
        Check if an object with the given name exists in Panorama
        Returns:
            dict: {'exists': bool, 'error': str if error}
        """
        try:
            # Check both shared and device-group objects
            xpaths = [
                "/config/shared/address",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address"
            ]
            
            for xpath in xpaths:
                response = self._make_api_request(
                    'GET',
                    "",
                    params={
                        'type': 'config',
                        'action': 'get',
                        'xpath': f"{xpath}/entry[@name='{name}']"
                    }
                )
                
                # Parse XML response
                root = ET.fromstring(response.text)
                if root.find('.//entry') is not None:
                    return {'exists': True}
                    
            return {'exists': False}
            
        except Exception as e:
            logger.error(f"Error checking object name: {str(e)}")
            return {'exists': False, 'error': str(e)}
    def create_object(self, name, address, obj_type='ip-netmask', device_group='shared', 
                    description='', shared=True, disabled=False):
        """
        Create a new address object in Panorama (simplified version)
        """
        try:
            # Validate object name
            if not name or not isinstance(name, str):
                return {
                    'success': False,
                    'message': 'Object name is required and must be a string'
                }
            
            if not re.match(r'^[a-zA-Z0-9\-_.]+$', name):
                return {
                    'success': False,
                    'message': 'Object name can only contain letters, numbers, hyphens, underscores and periods'
                }
            
            if len(name) > 63:
                return {
                    'success': False,
                    'message': 'Object name must be 63 characters or less'
                }
            
            # Validate address
            if not address:
                return {
                    'success': False,
                    'message': 'Address value is required'
                }
            
            if not self._validate_address(address, obj_type):
                return {
                    'success': False, 
                    'message': f'Invalid {obj_type} format: {address}'
                }
            
            # Prepare the XML payload with proper escaping
            xml_payload = f"""<entry name="{self._escape_xml(name)}">
                <{obj_type}>{self._escape_xml(address)}</{obj_type}>
                <description>{self._escape_xml(description)}</description>
            </entry>"""

            # Always create in shared location
            xpath = "/config/shared/address"
            
            # Create the object
            response = self._make_api_request(
                'POST',
                "",
                params={
                    'type': 'config',
                    'action': 'set',
                    'xpath': xpath,
                    'element': xml_payload
                }
            )
            
            # Check if the creation was successful
            root = ET.fromstring(response.text)
            if root.attrib.get('status') != 'success':
                error_msg = self._extract_error_message(response.text)
                return {
                    'success': False,
                    'message': f'Failed to create object: {error_msg}',
                    'panorama_response': response.text
                }
            
            # Commit the changes
            commit_response = self._make_api_request(
                'POST',
                "",
                params={
                    'type': 'commit',
                    'cmd': '<commit></commit>'
                }
            )
            
            # Verify commit was successful
            commit_root = ET.fromstring(commit_response.text)
            if commit_root.attrib.get('status') != 'success':
                error_msg = self._extract_error_message(commit_response.text)
                return {
                    'success': False,
                    'message': f'Object created but commit failed: {error_msg}',
                    'panorama_response': commit_response.text
                }
            
            return {
                'success': True, 
                'message': f'Successfully created {obj_type} object {name}',
                'object_name': name,
                'object_details': {
                    'name': name,
                    'type': obj_type,
                    'value': address,
                    'description': description,
                    'disabled': False,
                    'shared': True,
                    'device_group': 'shared'
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating address object: {str(e)}", exc_info=True)
            return {
                'success': False, 
                'message': f'Failed to create object: {str(e)}',
                'error_details': str(e)
            }