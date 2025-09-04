import os
import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from panos.panorama import Panorama, DeviceGroup
from panos.firewall import Firewall
from panos.objects import ServiceObject
from panos.policies import PreRulebase, PostRulebase, SecurityRule
from panos.objects import Tag
from .validations import PanoramaValidator
from panos.network import Zone

logger = logging.getLogger(__name__)

class RuleManager:
    def __init__(self):
        self.PANORAMA_IP = os.getenv('PANORAMA_IP', '10.1.3.6')
        self.API_KEY = os.getenv('API_KEY', 'LUFRPT16Z3QvYVpZK052NVloQ3FLV1lUd1M5dWMrUEk9SENZbzFwbWNDZm4xdDVYRHpYZko0UnROSFRqT3lySXR3QXU2YW1lYXE1aEcvMHNScFVyL1pabmVIclpRRFM5Rw==')
        self.panorama = Panorama(self.PANORAMA_IP, api_key=self.API_KEY)
        self.validator = PanoramaValidator(self.PANORAMA_IP, self.API_KEY)
        self.device_groups = []
        self.firewalls = []
        self.rule_locations = []


    def validate_rule_data(self, rule_data):
        """Validate all rule data before creation"""
        # Rule name validation
        valid, msg = self.validator.validate_rule_name(
            rule_data.get('name'),
            rule_data.get('rule_type', 'pre'),
            rule_data.get('location', 'shared')
        )
        if not valid:
            return False, msg
            
        # IP address validation - now accepts object names too
        for field in ['sourceIP', 'destinationIP']:
            if field in rule_data:
                valid, msg = self.validator.validate_ip_address(rule_data[field])
                if not valid:
                    return False, f"{field}: {msg}"
                    
        # Service validation - updated to handle protocol/port format
        if 'destinationPort' in rule_data:
            valid, msg = self.validator.validate_services([rule_data['destinationPort']])
            if not valid:
                return False, f"Service: {msg}"
                
        # Application validation
        if 'application' in rule_data:
            valid, msg = self.validator.validate_applications([rule_data['application']])
            if not valid:
                return False, f"Application: {msg}"
                
        return True, "Validation passed"

# AddingRule.py - Update the list_applications method
    def list_applications(self):
        """List all applications from Panorama"""
        try:
            all_applications = set()
            
            # Get shared applications
            xpath = "/config/shared/application"
            url = f"https://{self.PANORAMA_IP}/api/?type=config&action=get&xpath={xpath}&key={self.API_KEY}"
            response = requests.get(url, verify=False, timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                # Look for application entries in the response
                for entry in root.findall('.//entry'):
                    app_name = entry.get('name')
                    if app_name:
                        all_applications.add(app_name)
                
                # Also check for applications in the result section
                for entry in root.findall('.//result/application/entry'):
                    app_name = entry.get('name')
                    if app_name:
                        all_applications.add(app_name)
            
            # Get device-group specific applications
            device_groups = DeviceGroup.refreshall(self.panorama)
            for dg in device_groups:
                xpath = f"/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='{dg.name}']/application"
                url = f"https://{self.PANORAMA_IP}/api/?type=config&action=get&xpath={xpath}&key={self.API_KEY}"
                response = requests.get(url, verify=False, timeout=30)
                
                if response.status_code == 200:
                    root = ET.fromstring(response.text)
                    for entry in root.findall('.//entry'):
                        app_name = entry.get('name')
                        if app_name:
                            all_applications.add(app_name)
                    for entry in root.findall('.//result/application/entry'):
                        app_name = entry.get('name')
                        if app_name:
                            all_applications.add(app_name)
            
            # Convert to sorted list
            app_list = sorted(list(all_applications))
            
            # Add 'any' if not present
            if 'any' not in app_list:
                app_list.insert(0, 'any')
            
            logger.info(f"Found {len(app_list)} applications in Panorama")
            return {
                'status': 'success',
                'applications': app_list
            }
            
        except Exception as e:
            logger.error(f"Error listing applications: {str(e)}", exc_info=True)
            # Return the comprehensive list you provided as fallback
            comprehensive_apps = [
                '1c-enterprise', '1und1-mail', '2ch', '2ch-base', '2ch-posting', '3pc', 
                '4shared', '4sync', '7shifts', '8x8', '24sevenoffice', '51.com', 
                '51.com-base', '51.com-games', '51.com-music', '51.com-webdisk', 
                '51.com-bbs', '51.com-posting', '51.com-mail', '100bao', 
                '360-safeguard-update', 'abb-cls', 'abb-iac', 'abb-netconfig', 
                'abb-network-manager', 'abb-rnrp', 'abb-rp570', 'abb-show-remote-system', 
                'abbott-poca', 'abbott-rals-http', 'abbott-ralsui', 'abbott-serial', 
                'abiomed-remote-link', 'absolute-manage', 'accellion', 'accelo', 
                'access-grid', 'acellus', 'acme-protocol', 'acronis-cloud-backup', 
                'acronis-snapdeploy', 'active-directory', 'active-directory-base', 
                'ms-directory-service-setup', 'ms-dc-replication', 'activenet', 
                'activesync', 'ad-selfservice', 'adam-event-trigger', 'adam-net-utility', 
                'addp', 'addp-base', 'addp-discovery-response', 'addp-discovery-request', 
                'addp-reboot-request', 'addp-reboot-response', 'addp-dhcp-network-config-resp', 
                'addp-dhcp-network-config-req', 'addp-static-network-config-req', 
                'addp-static-network-config-resp', 'adnstream', 'adobe-cloud', 
                'adobe-connect', 'adobe-meeting', 'adobe-meeting-remote-control', 
                'adobe-meeting-file-transfer', 'adobe-meeting-desktop-sharing', 
                'adobe-meeting-uploading', 'adobe-connectnow', 'adobe-connectnow-base', 
                'adobe-connectnow-file-transfer', 'adobe-connectnow-remote-control', 
                'adobe-cq', 'adobe-creative-cloud', 'adobe-creative-cloud-base', 
                'adobe-creative-cloud-uploading', 'adobe-echosign', 'adobe-express', 
                'adobe-express-base', 'adobe-express-download', 'adobe-express-post', 
                'adobe-express-upload', 'adobe-firefly', 'adobe-firefly-base', 
                'adobe-firefly-download', 'adobe-firefly-post', 'adobe-firefly-upload', 
                'adobe-flash-socketpolicy-server', 'adobe-media-player', 
                'adobe-online-office', 'adobe-update', 'adrive', 'advantech-adam-ascii', 
                'aeroadmin', 'aerofs', 'aerospike', 'afaria', 'afp', 'afreeca', 'afs', 
                'afterschool', 'agiloft', 'agora-streaming', 'ai-wordsmith', 
                'ai-wordsmith-base', 'ai-wordsmith-delete', 'ai-wordsmith-move', 
                'ai-wordsmith-save', 'ai-wordsmith-upload', 'aible', 'aible-base', 
                'aible-upload', 'aim', 'aim-base', 'aim-file-transfer', 'aim-video', 
                'aim-audio', 'aim-express', 'aim-express-base', 'aim-express-file-transfer', 
                'aim-mail', 'aiosfoundation-openagi', 'aiosfoundation-openagi-base', 
                'aiosfoundation-openagi-download', 'aiosfoundation-openagi-upload', 
                'air-video', 'airaim', 'airdroid', 'airtable', 'airtable-base', 
                'airtable-uploading', 'airtable-downloading', 'airtable-sharing', 
                'airtable-posting', 'airtable-editing', 'airtime', 'airwatch', 
                'akamai-client', 'aladdin', 'alaris-dcmp', 'alfresco', 'ali-wangwang', 
                'ali-wangwang-file-transfer', 'ali-wangwang-audio-video', 
                'ali-wangwang-base', 'ali-wangwang-remote-control', 'alipay', 'alisoft', 
                'all-slots-casino', 'allpeers', 'alpemix', 'alpha-anywhere', 
                'altamont-outbox-burner-id', 'alteryx', 'alteryx-aidin', 'alteryx-base', 
                'alteryx-aidin-create', 'alteryx-aidin-delete', 'altiris', 'amazon-alexa', 
                'amazon-aws-console', 'amazon-bedrock', 'amazon-bedrock-base', 
                'amazon-bedrock-delete', 'amazon-bedrock-upload', 'amazon-chime', 
                'amazon-chime-base', 'amazon-chime-instant-messaging', 
                'amazon-chime-conferencing', 'amazon-chime-screen-sharing', 
                'amazon-cloud-drive', 'amazon-cloud-drive-base', 
                'amazon-cloud-drive-uploading', 'amazon-cloud-player', 
                'amazon-codewhisperer', 'amazon-cognito', 'amazon-cognito-base', 
                'amazon-cognito-delete', 'amazon-cognito-download', 'amazon-echo', 
                'amazon-echo-conntest', 'amazon-fire-tablet-conntest', 
                'amazon-fire-tv-conntest', 'amazon-instant-video', 'amazon-luna', 
                'amazon-music', 'amazon-music-base', 'amazon-music-streaming', 
                'amazon-nova-reel', 'amazon-polly', 'amazon-polly-base', 
                'amazon-polly-delete', 'amazon-polly-upload', 'amazon-prime-video', 
                'amazon-q', 'amazon-redshift', 'amazon-sagemaker', 'amazon-sagemaker-base', 
                'amazon-sagemaker-create', 'amazon-sagemaker-delete', 
                'amazon-sagemaker-gndtru-create', 'amazon-sagemaker-gndtru-delete', 
                'amazon-sagemaker-groundtruth', 'amazon-titan', 'amazon-titan-base', 
                'amazon-titan-embed', 'amazon-titan-image', 'amazon-titan-text', 
                'amazon-transcribe', 'amazon-transcribe-base', 'amazon-transcribe-create', 
                'amazon-transcribe-delete', 'amazon-transcribe-edit', 
                'amazon-transcribe-live', 'amazon-unbox', 'amazon-workspace', 
                'ameba-blog-posting', 'ameba-now', 'ameba-now-base', 'ameba-now-posting', 
                'ammyy-admin', 'amqp', 'amx-icsp', 'andover-continuum', 'android-market', 
                'anthropic-api', 'anthropic-api-base', 'anthropic-api-post', 'ants-p2p', 
                'any-0hop-protocol', 'anydesk', 'anyplace-remote-control', 'anysupport', 
                'anyterm', 'anyword', 'anyword-base', 'anyword-delete', 'anyword-upload', 
                'aol-messageboard-posting', 'aol-proxy', 'aomei-anyviewer', 
                'apache-activemq-openwire', 'apache-guacamole', 'apache-jserv', 
                'apache-solr', 'apache-zookeeper', 'apc-powerchute', 
                'aperio-eslide-manager', 'apex-legends', 'aporeto', 'appcelerator', 
                'appdynamics', 'appetize.io', 'appguru', 'apple-airplay', 'apple-airport', 
                'apple-appstore', 'apple-game-center', 'apple-location-service', 
                'apple-maps', 'apple-push-notifications', 'apple-remote-desktop', 
                'apple-siri', 'apple-update', 'apple-vpp', 'applejuice', 'appletvplus', 
                'appneta', 'appogee', 'appointy', 'apptivo', 'apt-get', 'arcgis', 
                'arcgis-base', 'arcgis-uploading', 'arcserve', 'ares', 'argus', 
                'ariba-by-sap', 'ariel', 'aris', 'aruba-papi', 'as2', 'asana', 
                'asana-base', 'asana-uploading', 'asana-downloading', 'asf-streaming', 
                'ask.fm', 'aspentech-cim-io', 'asproxy', 'assa-abloy-r3', 'assembla', 
                'assembla-base', 'assembla-uploading', 'asterisk-iax', 'asus-webstorage', 
                'atempo-tina', 'atera', 'atera-base', 'atera-delete', 'atera-download', 
                'atera-logout', 'atlas-copco-toolstalk-fms', 'atlas-copco-toolstalk2', 
                'atlassian-bamboo-cloud', 'atmail', 'atom', 'att-connect', 'att-locker', 
                'att-office-at-hand', 'audiosonic', 'audiosonic-base', 'audiosonic-create', 
                'audiosonic-delete', 'audiosonic-download', 'authentic8-silo', 'autobahn', 
                'autodesk360', 'autodesk360-base', 'autodesk360-uploading', 'ava-aware', 
                'avamar', 'avast-av-update', 'avaya-phone-ping', 'avaya-spaces', 
                'avaya-webalive', 'avaya-webalive-base', 'avaya-webalive-file-transfer', 
                'avaya-webalive-voice', 'avaya-webalive-desktop-sharing', 'avg-update', 
                'avid-isis', 'avid-nexis', 'avira-antivir-update', 'avocent', 
                'avocent-vsp', 'avoidr', 'awesun', 'aws-iot', 'aws-workdocs', 'ax.25', 
                'axifile', 'axis-camera-station-web-client', 'azure-custom-speech', 
                'azure-custom-speech-base', 'azure-custom-speech-download', 
                'azure-custom-speech-upload', 'azure-govt-cloud-blob', 
                'azure-govt-cloud-file', 'azure-govt-cloud-storage', 
                'azure-govt-cloud-table', 'azure-govt-key-vault', 'azure-iot', 'azureus', 
                'babelgum', 'babylon', 'backblaze-backup', 'backpack-editing', 
                'backup-exec', 'backweb', 'bacnet', 'any'
            ]
            return {
                'status': 'success',
                'applications': sorted(comprehensive_apps)
            }
        
    def get_hierarchy(self):
        """Get the full hierarchy of device groups and firewalls"""
        try:
            # First discover the environment
            discovery = self.discover_environment()
            if 'error' in discovery:
                return discovery

            # Fetch firewall info
            op_cmd = '<show><devices><all></all></devices></show>'
            url = f'https://{self.PANORAMA_IP}/api/?type=op&cmd={op_cmd}&key={self.API_KEY}'
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
            
            # Parse firewall info
            serial_to_hostname = {}
            root = ET.fromstring(response.text)
            for fw in root.findall(".//result/devices/entry"):
                serial = fw.findtext('serial') or fw.get('name')
                hostname = fw.findtext('hostname') or fw.get('hostname')
                if serial and hostname:
                    serial_to_hostname[serial] = hostname
            
            # Fetch full config
            config_url = f'https://{self.PANORAMA_IP}/api/?type=export&category=configuration&key={self.API_KEY}'
            config_response = requests.get(config_url, verify=False, timeout=30)
            config_response.raise_for_status()
            
            # Parse device groups
            dg_parents = {}
            fw_to_dg = {}
            config_root = ET.fromstring(config_response.text)
            
            dg_entries = config_root.findall(".//devices/entry[@name='localhost.localdomain']/device-group/entry")
            for dg in dg_entries:
                name = dg.get('name')
                parent = dg.findtext('parent-dg') if dg.find('parent-dg') is not None else 'shared'
                dg_parents[name] = parent
                
                devices = dg.find('devices')
                if devices is not None:
                    for fw in devices.findall('entry'):
                        serial = fw.get('name')
                        fw_to_dg[serial] = name
            
            # Build hierarchy tree structure
            hierarchy_tree = self._build_hierarchy_tree(dg_parents)
            
            # Format the response with tree structure
            formatted_data = []
            for serial, hostname in serial_to_hostname.items():
                current_dg = fw_to_dg.get(serial)
                path = []
                
                if current_dg:
                    path = self._get_hierarchy_path(current_dg, dg_parents)
                
                path.append(hostname)
                
                formatted_data.append({
                    'serial': serial,
                    'hostname': hostname,
                    'path': path,
                    'hierarchy': self._convert_path_to_tree(path)
                })
            
            return {
                'status': 'success',
                'data': formatted_data,
                'tree': hierarchy_tree,
                'device_groups': [dg.name for dg in self.device_groups],
                'firewalls': [fw.serial for fw in self.firewalls],
                'rule_locations': self.rule_locations
            }
            
        except Exception as e:
            logger.error(f"Error in get_hierarchy: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def discover_environment(self):
        """Discover device groups, firewalls, and rule locations"""
        try:
            # Refresh device groups
            self.device_groups = DeviceGroup.refreshall(self.panorama)
            
            # Refresh firewalls (only actual firewall devices)
            self.firewalls = [fw for fw in self.panorama.refresh_devices() if isinstance(fw, Firewall)]
            
            # Build rule locations
            self.rule_locations = ['shared'] + [dg.name for dg in self.device_groups]
            
            logger.info(f"Discovered device groups: {[dg.name for dg in self.device_groups]}")
            logger.info(f"Discovered firewalls: {[fw.serial for fw in self.firewalls]}")
            logger.info(f"Available rule locations: {self.rule_locations}")
            
            return {
                'status': 'success',
                'device_groups': [dg.name for dg in self.device_groups],
                'firewalls': [fw.serial for fw in self.firewalls],
                'rule_locations': self.rule_locations
            }
            
        except Exception as e:
            logger.error(f"Error in discover_environment: {str(e)}", exc_info=True)
            return {'error': str(e)}


    # AddingRule.py - Update the create_rule method
    def create_rule(self, rule_data):
        """Create a security rule in Panorama with pre/post rulebase support"""
        try:
            # First validate all rule data
            valid, message = self.validate_rule_data(rule_data)
            if not valid:
                return {
                    'success': False,
                    'message': message,
                    'rule_type': rule_data.get('rule_type', 'pre')
                }
            
            # Ensure device groups are loaded before proceeding
            if not self.device_groups:
                logger.info("No device groups found, discovering environment...")
                discovery = self.discover_environment()
                if 'error' in discovery:
                    return {
                        'success': False,
                        'message': f"Failed to discover environment: {discovery['error']}",
                        'rule_type': rule_data.get('rule_type', 'pre')
                    }
            
            location = rule_data.get('location', 'shared')
            rule_type = rule_data.get('rule_type', 'pre').lower()
            logger.info(f"Creating {rule_type}-rule at location: {location}")
            
            # Handle location input - allow either selected path or manual entry
            if location.lower() == 'shared':
                device_groups = []
            else:
                # Split the path into device groups
                device_groups = [dg.strip() for dg in location.split('/') if dg.strip()]
                
                # Debug logging
                logger.info(f"Device groups from location: {device_groups}")
                logger.info(f"Available device groups: {[dg.name for dg in self.device_groups]}")
                
                # Validate device groups exist
                valid_dgs = [dg.name for dg in self.device_groups]
                for dg in device_groups:
                    if dg not in valid_dgs:
                        logger.error(f"Device group '{dg}' not found in available groups: {valid_dgs}")
                        return {
                            'success': False,
                            'message': f"Device group '{dg}' does not exist",
                            'rule_type': rule_type
                        }

            # Create the proper hierarchy
            if not device_groups:
                # Shared rulebase
                if rule_type == 'pre':
                    rulebase = PreRulebase()
                else:
                    rulebase = PostRulebase()
                self.panorama.add(rulebase)
            else:
                # Device group rulebase
                parent = self.panorama
                for dg_name in device_groups:
                    dg = DeviceGroup(dg_name)
                    parent.add(dg)
                    parent = dg
                
                if rule_type == 'pre':
                    rulebase = PreRulebase()
                else:
                    rulebase = PostRulebase()
                parent.add(rulebase)
            
            # Handle source IP field (can be IP or object name)
            source_ip = rule_data.get('sourceIP', 'any')
            if source_ip.lower() == 'any':
                source_ip = ['any']
            else:
                source_ip = [source_ip]
            
            # Handle destination IP field (can be IP or object name)
            destination_ip = rule_data.get('destinationIP', 'any')
            if destination_ip.lower() == 'any':
                destination_ip = ['any']
            else:
                destination_ip = [destination_ip]
            
            # Handle service field
            service = rule_data.get('destinationPort', 'any')
            if service.lower() in ['any', '']:
                service = ['any']
            else:
                service = [s.strip() for s in service.split(',')]
            
            # Handle application field properly
            application = rule_data.get('application', 'any')
            if application.lower() in ['any', '']:
                application = ['any']
            else:
                # Split by comma and strip whitespace for multiple applications
                application = [app.strip() for app in application.split(',')]
            
            # Handle zones
            source_zone = rule_data.get('sourceZone', 'any')
            if source_zone.lower() == 'any':
                source_zone = ['any']
            else:
                source_zone = [source_zone]
            
            destination_zone = rule_data.get('destinationZone', 'any')
            if destination_zone.lower() == 'any':
                destination_zone = ['any']
            else:
                destination_zone = [destination_zone]
            
            # Create the security rule object
            rule = SecurityRule(
                name=rule_data['name'],
                fromzone=source_zone,
                tozone=destination_zone,
                source=source_ip,
                destination=destination_ip,
                service=service,
                application=application,
                action=rule_data['action'],
                description=rule_data.get('description', ''),
                disabled=rule_data.get('disabled', False),
                log_start=rule_data.get('logStart', True),
                log_end=rule_data.get('logEnd', True),
                negate_source=rule_data.get('negateSource', False),
                negate_destination=rule_data.get('negateDestination', False)
            )
            
            # Add security profiles if specified
            security_profiles = rule_data.get('securityProfiles', {})
            if security_profiles:
                for profile_type, profile_name in security_profiles.items():
                    if profile_name and profile_name.lower() != 'none':
                        setattr(rule, profile_type, profile_name)
            
            rulebase.add(rule)
            
            # Create the rule in Panorama
            rule.create()
            
            # Commit the changes with proper XML formatting
            if not device_groups:
                commit_cmd = '<commit><shared-policy><admin><member>admin</member></admin></shared-policy></commit>'
            else:
                commit_cmd = f'<commit><shared-policy><device-group><entry name="{device_groups[-1]}"/></device-group></shared-policy></commit>'
            
            commit_url = f"https://{self.PANORAMA_IP}/api/?type=commit&action=partial&cmd={commit_cmd}&key={self.API_KEY}"
            response = requests.get(commit_url, verify=False)
            response.raise_for_status()
            
            # Verify the rule was actually created
            if not device_groups:
                xpath = f"/config/shared/{rule_type}-rulebase/security/rules/entry[@name='{rule_data['name']}']"
            else:
                xpath = f"/config/devices/entry[@name='localhost.localdomain']/device-group/entry[@name='{device_groups[-1]}']/{rule_type}-rulebase/security/rules/entry[@name='{rule_data['name']}']"
            
            verify_url = f"https://{self.PANORAMA_IP}/api/?type=config&action=get&xpath={xpath}&key={self.API_KEY}"
            verify_response = requests.get(verify_url, verify=False)
            
            if verify_response.status_code != 200 or '<entry name=' not in verify_response.text:
                raise Exception("Rule creation verification failed")
            
            return {
                'success': True,
                'message': f'{rule_type.capitalize()}-rule created and committed successfully',
                'rule_name': rule_data['name'],
                'location': location,
                'rule_type': rule_type,
                'response': response.text,
                'verify_response': verify_response.text
            }
            
        except requests.exceptions.RequestException as re:
            logger.error(f"API request failed: {str(re)}", exc_info=True)
            return {
                'success': False,
                'message': 'Failed to communicate with Panorama',
                'error_details': str(re),
                'rule_type': rule_type
            }
        except Exception as e:
            logger.error(f"Rule creation failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': 'Failed to create rule',
                'error_details': str(e),
                'rule_type': rule_type
            }


    def _build_hierarchy_tree(self, dg_parents):
        """Build a tree structure of device groups"""
        tree = {'name': 'shared', 'children': []}
        dg_nodes = {'shared': tree}
        
        # First pass - create all nodes
        for dg in dg_parents:
            if dg not in dg_nodes:
                dg_nodes[dg] = {'name': dg, 'children': []}
        
        # Second pass - build hierarchy
        for dg, parent in dg_parents.items():
            if parent not in dg_nodes:
                dg_nodes[parent] = {'name': parent, 'children': []}
            dg_nodes[parent]['children'].append(dg_nodes[dg])
        
        return tree

    def _get_hierarchy_path(self, dg, dg_parents):
        """Get the hierarchy path for a device group"""
        path = []
        current = dg
        while current and current != 'shared':
            path.append(current)
            current = dg_parents.get(current)
        path.reverse()
        return path

    def _convert_path_to_tree(self, path):
        """Convert a path to a tree structure"""
        if not path:
            return []
        
        root = {'name': path[0], 'children': []}
        current = root
        
        for item in path[1:]:
            node = {'name': item, 'children': []}
            current['children'].append(node)
            current = node
            
        return root

@csrf_exempt
def firewall_hierarchy_api(request):
    """API endpoint to get firewall hierarchy"""
    try:
        manager = RuleManager()
        result = manager.get_hierarchy()
        
        if 'error' in result:
            return JsonResponse({'error': result['error']}, status=500)
            
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in firewall_hierarchy_api: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_security_rule_api(request):
    """API endpoint to create security rules"""
    if request.method != "POST":
        return JsonResponse({
            'success': False,
            'error': 'Method not allowed'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        
        required_fields = [
            'name', 'sourceZone', 'sourceIP', 'destinationZone', 
            'destinationIP', 'destinationPort', 'application', 
            'action', 'location', 'rule_type'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        manager = RuleManager()
        result = manager.create_rule(data)

        if result['success']:
            return JsonResponse({
                'success': True,
                'message': result['message'],
                'rule_name': result['rule_name'],
                'rule_type': result.get('rule_type', 'pre'),
                'location': result.get('location', 'shared'),
                'api_response': result.get('response', ''),
                'verify_response': result.get('verify_response', '')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['message'],
                'details': result.get('error_details', ''),
                'rule_type': result.get('rule_type', 'pre'),
                'location': data.get('location', 'shared')
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Error in create_security_rule_api: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)
    

# Add this new endpoint to your views
@csrf_exempt
def list_service_objects_api(request):
    """API endpoint to list all service objects"""
    try:
        manager = RuleManager()
        
        # Initialize panorama connection
        panorama = Panorama(os.getenv('PANORAMA_IP'), api_key=os.getenv('API_KEY'))
        
        # Refresh service objects from panorama
        services = panorama.refresh_all(ServiceObject)
        
        # Format response
        service_list = []
        for service in services:
            service_list.append({
                'name': service.name,
                'protocol': service.protocol or 'any',
                'port': service.port or 'any',
                'description': service.description or '',
                'location': 'shared'  # Modify if you have device-group specific services
            })
        
        return JsonResponse({
            'status': 'success',
            'objects': service_list
        })
        
    except Exception as e:
        logger.error(f"Error in list_service_objects_api: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# Add this to your RuleManager class
# In AddingRule.py - Update the list_service_objects method
# In AddingRule.py - Update the list_service_objects method
def list_service_objects(self):
    """List all service objects from Panorama"""
    try:
        # Get both shared and device-group specific service objects
        all_services = []
        
        # Get shared services
        shared_services = self.panorama.refreshall(ServiceObject)
        for service in shared_services:
            # Handle different service object attributes
            protocol = getattr(service, 'protocol', 'any')
            port = 'any'
            
            if hasattr(service, 'port'):
                port = service.port or 'any'
            elif hasattr(service, 'destination_port'):
                port = service.destination_port or 'any'
            elif hasattr(service, 'port_value'):
                port = service.port_value or 'any'
            
            all_services.append({
                'name': service.name,
                'protocol': protocol,
                'port': port,
                'description': getattr(service, 'description', ''),
                'location': 'shared'
            })
        
        # Get device-group specific services
        for dg in self.device_groups:
            dg_services = dg.refreshall(ServiceObject)
            for service in dg_services:
                protocol = getattr(service, 'protocol', 'any')
                port = 'any'
                
                if hasattr(service, 'port'):
                    port = service.port or 'any'
                elif hasattr(service, 'destination_port'):
                    port = service.destination_port or 'any'
                elif hasattr(service, 'port_value'):
                    port = service.port_value or 'any'
                
                all_services.append({
                    'name': service.name,
                    'protocol': protocol,
                    'port': port,
                    'description': getattr(service, 'description', ''),
                    'location': dg.name
                })
        
        return {
            'status': 'success',
            'objects': all_services
        }
        
    except Exception as e:
        logger.error(f"Error listing service objects: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }