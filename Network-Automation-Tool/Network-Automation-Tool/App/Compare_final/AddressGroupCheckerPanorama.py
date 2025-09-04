# AddressGroupCheckerPanorama.py
import xml.etree.ElementTree as ET
import requests
import logging
import re
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PanoramaAddressGroupChecker:
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

    def get_address_group_memberships(self, address_name):
        """
        Find all address groups that contain the specified address object
        Args:
            address_name: Name of the address object to search for
        Returns:
            list: List of group names that contain this address
        """
        try:
            groups = []
            xpaths = [
                "/config/shared/address-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address-group"
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
                
                # Search for groups containing this address
                for elem in root.findall('.//entry'):
                    group_name = elem.get('name')
                    static = elem.find('static')
                    if static is not None:
                        members = [m.text for m in static.findall('member') if m.text]
                        if address_name in members:
                            groups.append({
                                'name': group_name,
                                'location': 'shared' if 'shared' in xpath else 'device-group'
                            })
            
            return groups
            
        except Exception as e:
            logger.error(f"Error finding address group memberships: {str(e)}")
            return []

    def search_address_group(self, search_term):
        """
        Search for address groups and objects in Panorama with full membership info
        Returns:
            dict: {
                'groups': list of matching groups (each with 'name' and 'details'),
                'objects': list of matching address objects with group memberships
            }
        """
        try:
            results = {'groups': [], 'objects': []}
            
            # Search in shared and device-group address groups
            xpaths = [
                "/config/shared/address-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address-group"
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
                            'type': 'static',  # Default to static
                            'members': [],
                            'location': 'shared' if 'shared' in xpath else 'device-group'
                        }
                        
                        # Check if dynamic group
                        dynamic = elem.find('dynamic')
                        if dynamic is not None:
                            group_details['type'] = 'dynamic'
                            group_details['filter'] = dynamic.findtext('filter', '')
                        else:
                            # Static group - get members
                            static = elem.find('static')
                            if static is not None:
                                members = [m.text for m in static.findall('member') if m.text]
                                group_details['members'] = members
                                
                                # Get details for each member
                                member_details = []
                                for member in members:
                                    if member.startswith('group:'):
                                        # This is a group reference
                                        group_name = member[6:]  # Remove 'group:' prefix
                                        group_obj = self.get_address_group_details(group_name)
                                        if group_obj:
                                            member_details.append({
                                                'name': group_name,
                                                'type': 'group',
                                                'details': group_obj
                                            })
                                    else:
                                        # This is a regular address object
                                        member_obj = self.get_address_object_details(member)
                                        if member_obj:
                                            member_details.append(member_obj)
                                group_details['member_details'] = member_details
                        
                        results['groups'].append({
                            'name': group_name,
                            'details': group_details
                        })
            
            # Search address objects that might match
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
                
                # Search for matching address objects
                for elem in root.findall('.//entry'):
                    object_name = elem.get('name')
                    if search_term.lower() in object_name.lower():
                        object_details = {
                            'name': object_name,
                            'type': None,
                            'value': None,
                            'description': elem.findtext('description', ''),
                            'location': 'shared' if 'shared' in xpath else 'device-group',
                            'groups': self.get_address_group_memberships(object_name)
                        }
                        
                        # Check all possible types
                        for obj_type in ['ip-netmask', 'ip-range', 'fqdn', 'wildcard']:
                            value = elem.findtext(obj_type)
                            if value is not None:
                                object_details['type'] = obj_type
                                object_details['value'] = value
                                break
                        
                        results['objects'].append(object_details)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching address groups: {str(e)}")
            return {'error': str(e)}

    def get_address_object_details(self, name):
        """
        Get details of a specific address object
        Args:
            name: Name of the address object
        Returns:
            dict: Object details or None if not found
        """
        try:
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
                elem = root.find('.//entry')
                if elem is not None:
                    details = {
                        'name': name,
                        'type': None,
                        'value': None,
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    # Check all possible types
                    for obj_type in ['ip-netmask', 'ip-range', 'fqdn', 'wildcard']:
                        value = elem.findtext(obj_type)
                        if value is not None:
                            details['type'] = obj_type
                            details['value'] = value
                            break
                    
                    return details
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting address object details: {str(e)}")
            return None

    def get_address_group_details(self, name):
        """
        Get details of a specific address group
        Args:
            name: Name of the address group
        Returns:
            dict: Group details or None if not found
        """
        try:
            xpaths = [
                "/config/shared/address-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address-group"
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
                        'type': 'static',
                        'members': [],
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    # Check if dynamic group
                    dynamic = elem.find('dynamic')
                    if dynamic is not None:
                        details['type'] = 'dynamic'
                        details['filter'] = dynamic.findtext('filter', '')
                    else:
                        # Static group - get members
                        static = elem.find('static')
                        if static is not None:
                            members = [m.text for m in static.findall('member') if m.text]
                            details['members'] = members
                    
                    return details
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting address group details: {str(e)}")
            return None

    def list_address_objects(self):
        """
        List all address objects in Panorama
        Returns:
            dict: {
                'objects': list of address objects (each with 'name', 'type', 'value')
            }
        """
        try:
            objects = []
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
                
                for elem in root.findall('.//entry'):
                    object_name = elem.get('name')
                    object_details = {
                        'name': object_name,
                        'type': None,
                        'value': None,
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group',
                        'groups': self.get_address_group_memberships(object_name)
                    }
                    
                    # Check all possible types
                    for obj_type in ['ip-netmask', 'ip-range', 'fqdn', 'wildcard']:
                        value = elem.findtext(obj_type)
                        if value is not None:
                            object_details['type'] = obj_type
                            object_details['value'] = value
                            break
                    
                    objects.append(object_details)
            
            return {'objects': objects}
            
        except Exception as e:
            logger.error(f"Error listing address objects: {str(e)}")
            return {'error': str(e)}


    def group_name_exists(self, name):
        """
        Check if an address group with the given name exists
        Returns:
            dict: {'exists': bool, 'error': str if error}
        """
        try:
            # Check both shared and device-group address groups
            xpaths = [
                "/config/shared/address-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address-group"
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
    
    def list_address_groups(self):
        """
        List all address groups in Panorama
        Returns:
            dict: {
                'groups': list of address groups (each with 'name', 'type', 'members')
            }
        """
        try:
            groups = []
            xpaths = [
                "/config/shared/address-group",
                "/config/devices/entry[@name='localhost.localdomain']/device-group//address-group"
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
                        'type': 'static',
                        'members': [],
                        'description': elem.findtext('description', ''),
                        'location': 'shared' if 'shared' in xpath else 'device-group'
                    }
                    
                    # Check if dynamic group
                    dynamic = elem.find('dynamic')
                    if dynamic is not None:
                        group_details['type'] = 'dynamic'
                        group_details['filter'] = dynamic.findtext('filter', '')
                    else:
                        # Static group - get members
                        static = elem.find('static')
                        if static is not None:
                            members = [m.text for m in static.findall('member') if m.text]
                            group_details['members'] = members
                    
                    groups.append(group_details)
            
            return {'groups': groups}
            
        except Exception as e:
            logger.error(f"Error listing address groups: {str(e)}")
            return {'error': str(e)}



    def create_address_group(self, name, members, description='', device_group='shared', group_type='static'):
        """
        Create a new address group in Panorama
        Args:
            name: Name of the group
            members: List of member objects or groups
            description: Optional description
            device_group: Device group (default 'shared')
            group_type: 'static' or 'dynamic' (default 'static')
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
            # Validate group name
            if not name or not isinstance(name, str):
                return {
                    'success': False,
                    'message': 'Group name is required and must be a string'
                }
            
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
            
            # Validate members for static groups
            if group_type == 'static' and (not members or not isinstance(members, list)):
                return {
                    'success': False,
                    'message': 'Static groups require at least one member'
                }

            # Prepare members - no need to prefix with 'group:'
            # The API will automatically handle whether each member is an object or group
            formatted_members = []
            for member in members:
                # Check if member exists as either an address object or group
                obj_details = self.get_address_object_details(member)
                group_details = self.get_address_group_details(member)
                
                if not obj_details and not group_details:
                    return {
                        'success': False,
                        'message': f'Member "{member}" is neither an existing address object nor address group'
                    }
                
                formatted_members.append(member)

            # Prepare the XML payload
            members_xml = '\n'.join([f'<member>{self._escape_xml(m)}</member>' for m in formatted_members])
            xml_payload = f"""<entry name="{self._escape_xml(name)}">
                <static>
                    {members_xml}
                </static>
                <description>{self._escape_xml(description)}</description>
            </entry>"""
            
            # Create in shared location
            xpath = "/config/shared/address-group"
            
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
                'message': f'Successfully created address group {name}',
                'group_name': name,
                'group_details': {
                    'name': name,
                    'type': group_type,
                    'members': formatted_members,
                    'description': description,
                    'device_group': device_group,
                    'location': 'shared'
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating address group: {str(e)}", exc_info=True)
            return {
                'success': False, 
                'message': f'Failed to create group: {str(e)}',
                'error_details': str(e)
            }