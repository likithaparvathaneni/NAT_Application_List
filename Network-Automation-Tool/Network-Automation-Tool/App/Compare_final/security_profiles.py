import os
import logging
from django.http import JsonResponse
from panos.panorama import Panorama
from panos import policies, network, firewall, device, ha, objects
import json

logger = logging.getLogger(__name__)

class SecurityProfileManager:
    def __init__(self):
        self.PANORAMA_IP = os.getenv('PANORAMA_IP', '10.1.3.6')
        self.API_KEY = os.getenv('API_KEY', 'LUFRPT16Z3QvYVpZK052NVloQ3FLV1lUd1M5dWMrUEk9SENZbzFwbWNDZm4xdDVYRHpYZko0UnROSFRqT3lySXR3QXU2YW1lYXE1aEcvMHNScFVyL1pabmVIclpRRFM5Rw==')
        self.panorama = Panorama(self.PANORAMA_IP, api_key=self.API_KEY)

    def get_all_security_profiles(self):
        try:
            # Try to get all profile types using the API directly
            profile_types = [
                ('antivirus', 'antivirus'),
                ('antiSpyware', 'anti-spyware'),
                ('vulnerability', 'vulnerability'),
                ('urlFiltering', 'url-filtering'),
                ('fileBlocking', 'file-blocking'),
                ('wildfire', 'wildfire-analysis'),
                ('dataFiltering', 'data-filtering'),
                ('profileGroup', 'profile-group')
            ]
            
            profiles = {}
            
            for profile_name, xpath_name in profile_types:
                try:
                    xpath = f"/config/shared/{xpath_name}"
                    response = self.panorama.xapi.get(xpath)
                    
                    profile_entries = response.findall(f".//entry")
                    profiles[profile_name] = [
                        {'name': entry.get('name'), 'description': ''} 
                        for entry in profile_entries
                    ]
                except Exception as e:
                    logger.warning(f"Failed to load {profile_name} profiles: {str(e)}")
                    profiles[profile_name] = []
            
            return {
                'status': 'success',
                'profiles': profiles
            }
            
        except Exception as e:
            logger.error(f"Error getting security profiles: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

def list_security_profiles_api(request):
    """API endpoint to list all security profiles"""
    try:
        manager = SecurityProfileManager()
        result = manager.get_all_security_profiles()
        
        if result['status'] == 'error':
            return JsonResponse({'error': result['message']}, status=500)
            
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Error in list_security_profiles_api: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)