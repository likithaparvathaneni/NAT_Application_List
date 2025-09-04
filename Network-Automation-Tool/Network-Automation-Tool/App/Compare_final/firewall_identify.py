import socket
import ipaddress
import sqlite3
DATABASE = r"subnets_latest.db"
def resolve_fqdn_to_ip(fqdn):
    try:
        ip_addresses = socket.gethostbyname_ex(fqdn)[2]
        return ip_addresses[0]
    except socket.gaierror as e:
        print(f"Error resolving FQDN {fqdn}: {e}")
        return fqdn
def find_firewall_and_zone_details(ip, is_source):
    """
    Finds the firewall name, subnet, and zones (source and destination) for the given IP.
    Handles RFC1918 IPs and CIDR notation.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
 
    # Fetch subnets and next hops from the subnets table
    cursor.execute("""
        SELECT firewall_name, destination, nexthop
        FROM subnets;
    """)
    subnet_rows = cursor.fetchall()
 
    # Fetch interfaces and zones from the interfaces table
    cursor.execute("""
        SELECT firewall_name, ip, zone
        FROM interfaces
        WHERE ip != 'N/A'
    """)
    interface_rows = cursor.fetchall()
 
    conn.close()
 
    print(f"Processing {'Source' if is_source else 'Destination'} IP: {ip}")
 
    matched_firewalls=set()
 
    ip = ipaddress.ip_address(ip)  # Convert IP string to an IPv4Address object
    best_match = None
    best_subnet = None
    source_zone = None
    destination_zone = None
    longest_prefix = -1
 
    ip = ipaddress.ip_address(ip)  # Convert IP string to an IPv4Address object
 
    # # Iterate through each subnet to find the best match
    for firewall_name, subnet, nexthop in subnet_rows:
        try:
            try:
                if ip.supernet_of(subnet):
                    continue
            finally:
 
                # Handle CIDR or single IP notation
                network = ipaddress.ip_network(subnet, strict=False)
                if subnet=="0.0.0.0/0":
                    continue
 
                if ip in network:
                    prefix_length = network.prefixlen
 
                    # Prefer the longest prefix match
                    if prefix_length > longest_prefix:
                        best_match = firewall_name
                        best_subnet = subnet
                        source_zone = None
                        destination_zone = None
                        if ip == network.network_address:
                            print(f"{ip} is the first IP (network address) of subnet {subnet}.")
                        elif ip == network.broadcast_address:
                            print(f"{ip} is the last IP (broadcast address) of subnet {subnet}.")
                       
                        # If nexthop is 0.0.0.0, match IP with interfaces table instead
                        if nexthop == "0.0.0.0":
                            for int_firewall_name, int_ip, int_zone in interface_rows:
                                try:
                                    if int_firewall_name == firewall_name and ipaddress.ip_address(int_ip) == ip:
                                        if is_source:
                                            destination_zone = int_zone
                                            print(f"Destination zone based on interface IP match: {destination_zone}")
                                        else:
                                            source_zone = int_zone
                                            print(f"Source zone based on interface IP match: {source_zone}")
                                except ValueError:
                                    continue
                        else:
                            # Find the corresponding zone using the nexthop IP if not 0.0.0.0
                            for int_firewall_name, int_ip, int_zone in interface_rows:
                                try:
                                    if int_firewall_name == firewall_name:
                                        interface_network = ipaddress.ip_network(int_ip, strict=False)
 
                                        if nexthop:  # Check if next-hop is in the interface's network
                                            nexthop_ip = ipaddress.ip_address(nexthop)
                                            if nexthop_ip in interface_network:
                                                if is_source:
                                                    destination_zone = int_zone
                                                    print(f"Destination zone based on nexthop {nexthop_ip}: {destination_zone}")
                                                else:
                                                    source_zone = int_zone
                                                    print(f"Source zone based on nexthop {nexthop_ip}: {source_zone}")
                                except ValueError:
                                    continue
 
                        longest_prefix = prefix_length
        except Exception as E:
            continue
    print(best_match,best_subnet)
    if best_match:
        return [[best_match,best_subnet,source_zone or destination_zone]]
    # # Iterate through each subnet to find the best match
    for firewall_name, subnet, nexthop in subnet_rows:
        try:
            # Handle CIDR or single IP notation
            if subnet=="0.0.0.0/0":
                continue
            network = ipaddress.ip_network(subnet, strict=False)
 
            if ip in network:
                matched_firewalls.add((firewall_name,subnet))
        except ValueError:
            continue
    # print(matched_firewalls)
    return matched_firewalls
 
def search_firewalls(source_ip_input,destination_ip_input):
    print(source_ip_input,destination_ip_input)
    try:
        # Validate IP inputs
        source_ip_input=resolve_fqdn_to_ip(source_ip_input)
        destination_ip_input=resolve_fqdn_to_ip(destination_ip_input)
        if '/' in source_ip_input:
            source_ip = ipaddress.ip_network(source_ip_input, strict=False).network_address
        else:
            source_ip = ipaddress.ip_address(source_ip_input)
 
        if '/' in destination_ip_input:
            destination_ip = ipaddress.ip_network(destination_ip_input, strict=False).network_address
        else:
            destination_ip = ipaddress.ip_address(destination_ip_input)
 
        # Fetch details for Source and Destination IPs
        src_firewall = find_firewall_and_zone_details(source_ip, is_source=True)
           
        dst_firewall= find_firewall_and_zone_details(destination_ip, is_source=True)
        # print(src_firewall,dst_firewall)
        return list(src_firewall),list(dst_firewall)
    except Exception as e:
        return e