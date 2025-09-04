# ServiceGroupCheckerPanorama.py
import xml.etree.ElementTree as ET
import requests
import logging
import re
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PanoramaServiceGroupChecker:
    def __init__(self, panorama_ip='10.1.3.6', 
                 api_key='LUFRPT1JZzRoQTdGakxybGx2MnFPNFN0NmtpTncxZmc9SENZbzFwbWNDZm4xdDVYRHpYZko0UnROSFRqT3lySXR3QXU2YW1lYXE1aEd3a1E5UXprZ3N5Z2M0T25ROE5KUw=='):
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

    def get_service_group_memberships(self, service_name):
        """
        Find all service groups that contain the specified service object or group
        Args:
            service_name: Name of the service object or group to search for
        Returns:
            list: List of group names that contain this service
        """
        try:
            groups = []
            xpaths = [
                "/config/shared/service-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service-group"
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
                
                # Search for groups containing this service
                for elem in root.findall('.//entry'):
                    group_name = elem.get('name')
                    members = [m.text for m in elem.findall('members/member') if m.text]
                    if service_name in members:
                        groups.append({
                            'name': group_name,
                            'location': 'shared' if 'shared' in xpath else 'device-group'
                        })
            
            return groups
            
        except Exception as e:
            logger.error(f"Error finding service group memberships: {str(e)}")
            return []

    def search_service_group(self, search_term):
        """
        Search for service groups and objects in Panorama with full membership info
        Returns:
            dict: {
                'groups': list of matching groups (each with 'name' and 'details'),
                'objects': list of matching service objects with group memberships
            }
        """
        try:
            results = {'groups': [], 'objects': []}
            
            # Search in shared and device-group service groups
            xpaths = [
                "/config/shared/service-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service-group"
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
                
                # Search for matching groups
                for elem in root.findall('.//entry'):
                    group_name = elem.get('name')
                    if search_term.lower() in group_name.lower():
                        group_details = {
                            'name': group_name,
                            'description': elem.findtext('description', ''),
                            'members': [],
                            'tags': [t.text for t in elem.findall('tag/member') if t.text],
                            'location': 'shared' if 'shared' in xpath else 'device-group'
                        }
                        
                        # Get members
                        members = [m.text for m in elem.findall('members/member') if m.text]
                        group_details['members'] = members
                        
                        results['groups'].append({
                            'name': group_name,
                            'details': group_details
                        })
            
            # Search service objects that might match
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
                
                # Search for matching service objects
                for elem in root.findall('.//entry'):
                    object_name = elem.get('name')
                    if search_term.lower() in object_name.lower():
                        object_details = {
                            'name': object_name,
                            'protocol': None,
                            'port': None,
                            'description': elem.findtext('description', ''),
                            'location': 'shared' if 'shared' in xpath else 'device-group',
                            'groups': self.get_service_group_memberships(object_name)
                        }
                        
                        # Check protocol/port combinations
                        for protocol in ['tcp', 'udp']:
                            port_elem = elem.find(protocol)
                            if port_elem is not None:
                                port = port_elem.findtext('port')
                                if port is not None:
                                    object_details['protocol'] = protocol
                                    object_details['port'] = port
                                    break
                                # If port is None but protocol exists
                                object_details['protocol'] = protocol
                                object_details['port'] = 'any'
                        
                        results['objects'].append(object_details)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching service groups: {str(e)}")
            return {'error': str(e)}

    def get_service_object_details(self, name):
        """
        Get details of a specific service object
        Args:
            name: Name of the service object
        Returns:
            dict: Object details or None if not found
        """
        try:
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
                    details = {
                        'name': name,
                        'protocol': None,
                        'port': None,
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    # Check protocol/port combinations
                    for protocol in ['tcp', 'udp']:
                        port_elem = elem.find(protocol)
                        if port_elem is not None:
                            port = port_elem.findtext('port')
                            if port is not None:
                                details['protocol'] = protocol
                                details['port'] = port
                                break
                            # If port is None but protocol exists
                            details['protocol'] = protocol
                            details['port'] = 'any'
                    
                    return details
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting service object details: {str(e)}")
            return None

    def list_service_objects(self):
        """
        List all service objects in Panorama
        Returns:
            dict: {
                'objects': list of service objects (each with 'name', 'protocol', 'port')
            }
        """
        try:
            objects = []
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
                
                for elem in root.findall('.//entry'):
                    object_name = elem.get('name')
                    object_details = {
                        'name': object_name,
                        'protocol': None,
                        'port': None,
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group',
                        'groups': self.get_service_group_memberships(object_name)
                    }
                    
                    # Check protocol/port combinations
                    for protocol in ['tcp', 'udp']:
                        port_elem = elem.find(protocol)
                        if port_elem is not None:
                            port = port_elem.findtext('port')
                            if port is not None:
                                object_details['protocol'] = protocol
                                object_details['port'] = port
                                break
                            # If port is None but protocol exists
                            object_details['protocol'] = protocol
                            object_details['port'] = 'any'
                    
                    objects.append(object_details)
            
            return {'objects': objects}
            
        except Exception as e:
            logger.error(f"Error listing service objects: {str(e)}")
            return {'error': str(e)}
        
    def group_name_exists(self, name):
        """
        Check if a service group with the given name exists
        Returns:
            dict: {'exists': bool, 'error': str if error}
        """
        try:
            # Check both shared and device-group service groups
            xpaths = [
                "/config/shared/service-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service-group"
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
            logger.error(f"Error checking group name: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def list_service_groups(self):
        """
        List all service groups in Panorama
        Returns:
            dict: {
                'groups': list of service groups (each with 'name', 'members')
            }
        """
        try:
            groups = []
            xpaths = [
                "/config/shared/service-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service-group"
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
                
                for elem in root.findall('.//entry'):
                    group_name = elem.get('name')
                    group_details = {
                        'name': group_name,
                        'members': [m.text for m in elem.findall('members/member') if m.text],
                        'description': elem.findtext('description', ''),
                        'tags': [t.text for t in elem.findall('tag/member') if t.text],
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    groups.append(group_details)
            
            return {'groups': groups}
            
        except Exception as e:
            logger.error(f"Error listing service groups: {str(e)}")
            return {'error': str(e)}
        


    def _check_service_object_exists(self, name):
        """Check if a service object with the given name exists"""
        try:
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
                
                root = ET.fromstring(response.text)
                if root.find('.//entry') is not None:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking service object existence: {str(e)}")
            return False

    def _check_service_group_exists(self, name):
        """Check if a service group with the given name exists"""
        try:
            xpaths = [
                "/config/shared/service-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//service-group"
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
                
                root = ET.fromstring(response.text)
                if root.find('.//entry') is not None:
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking service group existence: {str(e)}")
            return False
        
    def create_service_group(self, name, members, device_group='shared', tags=None, description=''):
        """
        Create a new service group in Panorama
        Args:
            name: Name of the group
            members: List of member service objects or groups
            device_group: Device group (default 'shared')
            tags: List of tags (optional)
            description: Description for the group (optional) - Removed from required fields
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'group_name': str if success,
                'group_details': dict if success,
                'error_details': str if error
            }
        """
        try:
            # Validate inputs
            if not name:
                return {'success': False, 'message': 'Group name is required'}
            if not members:
                return {'success': False, 'message': 'At least one member is required'}
            
            # Validate group name format
            if not re.match(r'^[a-zA-Z0-9\-_.]+$', name):
                return {
                    'success': False,
                    'message': 'Group name can only contain letters, numbers, hyphens, underscores and periods'
                }
            
            if len(name) > 63:
                return {
                    'success': False,
                    'message': 'Group name must be 63 characters or less'
                }

            # Check if members exist
            for member in members:
                # Check if member exists as either a service object or group
                obj_exists = self._check_service_object_exists(member)
                group_exists = self._check_service_group_exists(member)
                
                if not obj_exists and not group_exists:
                    return {
                        'success': False,
                        'message': f'Member "{member}" is neither an existing service object nor service group'
                    }

            # Prepare XML payload - removed description field
            members_xml = '\n'.join([f'<member>{self._escape_xml(m)}</member>' for m in members])
            tags_xml = ''
            if tags:
                tags_xml = '<tag>' + ''.join([f'<member>{self._escape_xml(t)}</member>' for t in tags]) + '</tag>'
            
            xml_payload = f"""
            <entry name="{self._escape_xml(name)}">
                <members>
                    {members_xml}
                </members>
                {tags_xml}
            </entry>
            """

            # Determine the correct XPath based on device group
            if device_group.lower() == 'shared':
                xpath = "/config/shared/service-group"
            else:
                xpath = f"/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='{device_group}']/service-group"

            # Create the group
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

            # Check if creation was successful
            root = ET.fromstring(response.text)
            if root.attrib.get('status') != 'success':
                error_msg = self._extract_error_message(response.text)
                return {
                    'success': False,
                    'message': f'Failed to create group: {error_msg}',
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
                    'message': f'Group created but commit failed: {error_msg}',
                    'panorama_response': commit_response.text
                }

            return {
                'success': True, 
                'message': f'Successfully created service group {name}',
                'group_name': name,
                'group_details': {
                    'name': name,
                    'members': members,
                    'tags': tags or [],
                    'device_group': device_group,
                    'location': 'shared' if device_group.lower() == 'shared' else 'device-group'
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating service group: {str(e)}", exc_info=True)
            return {
                'success': False, 
                'message': f'Failed to create group: {str(e)}',
                'error_details': str(e)
            }
            