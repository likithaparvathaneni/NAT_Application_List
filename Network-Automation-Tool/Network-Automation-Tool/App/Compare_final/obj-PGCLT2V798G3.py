import xml.etree.ElementTree as ET
import time
import socket

# Measure start time
start_time = time.time()

# Load the XML content
with open(r"C:\Users\gopiprashanth.raju\Downloads\pah-pri-xml-eff-conf.txt", 'r') as file:
    xml_content = file.read()

root = ET.fromstring(xml_content)

# Function to gather rulebase elements
def print_rulebase(element, rules):
    if element.tag == "rulebase":
        rules.append(ET.tostring(element, encoding='unicode'))
    else:
        for child in element:
            print_rulebase(child, rules)

rules = []
print_rulebase(root, rules)
rules = ET.fromstring(rules[0])

# Function to store rulebase in a dictionary
def store_rule_in_dict(element):
    if element.tag == "rulebase":
        rule_dict = {}
        for entry in element.findall(".//entry"):
            entry_dict = {}
            for child in entry:
                entry_dict[child.tag] = [subchild.text.strip() for subchild in child]
                if child.tag=="action":
                    entry_dict[child.tag]=child.text
            rule_dict[entry.attrib['name']] = entry_dict
        return rule_dict

rule_dict = store_rule_in_dict(rules)
print(rule_dict)
# Function to gather address elements
def print_address(element, address):
    if element.tag == "address-group":
        address.append(ET.tostring(element, encoding='unicode'))
    else:
        for child in element:
            print_address(child, address)

address = []
print_address(root, address)
address = ET.fromstring(address[0])

# Function to store address in a dictionary
def store_address_in_dict(element):
    print(element.tag)
    if element.tag == "address-group":
        address_dict = {}
        for entry in element.findall(".//entry"):
            entry_dict = {}
            for child in entry:
                if child.tag == "ip-netmask":
                    entry_dict[child.tag] = child.text.strip()
                elif child.tag == "fqdn":
                    entry_dict[child.tag] = child.text.strip()
                else:
                    entry_dict[child.tag] = [subchild.text.strip() for subchild in child]
            address_dict[entry.attrib['name']] = entry_dict
        return address_dict
address_dict = store_address_in_dict(address)
print(address_dict)
# # Function to gather application-group elements
# def print_application_group(element, application_group):
#     if element.tag == "application-group":
#         application_group.append(ET.tostring(element, encoding='unicode'))
#     else:
#         for child in element:
#             print_application_group(child, application_group)

# application_group = []
# print_application_group(root, application_group)
# application_group = ET.fromstring(application_group[0])

# # Function to store application-group in a dictionary
# def store_application_group_in_dict(element):
#     if element.tag == "application-group":
#         application_group_dict = {}
#         for entry in element.findall(".//entry"):
#             entry_dict = {}
#             for child in entry:
#                 if child.tag == "members":
#                     entry_dict[child.tag] = [subchild.text.strip() for subchild in child]
#                 else:
#                     entry_dict[child.tag] = child.text.strip()
#             application_group_dict[entry.attrib['name']] = entry_dict
#         return application_group_dict

# application_group_dict = store_application_group_in_dict(application_group)

# # Function to gather service-group elements
# def print_service_group(element, service_group):
#     if element.tag == "service-group":
#         service_group.append(ET.tostring(element, encoding='unicode'))
#     else:
#         for child in element:
#             print_service_group(child, service_group)

# service_group = []
# print_service_group(root, service_group)
# service_group = ET.fromstring(service_group[0])

# # Function to store service-group in a dictionary
# def store_service_group_in_dict(element):
#     if element.tag == "service-group":
#         service_group_dict = {}
#         for entry in element.findall(".//entry"):
#             entry_dict = {}
#             for child in entry:
#                 if child.tag == "members":
#                     entry_dict[child.tag] = {}
#                     for subchild in child:
#                         entry_dict[child.tag][subchild.text] = []
#             service_group_dict[entry.attrib['name']] = entry_dict
#         return service_group_dict

# service_group_dict = store_service_group_in_dict(service_group)

# service_objects = {}

# # Function to search entries for members
# def search_entries_for_members(root, service_group_dict):
#     for service in service_group_dict.values():
#         for mem in service["members"]:
#             protocols = {}
#             for entry in root.findall(f".//entry[@name='{mem}']"):
#                 for protocol in entry.findall(".//protocol/*"):
#                     if protocol.tag not in protocols:
#                         protocols[protocol.tag] = []
#                     for port in protocol.findall("port"):
#                         protocols[protocol.tag].append(port.text)
#             service_objects[mem] = protocols

# search_entries_for_members(root, service_group_dict)

# # Function to resolve FQDN to IP addresses
# def resolve_fqdn(fqdn):
#     try:
#         ips = socket.gethostbyname_ex(fqdn)[2]  # This returns all IPs for the FQDN
#         return ips
#     except socket.gaierror:
#         return []
# print(address_dict)
# # Function to resolve to address iteratively
# def resolve_to_address(address):
#     resolved_addresses = []
#     addresses_to_check = [address]

#     while addresses_to_check:
#         current_address = addresses_to_check.pop()
#         if current_address in address_dict:
#             addr_entry = address_dict[current_address]
#             if "ip-netmask" in addr_entry:
#                 resolved_addresses.append(addr_entry["ip-netmask"])
#             elif "fqdn" in addr_entry:
#                 resolved_ips = resolve_fqdn(addr_entry["fqdn"])
#                 resolved_addresses.extend(resolved_ips)
#             else:
#                 for key in addr_entry:
#                     addresses_to_check.extend(addr_entry[key])
#         else:
#             resolved_addresses.append(current_address)

#     return resolved_addresses

# # Create detailed rules
# detailed_rules = {}
# for rule_name, rule in rule_dict.items():
#     if rule_name == "intrazone-default" or rule_name == "interzone-default":
#         continue
#     r = {}

#     # Populate the rule's basic information
#     for k in rule:
#         r[k] = rule[k]
#         r[k + "display"] = rule[k]

#     # Handle source addresses
#     r["source"] = []
#     if "source" in rule:
#         for address in rule["source"]:
#             r["source"].extend(resolve_to_address(address))

#     # Handle destination addresses
#     r["destination"] = []
#     if "destination" in rule:
#         for address in rule["destination"]:
#             r["destination"].extend(resolve_to_address(address))

#     # Handle applications
#     r["application"] = []
#     if "application" in rule:
#         for app in rule["application"]:
#             if app in application_group_dict:
#                 r["application"].extend(application_group_dict[app])
#             else:
#                 r["application"].append(app)

#     # Handle services
#     r["service"] = []
#     if "service" in rule:
#         for ser in rule["service"]:
#             if ser in service_group_dict:
#                 r["service"].extend(service_group_dict[ser])
#             else:
#                 r["service"].append(ser)

#     detailed_rules[rule_name] = r

# # Measure end time
# end_time = time.time()

# # Print time taken for execution
# print(f"Execution time: {end_time - start_time} seconds")

# with open("rule.txt", "w") as f:
#     f.write(str(detailed_rules))
# print(detailed_rules["Global_BGP"])
# print(address_dict["AIC_MDF_Management"])