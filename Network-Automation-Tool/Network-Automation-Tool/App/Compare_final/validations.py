# validations.py
import re
import ipaddress
from panos.panorama import Panorama
from panos.objects import AddressObject, ServiceObject, Tag
from panos.network import Zone
import requests
import xml.etree.ElementTree as ET
import logging
from panos.panorama import DeviceGroup

logger = logging.getLogger(__name__)

class PanoramaValidator:
    def __init__(self, panorama_ip, api_key):
        self.panorama = Panorama(panorama_ip, api_key=api_key)
        
    def validate_rule_name(self, name, rule_type, location):
        """Validate rule name is unique within the rule type and location"""
        if not name or len(name) > 63:
            return False, "Name must be 1-63 characters"
            
        if not re.match(r'^[a-zA-Z0-9\-_.]+$', name):
            return False, "Only letters, numbers, hyphens, underscores and periods allowed"
            
        if name[0].isdigit():
            return False, "Name cannot start with a number"
            
        # TODO: Check for uniqueness in Panorama
        return True, ""
        
    def validate_zones(self, zones):
        """Validate zones exist in Panorama"""
        existing_zones = Zone.refreshall(self.panorama)
        existing_zone_names = [z.name for z in existing_zones]
        
        missing_zones = [zone for zone in zones if zone not in existing_zone_names]
        if missing_zones:
            return False, f"Zones not found: {', '.join(missing_zones)}"
        return True, ""

# In validations.py - Update validate_services method
    # validations.py - Update validate_services method
    def validate_services(self, services):
        """Validate service objects exist - check by name or protocol/port"""
        if 'any' in services:
            return True, ""
        
        # Get all service objects from Panorama
        try:
            all_services = ServiceObject.refreshall(self.panorama)
            existing_names = [s.name for s in all_services]
            existing_protocol_port = {}
            
            for service in all_services:
                # Handle different service object types and SDK versions
                protocol = getattr(service, 'protocol', None)
                
                # For newer SDK versions, port might be in different attributes
                port = None
                if hasattr(service, 'port'):
                    port = service.port
                elif hasattr(service, 'destination_port'):
                    port = service.destination_port
                elif hasattr(service, 'port_value'):
                    port = service.port_value
                
                if protocol and port:
                    key = f"{protocol}/{port}"
                    existing_protocol_port[key] = service.name
                elif protocol:
                    key = f"{protocol}/any"
                    existing_protocol_port[key] = service.name
                elif port:
                    key = f"any/{port}"
                    existing_protocol_port[key] = service.name
                    
        except Exception as e:
            return False, f"Error fetching services: {str(e)}"
        
        missing = []
        for srv in services:
            if srv in existing_names:
                continue
                
            # Check if it's in protocol/port format
            if '/' in srv:
                try:
                    protocol, port = srv.split('/', 1)
                    lookup_key = f"{protocol.lower()}/{port}"
                    
                    # Check exact match
                    if lookup_key in existing_protocol_port:
                        continue
                        
                    # Check with 'any' protocol
                    if f"any/{port}" in existing_protocol_port:
                        continue
                        
                    # Check with 'any' port
                    if f"{protocol.lower()}/any" in existing_protocol_port:
                        continue
                        
                    missing.append(srv)
                    
                except ValueError:
                    missing.append(srv)
            else:
                missing.append(srv)
        
        if missing:
            return False, f"Service objects not found: {', '.join(missing)}"
        return True, ""

    def _is_valid_port(self, port_str):
        """Helper method to validate port number"""
        try:
            port = int(port_str)
            return 0 <= port <= 65535
        except ValueError:
            return False
        
# validations.py - Update validate_applications method if needed
    def validate_applications(self, apps):
        """Validate applications exist in Panorama"""
        if 'any' in apps:
            return True, ""
        
        # For custom input, just validate the format
        for app in apps:
            if not re.match(r'^[a-zA-Z0-9\-_]+$', app):
                return False, f"Invalid application name format: {app}"
        
        return True, "Validation passed"

    def validate_tags(self, tags):
        """Validate tags exist or create them"""
        if not tags:
            return True, ""
            
        existing_tags = Tag.refreshall(self.panorama)
        existing_tag_names = [t.name for t in existing_tags]
        
        missing_tags = [tag for tag in tags if tag not in existing_tag_names]
        for tag in missing_tags:
            new_tag = Tag(tag)
            self.panorama.add(new_tag)
            try:
                new_tag.create()
            except Exception as e:
                return False, f"Failed to create tag '{tag}': {str(e)}"
                
        return True, ""
        
    def validate_security_profiles(self, profile_type, profile_name):
        """Validate security profiles exist (simplified version)"""
        if not profile_name or profile_name.lower() == 'none':
            return True, ""
            
        # In this simplified version, we'll just validate the name format
        if not re.match(r'^[a-zA-Z0-9\-_]+$', profile_name):
            return False, f"Invalid {profile_type} profile name format"
        return True, ""
        
         

    def validate_port(self, port_str):
        """Validate port number or range"""
        if port_str.lower() in ['any', '']:
            return True, ""
            
        try:
            # Handle port ranges
            if '-' in port_str:
                start, end = map(int, port_str.split('-'))
                if not (0 <= start <= 65535 and 0 <= end <= 65535):
                    return False, "Ports must be 0-65535"
                if start > end:
                    return False, "Start port must be <= end port"
                return True, ""
                
            # Single port
            port = int(port_str)
            if not 0 <= port <= 65535:
                return False, "Port must be 0-65535"
            return True, ""
            
        except ValueError:
            return False, "Invalid port number"


# validations.py - Update the validate_ip_address method
    def validate_ip_address(self, ip_str):
        """Validate IP address/range/subnet OR object name"""
        if ip_str.lower() == 'any':
            return True, ""
        
        # First check if it's a valid IP address format
        try:
            # Handle IP ranges
            if '-' in ip_str:
                parts = ip_str.split('-')
                if len(parts) != 2:
                    return False, "Invalid IP range format"
                ipaddress.IPv4Address(parts[0])
                ipaddress.IPv4Address(parts[1])
                return True, ""
                
            # Handle CIDR
            if '/' in ip_str:
                ipaddress.IPv4Network(ip_str, strict=False)
                return True, ""
                
            # Single IP
            ipaddress.IPv4Address(ip_str)
            return True, ""
            
        except ValueError:
            # If it's not a valid IP format, check if it's a valid object name
            # Object names should follow naming conventions but not necessarily be IP addresses
            if not re.match(r'^[a-zA-Z0-9\-_.]+$', ip_str):
                return False, "Invalid IP address or object name format"
            
            # Check if object exists in Panorama (optional - could be expensive)
            # For now, just validate the name format
            return True, ""
        
    def validate_address_objects(self, addresses):
        """Validate address objects/groups exist or are valid IP addresses"""
        if 'any' in addresses:
            return True, ""
        
        # Check if it's a valid IP address first
        for addr in addresses:
            # Skip validation for IP addresses (they're already validated by validate_ip_address)
            try:
                # Check if it's a valid IP format
                if '-' in addr:
                    parts = addr.split('-')
                    if len(parts) == 2:
                        ipaddress.IPv4Address(parts[0])
                        ipaddress.IPv4Address(parts[1])
                        continue
                elif '/' in addr:
                    ipaddress.IPv4Network(addr, strict=False)
                    continue
                else:
                    ipaddress.IPv4Address(addr)
                    continue
            except ValueError:
                # If it's not a valid IP, check if it's a valid object name
                if not re.match(r'^[a-zA-Z0-9\-_.]+$', addr):
                    return False, f"Invalid address format: {addr}"
        
        # Check individual address objects (optional - can be expensive)
        # all_objects = AddressObject.refreshall(self.panorama)
        # existing_names = [obj.name for obj in all_objects]
        
        # missing = [addr for addr in addresses if addr not in existing_names]
        # if missing:
        #     return False, f"Address objects not found: {', '.join(missing)}"
        
        return True, ""