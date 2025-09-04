# ServiceObjectCheckerPanorama.py
import xml.etree.ElementTree as ET
import requests
import logging
import re
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PanoramaServiceObjectChecker:
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
    
    def _validate_port(self, port):
        """Validate port format (single, range, or comma-separated)"""
        if not port:
            return False
            
        # Check for comma-separated ports
        if ',' in port:
            ports = port.split(',')
            for p in ports:
                if not self._validate_single_port(p.strip()):
                    return False
            return True
            
        # Check for port range
        if '-' in port:
            parts = port.split('-')
            if len(parts) != 2:
                return False
            try:
                start = int(parts[0])
                end = int(parts[1])
                return 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end
            except ValueError:
                return False
                
        # Single port
        return self._validate_single_port(port)
    
    def _validate_single_port(self, port):
        """Validate a single port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except ValueError:
            return False
    
    def service_exists(self, protocol, port):
        """
        Check if service objects exist in Panorama matching the exact protocol and port
        Returns:
            dict: {
                'exists': bool, 
                'objects': list of dicts if exists (each with 'object_name' and 'object_details')
            }
        """
        try:
            if protocol.lower() not in ['tcp', 'udp', 'sctp']:
                return {
                    'exists': False,
                    'error': 'Invalid protocol. Must be tcp, udp, or sctp'
                }
            
            if not self._validate_port(port):
                return {
                    'exists': False,
                    'error': 'Invalid port format. Must be single port, range (1-65535), or comma-separated list'
                }
            
            matching_objects = []
            # Check both shared and device-group objects
            xpaths = [
                "/config/shared/service",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service"
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
                
                # Search for services matching protocol and exact port
                for elem in root.findall('.//entry'):
                    object_name = elem.get('name')
                    service_protocol = elem.findtext('protocol/' + protocol.lower())
                    if service_protocol is not None:
                        # Check exact port match
                        port_element = elem.find(f'protocol/{protocol.lower()}/port')
                        if port_element is not None:
                            service_port = port_element.text
                            if service_port == port:  # Only exact matches
                                object_details = {
                                    'name': object_name,
                                    'description': elem.findtext('description', ''),
                                    'protocol': protocol.lower(),
                                    'port': service_port,
                                    'location': 'shared' if 'shared' in xpath else 'device-group'
                                }
                                matching_objects.append({
                                    'object_name': object_name,
                                    'object_details': object_details
                                })
            
            if matching_objects:
                return {
                    'exists': True,
                    'objects': matching_objects
                }
            else:
                return {'exists': False}
                
        except Exception as e:
            logger.error(f"Error checking service object: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
 
    def create_service(self, name, protocol, port, description='', tags=None, device_group='shared'):
        """
        Create a new service object in Panorama
        """
        try:
            # Validate object name
            if not name or not isinstance(name, str):
                return {
                    'success': False,
                    'message': 'Service name is required and must be a string'
                }
            
            if not re.match(r'^[a-zA-Z0-9\-_.]+$', name):
                return {
                    'success': False,
                    'message': 'Service name can only contain letters, numbers, hyphens, underscores and periods'
                }
            
            if len(name) > 63:
                return {
                    'success': False,
                    'message': 'Service name must be 63 characters or less'
                }
            
            # Validate protocol
            protocol = protocol.lower()
            if protocol not in ['tcp', 'udp', 'sctp']:
                return {
                    'success': False,
                    'message': 'Invalid protocol. Must be tcp, udp, or sctp'
                }
            
            # Validate port
            if not self._validate_port(port):
                return {
                    'success': False,
                    'message': 'Invalid port format. Must be single port, range (1-65535), or comma-separated list'
                }
            
            # Prepare the XML payload with proper escaping
            port_xml = f"<port>{self._escape_xml(port)}</port>"
            
            xml_payload = f"""<entry name="{self._escape_xml(name)}">
                <protocol>
                    <{protocol}>
                        {port_xml}
                    </{protocol}>
                </protocol>
                <description>{self._escape_xml(description)}</description>"""
            
            # Add tags if provided
            if tags:
                tags_xml = "<tag>"
                for tag in [t.strip() for t in tags.split(',') if t.strip()]:
                    tags_xml += f"<member>{self._escape_xml(tag)}</member>"
                tags_xml += "</tag>"
                xml_payload += tags_xml
            
            xml_payload += "</entry>"

            # Always create in shared location
            xpath = "/config/shared/service"
            
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
                    'message': f'Failed to create service: {error_msg}',
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
                    'message': f'Service created but commit failed: {error_msg}',
                    'panorama_response': commit_response.text
                }
            
            return {
                'success': True, 
                'message': f'Successfully created {protocol} service {name}',
                'object_name': name,
                'object_details': {
                    'name': name,
                    'protocol': protocol,
                    'port': port,
                    'description': description,
                    'tags': [t.strip() for t in tags.split(',')] if tags else [],
                    'device_group': 'shared'
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating service object: {str(e)}", exc_info=True)
            return {
                'success': False, 
                'message': f'Failed to create service: {str(e)}',
                'error_details': str(e)
            }
        

    def service_name_exists(self, name):
        """Check if a service object exists by name across all device groups"""
        try:
            matching_objects = []
            # Check both shared and device-group objects
            xpaths = [
                "/config/shared/service",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service"
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
                elem = root.find('.//entry')
                if elem is not None:
                    object_details = {
                        'name': name,
                        'protocol': None,
                        'port': None,
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    # Check protocol/port combinations
                    for protocol in ['tcp', 'udp', 'sctp']:
                        port_elem = elem.find(f'protocol/{protocol}')
                        if port_elem is not None:
                            port = port_elem.findtext('port')
                            object_details['protocol'] = protocol
                            object_details['port'] = port or 'any'
                            break
                    
                    matching_objects.append({
                        'object_name': name,
                        'object_details': object_details
                    })
            
            if matching_objects:
                return {
                    'exists': True,
                    'objects': matching_objects
                }
            else:
                return {'exists': False}
                
        except Exception as e:
            logger.error(f"Error checking service name: {str(e)}")
            return {'exists': False, 'error': str(e)}
