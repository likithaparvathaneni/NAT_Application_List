from netmiko import ConnectHandler
import ipaddress
import socket
import pandas as pd
def resolve_fqdn_to_ip(fqdn):
    try:
        ip_addresses = socket.gethostbyname_ex(fqdn)[2]
        return ip_addresses[0]
    except socket.gaierror as e:
        print(f"Error resolving FQDN {fqdn}: {e}")
        return fqdn
fqdn = "cghub.providence.org"
ip_addresses = resolve_fqdn_to_ip(fqdn)
print(f"IP addresses for FQDN {fqdn}: {ip_addresses}")
# def run_filtered_search_command(host, username, password, source_ip, destination_ip_or_subnet, port):
#     filtered_rules = []
#     try:
#         source_ip=resolve_fqdn_to_ip(source_ip)
#         destination_ip_or_subnet=resolve_fqdn_to_ip(destination_ip_or_subnet)
#         panorama_device = {
#             'device_type': 'paloalto_panos',
#             'host': host,
#             'username': username,
#             'password': password,
#         }
#         connection = ConnectHandler(**panorama_device)
#         command = f'show running security-policy source {source_ip}'
#         output = connection.send_command(command)

#         destination_network = ipaddress.ip_network(destination_ip_or_subnet, strict=False)

#         filtered_rules = []
#         print(rules)
#         rules = output.splitlines()
        
#         for rule in rules:
#             rule_parts = rule.strip().split()
#             try:
#                 rule_destination = rule_parts[3]
#                 rule_ports = rule_parts[7]
#             except:
#                 continue
#             flag=False
#             rule_destination=resolve_fqdn_to_ip(rule_destination)           
#             try:
#                 if rule_destination == 'any':
#                     if str(port) in rule_ports:
#                         filtered_rules.append(rule)
#                     continue
#                 rule_network = ipaddress.ip_network(rule_destination, strict=False)
#                 if destination_network.subnet_of(rule_network) or destination_network.supernet_of(rule_network) or rule_network.subnet_of(destination_network) or rule_network.supernet_of(destination_network):
#                     if str(port) in rule_ports:
#                         filtered_rules.append(rule)
#             except ValueError:
#                 continue
#         connection.disconnect()
#         if filtered_rules==[]:
#             raise ValueError
#         else:
#             print("Rules found in Panorama: \n\n",filtered_rules)
#     except Exception as e:
#         print(e)
#         print("Not found in Panorama. Searching in ASA")
#         df=pd.read_excel("ASI.xlsx")
#         destination_network=ipaddress.ip_network(destination_ip_or_subnet,strict=False)
#         source_network=ipaddress.ip_network(source_ip,strict=False)
#         for rule_destination in df["Address"]:
#             flag=False
#             for i in rule_destination:
#                     if i=="." or i.isnumeric() or i=="/":
#                         continue
#                     else:
#                         flag=True
#                         break
#             if flag:
#                 rule_destination=resolve_fqdn_to_ip(rule_destination)
#             try:
#                 if rule_destination == 'any':
#                     filtered_rules.append(rule_destination)
#                     continue
#                 rule_network = ipaddress.ip_network(rule_destination, strict=False)
#                 if destination_network.subnet_of(rule_network) or destination_network.supernet_of(rule_network) or source_network.subnet_of(rule_network) or source_network.supernet_of(rule_network) or destination_network.supernet_of(rule_network) or rule_network.subnet_of(destination_network) or rule_network.supernet_of(destination_network) or destination_network.supernet_of(rule_network) or rule_network.subnet_of(source_network) or rule_network.supernet_of(source_network):
#                     filtered_rules.append(rule_destination)
#             except ValueError:
#                 continue
#     if filtered_rules==[]:
#         print("rule doesnot exist in firewall or ASI")
#     else:
#         print(filtered_rules,"are found in ASI")
# host = '192.168.1.100'
# username = 'admin'
# password = 'your_password'
# source_ip = '100.100.250.90'
# destination_ip_or_subnet = '192.168.1.100'
# port = 80
# run_filtered_search_command(host, username, password, source_ip, destination_ip_or_subnet, port)
# # import ipaddress

# # destination_network = ipaddress.ip_network("10.0.0.5", strict=False)
# # rule_network = ipaddress.ip_network("10.0.0.0/24", strict=False)
# # print(rule_network)
# # print(destination_network.subnet_of(rule_network))


# # from netmiko import ConnectHandler

# # def list_zones(host, username, password):
# #     # Define the device connection parameters
# #     device = {
# #         'device_type': 'paloalto_panos',
# #         'host': host,
# #         'username': username,
# #         'password': password,
# #     }

# #     try:
# #         # Establish the connection to the device
# #         connection = ConnectHandler(**device)
        
# #         # Command to list all zones
# #         command = 'show zones'
# #         output = connection.send_command(command)
        
# #         # Print the result for this device
# #         print(f"Zones for device {host}:")
# #         print(output)
        
# #         # Disconnect from the device
# #         connection.disconnect()
# #     except Exception as e:
# #         print(f"Error connecting to {host}: {e}")

# # # List of firewall devices
# # devices = [
# #     {'host': '192.168.1.100', 'username': 'admin', 'password': 'your_password'},
# #     {'host': '192.168.1.101', 'username': 'admin', 'password': 'your_password'},
# #     # Add more devices as needed
# # ]

# # # Iterate over each device and fetch zones
# # for device in devices:
# #     list_zones(device['host'], device['username'], device['password'])


# # from netmiko import ConnectHandler
# # import re

# # def fetch_zones_for_ips(host, username, password, source_ip, dest_ip):
# #     # Define the device connection parameters
# #     device = {
# #         'device_type': 'paloalto_panos',
# #         'host': host,
# #         'username': username,
# #         'password': password,
# #     }

# #     try:
# #         # Establish the connection to the device
# #         connection = ConnectHandler(**device)
        
# #         # Command to list all security policies
# #         command = 'show running security-policy'
# #         output = connection.send_command(command)
        
# #         # Initialize variables to store zones
# #         source_zone = None
# #         dest_zone = None
        
# #         # Split output into lines
# #         lines = output.splitlines()
        
# #         # Iterate over each line to find relevant information
# #         for line in lines:
# #             if source_ip in line:
# #                 # Extract source zone if the source IP is found
# #                 source_zone_match = re.search(r'source-zone\s+(\S+)', line)
# #                 if source_zone_match:
# #                     source_zone = source_zone_match.group(1)
            
# #             if dest_ip in line:
# #                 # Extract destination zone if the destination IP is found
# #                 dest_zone_match = re.search(r'destination-zone\s+(\S+)', line)
# #                 if dest_zone_match:
# #                     dest_zone = dest_zone_match.group(1)
        
# #         # Print the results
# #         print(f"Source IP: {source_ip} is in zone: {source_zone}")
# #         print(f"Destination IP: {dest_ip} is in zone: {dest_zone}")
        
# #         # Disconnect from the device
# #         connection.disconnect()
        
# #     except Exception as e:
# #         print(f"Error connecting to {host}: {e}")

# # # Device details
# # host = '192.168.1.100'
# # username = 'admin'
# # password = 'your_password'
# # source_ip = '10.0.0.1'
# # dest_ip = '10.0.0.2'

# # fetch_zones_for_ips(host, username, password, source_ip, dest_ip)
# # import socket

# # def resolve_fqdn_to_ip(fqdn):
# #     try:
# #         ip_addresses = socket.gethostbyname_ex(fqdn)[2]
# #         return ip_addresses
# #     except socket.gaierror as e:
# #         print(f"Error resolving FQDN {fqdn}: {e}")
# #         return []

# # fqdn = "example.com"
# # ip_addresses = resolve_fqdn_to_ip(fqdn)
# # print(f"IP addresses for FQDN {fqdn}: {ip_addresses}")