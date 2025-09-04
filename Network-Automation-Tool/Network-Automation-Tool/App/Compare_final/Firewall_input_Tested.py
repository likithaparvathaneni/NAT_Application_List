import socket
import ipaddress
import sqlite3
import os
DATABASE = r"subnets.db"
def resolve_fqdn_to_ip(fqdn):
    try:
        ip_addresses = socket.gethostbyname_ex(fqdn)[2]
        return ip_addresses[0]
    except socket.gaierror as e:
        print(f"Error resolving FQDN {fqdn}: {e}")
        return fqdn
def find_firewall_and_zone_details1(ip, is_source):
    """
    Finds the firewall name, subnet, and zones (source and destination) for the given IP.
    Handles RFC1918 IPs and CIDR notation.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
 
    # Fetch subnets and next hops from the subnets table
 
    cursor.execute("""
        SELECT firewall_name,destination,interface,flags
        FROM subnets;
    """)
 
    subnet_rows = cursor.fetchall()
 
    # Fetch interfaces and zones from the interfaces table
    cursor.execute("""
        SELECT firewall_name, name, zone
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
    zone=None
    ip = ipaddress.ip_address(ip)
    longest_prefix = -1
    for firewall_name, subnet, name,flags in subnet_rows:
        if flags.strip()=="uh":
            continue
        try:
            zone=None
            # Handle CIDR or single IP notation
            if subnet=="0.0.0.0/0":
                continue
            network = ipaddress.ip_network(subnet, strict=False)
 
            if ip in network:
                prefix_length = network.prefixlen
                longest_prefix=max(longest_prefix,prefix_length)
                for int_firewall_name, interface, int_zone in interface_rows:
                    if int_firewall_name == firewall_name and name.strip()==interface.strip():
                        zone=int_zone
                   
                    matched_firewalls.add((firewall_name,subnet,zone))
 
 
        except :
            continue
    matched_firewalls=set()
    for firewall_name, subnet, name,flags in subnet_rows:
        try:
            zone=None
            # Handle CIDR or single IP notation
            if subnet=="0.0.0.0/0":
                continue
            network = ipaddress.ip_network(subnet, strict=False)
 
            if ip in network:
                prefix_length = network.prefixlen
                if longest_prefix!=prefix_length:
                    continue
                for int_firewall_name, interface, int_zone in interface_rows:
                    if int_firewall_name == firewall_name and interface==name:
                        zone=int_zone
                matched_firewalls.add(firewall_name)
       
 
        except :
            continue
    # print(matched_firewalls)
   
    return list(matched_firewalls)
def find_subnet(ip):
    """
    Finds the firewall name, subnet, and zones (source and destination) for the given IP.
    Handles RFC1918 IPs and CIDR notation.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch subnets and next hops from the subnets table
    cursor.execute("""
        SELECT firewall_name, destination, nexthop,flags
        FROM subnets
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
    best_match = None
    best_subnet = None
    source_zone = None
    destination_zone = None
    longest_prefix = -1

    ip = ipaddress.ip_address(ip)  # Convert IP string to an IPv4Address object

    # Iterate through each subnet to find the best match
    for firewall_name, subnet, nexthop,flags in subnet_rows:
        if flags=="uh":
            continue
        if subnet=="0.0.0.0/0":
            continue
        try:
            # Handle CIDR or single IP notation
            network = ipaddress.ip_network(subnet, strict=False)

            if ip in network:
                prefix_length = network.prefixlen

                # Prefer the longest prefix match
                if prefix_length > longest_prefix:
                    best_match = firewall_name
                    best_subnet = subnet
        except ValueError:
            continue

    return best_subnet

def find_zone(ip, firewall):
    print(ip,firewall)
    print(firewall)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch subnets and next hops from the subnets table
    cursor.execute("""
        SELECT firewall_name, destination,interface
        FROM subnets
    """)
    subnet_rows = cursor.fetchall()

    # Fetch interfaces and zones from the interfaces table
    cursor.execute("""
        SELECT firewall_name,name, ip, zone
        FROM interfaces
        WHERE ip != 'N/A'
    """)
    interface_rows = cursor.fetchall()
    matched_zone=None
    for firewall_name,destination,interface in subnet_rows:
        if firewall_name==firewall and ip==destination:
            for firewall_name,name,ip1,zone in interface_rows:
                if firewall_name==firewall and name==interface:
                    matched_zone=zone 
    if matched_zone is None:
        for firewall_name,destination,interface in subnet_rows:
            if firewall_name==firewall and (ip==destination or destination=="0.0.0.0/0"):
                print(firewall_name,destination)
                for firewall_name,name,ip1,zone in interface_rows:
                    if firewall_name==firewall and name==interface:
                        print(zone)
                        matched_zone=zone 
    return matched_zone
def search_firewalls(source_ip_input,destination_ip_input,firewall):
    try:
        print(source_ip_input,destination_ip_input)
        # Validate IP inputs
        if '/' in source_ip_input:
            source_ip = ipaddress.ip_network(source_ip_input, strict=False).network_address
        else:
            if source_ip_input!="any":
                source_ip = ipaddress.ip_address(source_ip_input)
            else:
                source_ip=ipaddress.ip_network("0.0.0.0/0", strict=False).network_address

        if '/' in destination_ip_input:
            destination_ip = ipaddress.ip_network(destination_ip_input, strict=False).network_address
        else:
            if destination_ip_input!="any":
                destination_ip = ipaddress.ip_address(destination_ip_input)
            else:
                destination_ip=ipaddress.ip_network("0.0.0.0/0", strict=False).network_address
        src_subnet = "0.0.0.0"
        dst_subnet = "0.0.0.0"
        # Fetch details for Source and Destination IPs
        if  source_ip_input!="any":
            src_subnet=find_subnet(source_ip)
            src_firewall=find_firewall_and_zone_details1(source_ip,is_source=True) 
            src_firewall=sorted(src_firewall)
            if src_firewall:
                src_source_zone=find_zone(src_subnet,src_firewall[0])
                dst_subnet= find_subnet(destination_ip)
                src_destination_zone = find_zone(dst_subnet, src_firewall[0]) 
            else:
                src_source_zone=None
                dst_subnet= None
                src_destination_zone = None 
        else:
            src_subnet = "0.0.0.0/0"
            

        if destination_ip_input!="any":
            dst_subnet= find_subnet(destination_ip)
            dst_firewall=find_firewall_and_zone_details1(destination_ip,is_source=True)
            dst_firewall=sorted(dst_firewall)
            if dst_firewall:
                dst_destination_zone=find_zone(dst_subnet,dst_firewall[0])
                dst_source_zone = find_zone(src_subnet,dst_firewall[0])
            else:
                dst_destination_zone=None
                dst_source_zone = None
        else:
            dst_subnet = "0.0.0.0/0"

        return [find_zone(src_subnet,firewall),find_zone(src_subnet,firewall)]

    except Exception as e:
        print(e)
        return ["Error"]