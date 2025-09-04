from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Compare_final.main import files
from Compare_final.pre import main
from Compare_final.update_db import update_db
from Compare_final.Addition import Addition
from Compare_final.Modified import main as Modified
import threading
import time
import zipfile
from io import BytesIO
import os
import sqlite3
import json
from Compare_final.firewall_tested import search_firewalls
import json
from Compare_final.Firewall_Fetch import main as Firewall_Fetch
from Compare_final.database_creation_interface import main as interface_creation
from Compare_final.database_creation_xml import main as xml_creation
from Compare_final.Firewall_Rule_Parse import main as detect_rule
from Compare_final.Negate_Rules import main as negate
from Compare_final.Firewall_input_Tested import search_firewalls as input_search_firewalls
import socket
import ipaddress 
import queue
import pandas as pd
import json
from Compare_final.objectcheckerpanorama import PanoramaObjectChecker
from Compare_final.ServiceObjectCheckerPanorama import PanoramaServiceObjectChecker
from Compare_final.AddressGroupCheckerPanorama import PanoramaAddressGroupChecker
from Compare_final.ServiceGroupCheckerPanorama import PanoramaServiceGroupChecker
from Compare_final.AddingRule import firewall_hierarchy_api,create_security_rule_api,RuleManager
# Add these to your existing views.py
import requests
import xml.etree.ElementTree as ET
import os
# views.py (only the relevant service group and service object views)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging

logger = logging.getLogger(__name__)


# views.py - Ensure list_applications view is correct
@csrf_exempt
def list_applications(request):
    if request.method == "GET":
        try:
            # Return the comprehensive list you provided
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
            
            logger.info(f"Returning {len(comprehensive_apps)} applications")
            return JsonResponse({
                'status': 'success',
                'applications': sorted(comprehensive_apps)
            })
            
        except Exception as e:
            logger.error(f"Error in list_applications: {str(e)}", exc_info=True)
            # Even on error, return the comprehensive list
            comprehensive_apps = [
                '1c-enterprise', '1und1-mail', '2ch', '2ch-base', '2ch-posting', '3pc', 
                # ... (include the entire list here)
                'any'
            ]
            return JsonResponse({
                'status': 'success',
                'applications': sorted(comprehensive_apps)
            })
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)
@csrf_exempt
def get_rule_hierarchy(request):
    if request.method == "GET":
        try:
            manager = RuleManager()
            result = manager.get_hierarchy()
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def create_security_rule(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            required_fields = ['name', 'sourceZone', 'sourceIP', 'destinationZone', 
                             'destinationIP', 'destinationPort', 'application', 'action', 'location']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)

            manager = RuleManager()
            result = manager.create_rule(data)

            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': result['message'],
                    'rule_name': result['rule_name']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'details': result.get('error_details', ''),
                    'panorama_response': result.get('panorama_response', '')
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error in create_security_rule view: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)

@csrf_exempt
def create_service_group(request):
    if request.method == "POST":
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON payload'
                }, status=400)

            # Debugging - log the incoming data
            logger.info(f"Incoming create_service_group data: {data}")

            # Validate required fields
            required_fields = ['name', 'members']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)

            # Convert tags to list if it's a string
            tags = data.get('tags', [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

            manager = PanoramaServiceGroupChecker()
            result = manager.create_service_group(
                name=data['name'],
                members=data['members'],
                device_group=data.get('deviceGroup', 'shared'),
                tags=tags
            )

            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': result['message'],
                    'group_name': result['group_name'],
                    'group_details': result.get('group_details', {})
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'details': result.get('error_details', ''),
                    'panorama_response': result.get('panorama_response', '')
                }, status=400)

        except Exception as e:
            logger.error(f"Error in create_service_group view: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)

@csrf_exempt
def list_service_groups(request):
    if request.method == "GET":
        try:
            manager = PanoramaServiceGroupChecker()
            result = manager.list_service_groups()
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def search_service_group(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            search_term = data.get('searchTerm')
            
            if not search_term:
                return JsonResponse({'error': 'Search term is required'}, status=400)
                
            manager = PanoramaServiceGroupChecker()
            result = manager.search_service_group(search_term)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def list_service_objects(request):
    if request.method == "GET":
        try:
            manager = PanoramaServiceGroupChecker()
            result = manager.list_service_objects()
            
            # Ensure the response includes protocol/port
            if 'objects' in result:
                for obj in result['objects']:
                    if 'protocol' not in obj:
                        obj['protocol'] = 'any'
                    if 'port' not in obj:
                        obj['port'] = 'any'
            
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def check_service_group_name(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            group_name = data.get('groupName')
            
            if not group_name:
                return JsonResponse({'error': 'Group name is required'}, status=400)
                
            manager = PanoramaServiceGroupChecker()
            result = manager.group_name_exists(group_name)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse({
                'exists': result['exists']
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def check_service(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            protocol = data.get('protocol')
            port = data.get('port')
            service_name = data.get('serviceName')
            
            if not service_name and (not protocol or not port):
                return JsonResponse({'error': 'Either serviceName or protocol/port are required'}, status=400)
                
            manager = PanoramaServiceObjectChecker()
            
            # Check by service name first
            if service_name:
                result = manager.service_name_exists(service_name)
                if result['exists']:
                    return JsonResponse({
                        'exists': True,
                        'objects': result['objects']  # Ensure this returns proper format
                    })
            
            # Additional check: try protocol/port combination from service_name
            if service_name and '/' in service_name:
                try:
                    proto, prt = service_name.split('/', 1)
                    result = manager.service_exists(proto, prt)
                    if result['exists']:
                        return JsonResponse({
                            'exists': True,
                            'objects': result['objects']
                        })
                except ValueError:
                    pass
                    
            # If still not found, check by provided protocol/port
            if protocol and port:
                result = manager.service_exists(protocol, port)
                if result['exists']:
                    return JsonResponse({
                        'exists': True,
                        'objects': result['objects']
                    })
            
            return JsonResponse({'exists': False})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def create_service(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            required_fields = ['objectName', 'protocol', 'port']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)

            manager = PanoramaServiceObjectChecker()
            result = manager.create_service(
                name=data['objectName'],
                protocol=data['protocol'],
                port=data['port'],
                description=data.get('description', ''),
                tags=data.get('tags', ''),
                device_group='shared'
            )

            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': result['message'],
                    'objectName': result['object_name'],
                    'objectDetails': result.get('object_details', {})
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'details': result.get('error_details', ''),
                    'panorama_response': result.get('panorama_response', '')
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error in create_service view: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)

# Add these view functions

@csrf_exempt
def list_address_groups(request):
    if request.method == "GET":
        try:
            manager = PanoramaAddressGroupChecker()
            result = manager.list_address_groups()
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def search_address_group(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            search_term = data.get('searchTerm')
            
            if not search_term:
                return JsonResponse({'error': 'Search term is required'}, status=400)
                
            manager = PanoramaAddressGroupChecker()
            result = manager.search_address_group(search_term)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def list_address_objects(request):
    if request.method == "GET":
        try:
            manager = PanoramaAddressGroupChecker()
            result = manager.list_address_objects()
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_address_group(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            required_fields = ['name', 'members']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)

            manager = PanoramaAddressGroupChecker()
            result = manager.create_address_group(
                name=data['name'],
                members=data['members'],
                description=data.get('description', ''),
                device_group='shared',
                group_type='static'
            )

            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': result['message'],
                    'group_name': result['group_name'],
                    'group_details': result.get('group_details', {})
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'details': result.get('error_details', ''),
                    'panorama_response': result.get('panorama_response', '')
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error in create_address_group view: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)

@csrf_exempt
def check_address_group_name(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            group_name = data.get('groupName')
            
            if not group_name:
                return JsonResponse({'error': 'Group name is required'}, status=400)
                
            manager = PanoramaAddressGroupChecker()
            result = manager.group_name_exists(group_name)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse({
                'exists': result['exists']
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Add these to your existing views.py


@csrf_exempt
def create_service(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            required_fields = ['objectName', 'protocol', 'port']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)

            manager = PanoramaServiceObjectChecker()
            result = manager.create_service(
                name=data['objectName'],
                protocol=data['protocol'],
                port=data['port'],
                description=data.get('description', ''),
                tags=data.get('tags', ''),
                device_group='shared'
            )

            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': result['message'],
                    'objectName': result['object_name'],
                    'objectDetails': result.get('object_details', {})
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'details': result.get('error_details', ''),
                    'panorama_response': result.get('panorama_response', '')
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error in create_service view: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)


@csrf_exempt
def check_object_name(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            object_name = data.get('objectName')
            
            if not object_name:
                return JsonResponse({'error': 'Object name is required'}, status=400)
                
            manager = PanoramaObjectChecker()
            result = manager.object_name_exists(object_name)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            return JsonResponse({
                'exists': result['exists']
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# views.py (updated object checker endpoints)
@csrf_exempt
def check_object(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            address = data.get('address')
            
            if not address:
                return JsonResponse({'error': 'Address is required'}, status=400)
                
            manager = PanoramaObjectChecker()
            result = manager.object_exists(address)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
                
            if result['exists']:
                return JsonResponse({
                    'exists': True,
                    'objects': [{
                        'objectName': obj['object_name'],
                        'objectDetails': obj['object_details']
                    } for obj in result['objects']]
                })
            else:
                return JsonResponse({
                    'exists': False
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_object(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            required_fields = ['objectName', 'value']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)

            manager = PanoramaObjectChecker()
            result = manager.create_object(
                name=data['objectName'],
                address=data['value'],
                obj_type=data.get('type', 'ip-netmask'),
                description=data.get('description', ''),
                shared=True,  # Always shared now
                disabled=False,  # Always enabled now
                device_group='shared'  # Always shared
            )

            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': result['message'],
                    'objectName': result['object_name'],
                    'objectDetails': result.get('object_details', {})
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['message'],
                    'details': result.get('error_details', ''),
                    'panorama_response': result.get('panorama_response', '')
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error in create_object view: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)


@csrf_exempt
def home(request):
    """Handles file uploads and invokes the file comparison function."""
    if request.method == "POST":
        files(
            request.FILES.get("file1"),
            request.FILES.get("file2"),
        )
        return JsonResponse({"message": "Files processed successfully."})
@csrf_exempt
def home_check(request):
    """Processes input files and returns a ZIP file as a response."""
    if request.method == "POST":
        try:
            print("hello")
            # info_file = request.FILES.get("file1").read().decode("utf-8")
            # clear_message_list = info_file.splitlines()
            ips=request.POST.get("ips")
            username=request.POST.get("username")
            password=request.POST.get("password")
            clear_message_list=[]

            for ip in ips.split(','):
                line=ip+","+username+","+password
                clear_message_list.append(line)
            for i in clear_message_list:
                print(i)
            output, error, log, name = main(
                clear_message_list,
                request.FILES.get("file2"),
            )

            if not (output or error or name):
                return JsonResponse({
                    "success": False,
                    "message": "No output generated. Please check your input files."
                }, status=400)

            outer_zip_buffer = BytesIO()
            all_outputs = []
            indi = []

            # Create device-specific zip files and collect all output files
            with zipfile.ZipFile(outer_zip_buffer, 'w') as outer_zip:
                for output_path, error_path, log_path, name in zip(output, error, log, name):
                    device_zip_buffer = BytesIO()
                    with zipfile.ZipFile(device_zip_buffer, 'w') as device_zip:
                        if output_path and os.path.exists(output_path):
                            with open(output_path, 'rb') as output_file:
                                file=output_file.read()
                                device_zip.writestr(os.path.basename(output_path), file)
                                all_outputs.append([os.path.basename(output_path), file])
                        if error_path and os.path.exists(error_path):
                            with open(error_path, 'rb') as error_file:
                                device_zip.writestr(os.path.basename(error_path), error_file.read())
                        if log_path and os.path.exists(log_path):
                            with open(log_path, 'rb') as log_file:
                                device_zip.writestr(os.path.basename(log_path), log_file.read())
                    indi.append([f"{name}_report.zip", device_zip_buffer.getvalue()])

            # Create a zip for all output files (all_devices_output.zip)
            all_devices_buffer = BytesIO()
            with zipfile.ZipFile(all_devices_buffer, 'w') as all_devices_zip:
                for i in all_outputs:
                    all_devices_zip.writestr(i[0], i[1])
            # Now, write all_devices_output.zip first to the outer zip
            outer_zip_buffer = BytesIO()
            with zipfile.ZipFile(outer_zip_buffer, 'w') as outer_zip:
                # Add all_devices_output.zip as the first entry
                outer_zip.writestr("all_devices_output.zip", all_devices_buffer.getvalue())

                # Add the individual device zip files
                for i in indi:
                    outer_zip.writestr(i[0], i[1])

            # Cleanup generated files (optional)
            for file_list in [output, error, log]:
                for file_path in file_list:
                    if os.path.exists(file_path):
                        os.remove(file_path)

            # Return the final zip file as a response
            response = HttpResponse(outer_zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="reports.zip"'
            return response

        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "message": str(e)}, status=500)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


@csrf_exempt
def firewall(request):
    memo=dict()
    print(request.method)
    if request.method == "POST":
        source_ip = request.POST.get('sourceIP')
        dest_ip = request.POST.get('destinationIP')
        protocol=request.POST.get("protocol")
        src_zone=request.POST.get("sourceZone")
        dest_zone=request.POST.get("destinationZone")
        port=request.POST.get("destinationPort")
        firewall_names=str(request.POST.get("firewallName"))
        app_defaults = pd.read_csv( r"Compare_final\applipedia_data_cleaned.csv"
        )
        print(src_zone,dest_zone)
    # Convert the app_defaults to a dictionary for faster access
        app_defaults_dict = app_defaults.set_index('Name').T.to_dict('list')
        print("firewall",str(firewall_names))
        if "," in port:
            port=port.split(",")
        application=request.POST.get("application") 
        action=request.POST.get("Action")
        if action is None:
            action="allow"
        if application is None:
            application="any"
        if (port is None or port=="" or port=="any") and application!="any":
            port=app_defaults_dict[application][-1]
            r=[]
            port=port[port.index("[")+1:port.index("]")]
            for p in port.split(","):
                p=p[1:]
                p=p[:len(p)-1]
                r.append(p)
            port=r
        if application=="any" and port=="":
            port="any"
        print(port)
        data=set()
        fire={}
        if firewall_names:
            print(firewall_names,"firewall")
            output=input_search_firewalls(source_ip,dest_ip,firewall_names)
            print(output)
            fire[firewall_names]={}
            fire[firewall_names]["src"]=output[0]
            fire[firewall_names]["dest"]=output[1]
        if firewall_names=="" or firewall_names is None:
            data=search_firewalls(source_ip,dest_ip)
            print(fire)
            print(data)
            res=[]
            d=set()
            if len(data)<=3:
                return JsonResponse({"data":["No Matching Firewalls found"]})
            if data[0]!="Not Found":
                for i in data[0]:
                    d.add(i)
                    fire[i]={"src":data[1],"dest":data[2]}
            if data[3]!="Not Found":
                for i in data[3]:
                    d.add(i)
                    fire[i]={"src":data[4],"dest":data[5]}
            data=d
        else:
            print("firewall_else",firewall_names) 
            data=set(firewall_names.split(','))
        print(fire)
        q = queue.Queue()
        threads = []
        all_rules=[]
        other_cases={}
        print("fire",fire)
        for item in data:
            if item in fire:
                print((fire[item]["src"]==src_zone,src_zone=="any"),fire[item]["src"],src_zone)
                if (fire[item]["src"]==src_zone or src_zone=="any") and (fire[item]["dest"]==dest_zone or dest_zone=="any"):
                    thread = threading.Thread(target=detect_rule, args=(item,source_ip, dest_ip, fire[item]["src"] or src_zone, fire[item]["dest"] or dest_zone, port, protocol,action,application,q))
                    threads.append(thread)
                    thread.start()
                else:
                    other_cases[item]=""
                    if fire[item]["src"]!=src_zone and src_zone!="any" and fire[item]["dest"]!=dest_zone and dest_zone!="any" and source_ip!="any" and dest_ip!="any":
                        other_cases[item]+=(" "*20+" Both "+dest_ip+" "+source_ip+" Doesn't belong to "+dest_zone+" and "+src_zone)
                    else:
                        if fire[item]["src"]!=src_zone and src_zone!="any" and source_ip!="any":
                            other_cases[item]="Given "+source_ip+" Doesn't belong to "+src_zone
                        if fire[item]["dest"]!=dest_zone and dest_zone!="any" and dest_ip!="any":
                            other_cases[item]+=(" "*20+" Given "+dest_ip+" Doesn't belong to "+dest_zone)
            else:
                    thread = threading.Thread(target=detect_rule, args=(item,source_ip, dest_ip, fire[item]["src"], fire[item]["dest"], port, protocol,action,application,q))
                    threads.append(thread)
                    thread.start()
        print(other_cases)
        for thread in threads:
            thread.join()

        res = []
        while not q.empty():
            res.append(q.get())
        final_res=[]
        visited=set()
        for i in range(len(res)):
            firewall = res[i][0]
            if res[i][1]!="No rule Found":
                inter_check=str(sorted(res[i][1],key=lambda x:x["index"]))
            else:
                inter_check=str(sorted(res[i][1]))
            if inter_check in visited:
                continue
            for j in range(i + 1, len(res)):
                if res[i][1]!="No rule Found":
                    inter_check1=str(sorted(res[i][1],key=lambda x:x["index"]))
                else:
                    inter_check1=str(sorted(res[i][1]))
                if inter_check==inter_check1:
                    firewall += " "
                    firewall += res[j][0]
            visited.add(inter_check)
            firewall=firewall.strip().split()
            f=""
            firewall=sorted(firewall)
            for fw in firewall:
                f=f+" "+fw
            firewall=f.strip()
            final_res.append([firewall, res[i][1],len(res[i][1])])  
            memo=dict()
            memo1=dict()
            if len(res[i])>3:
                memo=dict(res[i][2])
                all_rules.append(res[i][3])
            for key, value in memo.items():
                if isinstance(value, set):
                    memo[key] = list(value)
        for o in other_cases:
            final_res.append([o,other_cases[o]])
        return JsonResponse({"data":final_res or ["No firewalls Found"],"memo":memo,"all_rules":all_rules})
@csrf_exempt
def firewall_update(request):
    if request.method=="POST":
        try:
            Host=request.POST.get("Host")
            username=request.POST.get("Username")
            password=request.POST.get("Password")
            Interface,Routing=Firewall_Fetch(Host,username,password)
            xml_creation(Routing)
            interface_creation(Interface)
            response="Sucessfully Updated"
        except Exception as e:
            response=str(e)
        finally:
            return JsonResponse({"data":response})
        

@csrf_exempt
def fw_firewall(request):
    if request.method == "POST":
        source_ip = request.POST.get('sourceIP')
        dest_ip = request.POST.get('destinationIP')
        data=search_firewalls(source_ip,dest_ip)
        print(data)
        return JsonResponse({"data":data})
 
    # Fix: options is not defined, return empty list or appropriate value
    return JsonResponse({"devices": []})
@csrf_exempt
def zones(request):
    if request.method=="GET":
        try:
            DATABASE = r"subnets.db"
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            subnet_rows = cursor.fetchall()
        
            # Fetch interfaces and zones from the interfaces table
            cursor.execute("""
                SELECT firewall_name, name, zone
                FROM interfaces
                WHERE ip != 'N/A'
            """)
            subnet_rows = cursor.fetchall()
            zones=set()
            for firewall_name, name, zone in subnet_rows:
                zones.add(zone)
            zones.add("any")
            print(zones)
            return JsonResponse({"data":list(zones)})
        except Exception as e:
            print(e)
            # Fix: error is not defined, return error message
            return JsonResponse({"data": str(e)})
def resolve_fqdn_to_ip(request):
    if request.method=="POST":
        try:
            fqdn="Error"
            fqdn=request.POST.get("data")
            ip_addresses = socket.gethostbyname_ex(fqdn)[2]
            return JsonResponse({"data":ip_addresses[0]})
        except Exception as e:
            print(e)
            return JsonResponse({"data":fqdn})
def fetch_all_apps(request):
    if request.method=="GET":
        df=pd.read_csv(r"Compare_final\applipedia_data_cleaned.csv")
        return JsonResponse({"data": list(df["Name"])+["any"]})
@csrf_exempt
def Add(request):
    if request.method=="POST":
        data = json.loads(request.body)
        memo = data.get("memo")
        allrules = data.get("allrules")
        rules = data.get("rules")
        form = data.get("formData")
        pass_action="allow"
        if form["Action"]=="allow":
            pass_action="deny"
        res=[]
        for ind in range(len(rules)):
            src = form.get("sourceIP", "any")
            dest = form.get("destinationIP", "any")
            src_zone = form.get("sourceZone", "any")
            dest_zone = form.get("destinationZone", "any")
            Protocol = form.get("protocol", "any")
            application = form.get("application", "any")
            port = form.get("destinationPort", "any")
            negate_rules = negate(
                src,
                dest,
                src_zone,
                dest_zone,
                port,
                Protocol,
                pass_action,
                application,
                allrules[ind]
            )
            found_index = float("inf")
            for i in rules[ind][1]:
                found_index = min(found_index, i["index"])
            mini_index = float("inf")
            for i in negate_rules:
                mini_index = min(mini_index, i["index"])
            print(found_index, mini_index)
            if found_index < mini_index:
                res.append("Rule already Exists for " + str(ind))
                continue
            modified_rules = Modified(
                src,
                dest,
                src_zone,
                dest_zone,
                port,
                Protocol,
                pass_action,
                application,
                allrules[ind]
            )
            found_index = float("inf")
            for i in modified_rules:
                found_index = min(found_index, i["index"])
            print(found_index, mini_index)
            if found_index == float("inf"):
                res.append("New rule has to be added before " + str(mini_index))
                continue
            rule = modified_rules[found_index]
            if found_index < mini_index:
                res.append("Rule " + str(found_index) + " has to be modified")
                src_flag = False
                dest_flag = False
                dest_zone_flag = False
                src_zone_flag = False
                port_flag = False
                protocol_flag = False
                application_flag = False
                arr = ["source", "destination", "to", "from"]
                for i in arr:
                    if i not in rule:
                        return False, rule["name"], []
                for s in rule["source"]:
                    if src_flag:
                        continue
                    if s == "...":
                        continue
                    try:
                        if "-" in s:
                            start_ip, end_ip = s.split("-")
                            start_ip = ipaddress.ip_address(start_ip)
                            end_ip = ipaddress.ip_address(end_ip)
                            # Check if IP falls within the range
                            if src == "any" or ("/" not in src and start_ip <= ipaddress.ip_address(src) <= end_ip):
                                src_flag = True
                            else:
                                subnet = ipaddress.ip_network(src, strict=False)
                                # Check if IP falls within the subnet
                                if start_ip <= subnet.network_address <= end_ip and start_ip <= subnet.broadcast_address <= end_ip:
                                    src_flag = True
                    except Exception:
                        continue
                if 'negate-source' in rule and rule['negate-source'] and src != "any":
                    src_flag = not src_flag
                for d in rule["destination"]:
                    if dest_flag:
                        continue
                    if d == "...":
                        continue
                    try:
                        if "-" in d:
                            start_ip, end_ip = d.split("-")
                            start_ip = ipaddress.ip_address(start_ip)
                            end_ip = ipaddress.ip_address(end_ip)
                            # Check if IP falls within the range
                            if dest == "any" or start_ip <= ipaddress.ip_address(dest) <= end_ip:
                                dest_flag = True
                        else:
                            dest_flag = (
                                d == "any" or dest == "any" or
                                (
                                    ipaddress.ip_network(d, strict=False).version == ipaddress.ip_network(dest, strict=False).version and
                                    (
                                        ipaddress.ip_network(d, strict=False).supernet_of(ipaddress.ip_network(dest, strict=False)) or
                                        ipaddress.ip_network(dest, strict=False).subnet_of(ipaddress.ip_network(d, strict=False))
                                    )
                                )
                            )
                    except Exception:
                        continue
                if 'negate-destination' in rule and rule['negate-destination'] == "yes" and dest != "any":
                    dest_flag = not dest_flag
                for s in rule["from"]:
                    if src_zone_flag:
                        continue
                    if s.lower() == src_zone.lower() or s.lower() == "any" or src_zone.lower() == "any":
                        src_zone_flag = s
                for d in rule["to"]:
                    if dest_zone_flag:
                        continue
                    if d.lower() == dest_zone.lower() or d.lower() == "any" or dest_zone.lower() == "any":
                        dest_zone_flag = d
                for entry in rule["entries"]:
                    try:
                        if isinstance(port, list):
                            p = port
                            for port_item in p:
                                if "-" in port_item:
                                    s1, e1 = port_item.split("-")
                                    s1 = int(s1)
                                    e1 = int(e1)
                                    if "-" in entry["destination_port"]:
                                        start_port, end_port = entry["destination_port"].split("-")
                                        start_port = int(start_port)
                                        end_port = int(end_port)
                                        if s1 >= start_port and e1 <= end_port:
                                            if (
                                                entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                            ) and (
                                                entry["application"] == "any" or application == "any" or entry["application"] == application
                                            ):
                                                protocol_flag = entry["protocol"]
                                                port_flag = entry["destination_port"]
                                                application_flag = entry["application"]
                                    else:
                                        if (
                                            entry["destination_port"] == "any" or port_item == "any" or entry["destination_port"] == port_item or s1 <= int(entry["destination_port"]) <= e1
                                        ) and (
                                            entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                        ) and (
                                            entry["application"] == "any" or application == "any" or entry["application"] == application
                                        ):
                                            port_flag = entry["destination_port"]
                                            protocol_flag = entry["protocol"]
                                            application_flag = entry["application"]
                                if "-" in entry["destination_port"] and entry["destination_port"] != "app-default" and port_item != "any":
                                    start_port, end_port = entry["destination_port"].split("-")
                                    start_port = int(start_port)
                                    end_port = int(end_port)
                                    check_port = int(port_item)
                                    if start_port <= check_port <= end_port:
                                        if (
                                            entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                        ) and (
                                            entry["application"] == "any" or application == "any" or entry["application"] == application
                                        ):
                                            protocol_flag = entry["protocol"]
                                            port_flag = entry["destination_port"]
                                            application_flag = entry["application"]
                                else:
                                    if port_flag:
                                        continue
                                    if (
                                        entry["destination_port"] == "any" or port_item == "any" or entry["destination_port"] == port_item
                                    ) and (
                                        entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                    ) and (
                                        entry["application"] == "any" or application == "any" or entry["application"] == application
                                    ):
                                        port_flag = entry["destination_port"]
                                        protocol_flag = entry["protocol"]
                                        application_flag = entry["application"]
                        else:
                            if not isinstance(port, list) and "-" in port:
                                s1, e1 = port.split("-")
                                s1 = int(s1)
                                e1 = int(e1)
                                if "-" in entry["destination_port"]:
                                    start_port, end_port = entry["destination_port"].split("-")
                                    start_port = int(start_port)
                                    end_port = int(end_port)
                                    if s1 >= start_port and e1 <= end_port:
                                        if (
                                            entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                        ) and (
                                            entry["application"] == "any" or application == "any" or entry["application"] == application
                                        ):
                                            protocol_flag = entry["protocol"]
                                            port_flag = entry["destination_port"]
                                            application_flag = entry["application"]
                                else:
                                    if (
                                        entry["destination_port"] == "any" or port == "any" or entry["destination_port"] == port or s1 <= int(entry["destination_port"]) <= e1
                                    ) and (
                                        entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                    ) and (
                                        entry["application"] == "any" or application == "any" or entry["application"] == application
                                    ):
                                        port_flag = entry["destination_port"]
                                        protocol_flag = entry["protocol"]
                                        application_flag = entry["application"]
                            else:
                                if "-" in entry["destination_port"] and entry["destination_port"] != "app-default" and port != "any":
                                    start_port, end_port = entry["destination_port"].split("-")
                                    start_port = int(start_port)
                                    end_port = int(end_port)
                                    check_port = int(port)
                                    if start_port <= check_port <= end_port:
                                        if (
                                            entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                        ) and (
                                            entry["application"] == "any" or application == "any" or entry["application"] == application
                                        ):
                                            protocol_flag = entry["protocol"]
                                            port_flag = entry["destination_port"]
                                            application_flag = entry["application"]
                                else:
                                    if port_flag:
                                        continue
                                    if (
                                        entry["destination_port"] == "any" or port == "any" or entry["destination_port"] == port
                                    ) and (
                                        entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol
                                    ) and (
                                        entry["application"] == "any" or application == "any" or entry["application"] == application
                                    ):
                                        port_flag = entry["destination_port"]
                                        protocol_flag = entry["protocol"]
                                        application_flag = entry["application"]
                    except Exception:
                        print(f"Invalid port: {entry}", " Error")
                if src_flag is False:
                    res.append("Source IP has to be modified")
                if dest_flag is False:
                    res.append("Destination IP has to be modified")
                if src_zone_flag is False:
                    res.append("Source Zone has to be modified")
                if dest_zone_flag is False:
                    res.append("Destination Zone has to be modified")
                if application_flag:
                    res.append("Application flag has to be modified")
                if port_flag:
                    res.append("Port has to be modified")
                res[-1] = res[-1] + " " + str(ind)
        print(res)
        return JsonResponse({})
@csrf_exempt
def App(request):
    if request.method=="GET":
        app_defaults = pd.read_csv( r"Compare_final\applipedia_data_cleaned.csv"
        )
    # Convert the app_defaults to a dictionary for faster access
        app_defaults_dict = app_defaults.set_index('Name').T.to_dict('list')
        print(list(app_defaults["Name"]))
        return JsonResponse({"data": list(set(app_defaults["Name"]))})
@csrf_exempt
def Firewall_names(request):
    if request.method=="GET":
        try:
            DATABASE = r"subnets.db"
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            subnet_rows = cursor.fetchall()
        
            # Fetch interfaces and zones from the interfaces table
            cursor.execute("""
                SELECT firewall_name, name, zone
                FROM interfaces
                WHERE ip != 'N/A'
            """)
            subnet_rows = cursor.fetchall()
            firewalls=set()
            for firewall_name, name, zone in subnet_rows:
                firewalls.add(firewall_name)
            print(firewalls)
            return JsonResponse({"data":list(firewalls)})
        except Exception as e:
            print(e)
            # Fix: error is not defined, return error message
            return JsonResponse({"data": str(e)})