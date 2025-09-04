from netaddr import IPRange, IPNetwork
 
def is_subnet_in_range(ip_range, subnet):
    """
    Checks if a given subnet is completely contained within an IP range.
 
    :param ip_range: IP range in the format "start_ip-end_ip" (e.g., "65.52.0.0-65.55.255.255")
    :param subnet: Subnet in CIDR notation (e.g., "65.52.0.0/16")
    :return: True if the subnet is fully inside the IP range, False otherwise.
    """
    try:
        # Convert the range into an IPRange object
        start_ip, end_ip = ip_range.split('-')
        ip_range_obj = IPRange(start_ip, end_ip)
 
        # Convert the subnet into an IPNetwork object
        subnet_obj = IPNetwork(subnet)
 
        # Check if ALL subnet IPs are within the range
        return subnet_obj.first in ip_range_obj and subnet_obj.last in ip_range_obj
 
    except ValueError:
        return False  # Invalid input format
 
#  Example Usage
print(is_subnet_in_range("65.52.0.0-65.55.255.255", "65.52.0.0/16"))  # True
print(is_subnet_in_range("65.52.0.0-65.55.255.255", "65.56.0.0/16"))  # False
print(is_subnet_in_range("13.64.0.0-13.107.255.255", "13.66.0.0/18")) # True