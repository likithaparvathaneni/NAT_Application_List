import xml.etree.ElementTree as ET
import time
import socket

# Measure start time
start_time = time.time()

# Load the XML content 
with open(r"pah-pri-xml-eff-conf.txt", 'r') as file:
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
# Function to gather address elements
def print_address(element, address):
    if element.tag == "address-group" or element.tag=="address":
        address.append(ET.tostring(element, encoding='unicode'))
    else:
        for child in element:
            print_address(child, address)

address = []
print_address(root, address)
address = ET.fromstring(address[0])

# Function to store address in a dictionary
def store_address_in_dict(element):
    if element.tag == "address-group" or element.tag =="address":
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
memo = {}

fq_ad={}
def address_check(add):
    # If the address is already processed, return to avoid reprocessing and infinite loops
    if add in memo:
        return
    # Initialize the address in memo with an empty set
    memo[add] = set()

    # Process static addresses
    if "static" in address_dict[add]:
        for a in address_dict[add]["static"]:
            if a in address_dict:
                if a not in memo:
                    address_check(a)
                # Update the memo entry with addresses found in the static address check
                memo[add].update(memo[a])
            else:
                memo[add].add(a)
                
    # Process IP-Netmask addresses
    if "ip-netmask" in address_dict[add]:
        for ip in address_dict[add]["ip-netmask"].split(","):
            memo[add].add(ip)
    
    # Process FQDN addresses and resolve to IP addresses
    if "fqdn" in address_dict[add]:
        for fq in address_dict[add]["fqdn"].split(","):
            fq_ad[fq]=[fq]
            memo[add].add(fq)

for add in address_dict:
    address_check(add)

# # Function to gather application-group elements
def print_application_group(element, application_group):
    if element.tag == "application-group":
        application_group.append(ET.tostring(element, encoding='unicode'))
    else:
        for child in element:
            print_application_group(child, application_group)

application_group = []
print_application_group(root, application_group)
application_group = ET.fromstring(application_group[0])

# Function to store application-group in a dictionary
def store_application_group_in_dict(element):
    if element.tag == "application-group":
        application_group_dict = {}
        for entry in element.findall(".//entry"):
            entry_dict = {}
            for child in entry:
                if child.tag == "members":
                    entry_dict[child.tag] = [subchild.text.strip() for subchild in child]
                else:
                    entry_dict[child.tag] = child.text.strip()
            application_group_dict[entry.attrib['name']] = entry_dict
        return application_group_dict

application_group_dict = store_application_group_in_dict(application_group)
import xml.etree.ElementTree as ET

def print_service_group(element, service_group):
    if element.tag in ["service-group", "service"]:
        service_group.append(ET.tostring(element, encoding='unicode'))
    else:
        for child in element:
            print_service_group(child, service_group)

service_group = []
print_service_group(root, service_group)
service_group = [ET.fromstring(sg) for sg in service_group]

# Function to store service-group and service in a dictionary
def store_service_group_in_dict(elements):
    service_group_dict = {}
    for element in elements:
        if element.tag in ["service-group", "service"]:
            for entry in element.findall(".//entry"):
                entry_dict = {}
                for child in entry:
                    if child.tag == "members":
                        entry_dict[child.tag] = {}
                        for subchild in child:
                            entry_dict[child.tag][subchild.text] = []
                    elif child.tag == "protocol":
                        for protocol in child:
                            port = protocol.find("port")
                            if port is not None:
                                entry_dict["protocol"] = protocol.tag
                                entry_dict["port"] = port.text
                service_group_dict[entry.attrib['name']] = entry_dict
    return service_group_dict

# Example usage
service_group_dict = store_service_group_in_dict(service_group)
memo1 = {}

memo1 = {}

def serv_objects(ser):
    if ser in memo1:
        return
    memo1[ser] = {"port": [], "protocol": [],"service":[]}

    if "members" in service_group_dict[ser]:
        for a in service_group_dict[ser]["members"]:
            if a in service_group_dict:
                if a not in memo1:
                    serv_objects(a)
                memo1[ser]["port"].extend(memo1[a]["port"])
                memo1[ser]["protocol"].extend(memo1[a]["protocol"])
            else:
                memo1[ser]["service"].append(a)
    if "protocol" in service_group_dict[ser]:
        for protocol in service_group_dict[ser]["protocol"].split(","):
            memo1[ser]["protocol"].append(protocol)
    if "port" in service_group_dict[ser]:
        for port in service_group_dict[ser]["port"].split(","):
            memo1[ser]["port"].append(port)

for s in service_group_dict:
    serv_objects(s)
import pandas as pd

# Load the app defaults from the CSV
app_defaults = pd.read_csv(    r"C:\Users\gopiprashanth.raju\OneDrive - Providence St. Joseph Health\Desktop\Network-Automation-Tool-Gopi (3)\Network-Automation-Tool-Gopi\Network-Automation-Tool-Gopi\App\Compare_final\applipedia_data_cleaned.csv"
)

# Convert the app_defaults to a dictionary for faster access
app_defaults_dict = app_defaults.set_index('Name').T.to_dict('list')
print(app_defaults_dict)

rules = {}
for rule_name, rule in rule_dict.items():
    rules[rule_name] = {}

    for k in rule:
        rules[rule_name][k] = rule[k]
        rules[rule_name][k+"dis"] = rule[k]

    # Process source addresses
    source_address = []
    if "source" in rule:
        for add in rule["source"]:
            if add in memo:
                source_address.extend(memo[add])
            else:
                source_address.append(add)
    rules[rule_name]["source"] = source_address

    # Process destination addresses
    destination_address = []
    if "destination" in rule:
        for add in rule["destination"]:
            if add in memo:
                destination_address.extend(memo[add])
            else:
                destination_address.append(add)
    rules[rule_name]["destination"] = destination_address

    # Process ports and protocols
    ports = []
    protocols = []
    services = []
    apps=[]
    if "service" in rule:
        for ser in rule["service"]:
            if ser == "application-default":
                if "application" in rule and rule["application"]:
                    for app in rule["application"]:
                        if app in app_defaults_dict:
                            
                            ports.extend(app_defaults_dict[app][9].strip("[]").replace("'", "").split(","))
                            protocols.extend(app_defaults_dict[app][8].strip("[]").replace("'", "").split(","))
                            # Check OnClick_Last_Digit and handle accordingly
                            last_digit = int(app_defaults_dict[app][7])  # Assuming this column represents OnClick_Last_Digit
                            if last_digit == 1:
                                idx = app_defaults[app_defaults['Name'] == app].index[0] + 1
                                while idx < len(app_defaults) and int(app_defaults.iloc[idx, 8]) not in [0, 1]:
                                    next_app = app_defaults.iloc[idx, 1]
                                    apps.append(next_app)
                                    print(next_app)
                                    ports.extend(app_defaults_dict[next_app][9].strip("[]").replace("'", "").split(","))
                                    protocols.extend(app_defaults_dict[next_app][8].strip("[]").replace("'", "").split(","))
                                    idx += 1
                                rule["application"].extend(apps)
                continue
            elif ser in ["service-https", "service-http"]:
                if ser == "service-https":
                    ports.append("443")
                    protocols.append("tcp")
                elif ser == "service-http":
                    ports.append("80")
                    protocols.append("tcp")
            elif ser in memo1:
                ports.extend(memo1[ser]["port"])
                protocols.extend(memo1[ser]["protocol"])
                services.extend(memo1[ser]["service"])
            else:
                services.append(ser)
    rules[rule_name]["port"] = ports
    rules[rule_name]["protocol"] = protocols
    rules[rule_name]["service"] = services

    # Process other attributes
    for attr in ["action", "application", "category"]:
        if attr in rule:
            rules[rule_name][attr] = rule[attr]

    # Generate entries
    r = rules[rule_name]
    r["entries"] = []
    if "application" not in r:
        r["application"] = []
    if "port" not in r:
        r["port"] = []
    if "protocol" not in r:
        r["protocol"] = []
    for at in ["port","protocol","application","service"]:
        rules[rule_name][at]=set(rules[rule_name][at])
        if "" in rules[rule_name][at]:
            rules[rule_name][at].remove("")
        rules[rule_name][at]=list(set(rules[rule_name][at]))
    for application in r["application"]:
        for protocol in r["protocol"]:
            for port in r["port"]:
                entry = {
                    "application": application,
                    "protocol": protocol,
                    "port": port
                }
                r["entries"].append(entry)

    if "service" in r and "application-default" in r["service"]:
        for app in r["application"]:
            if app in app_defaults_dict:
                for port in app_defaults_dict[app][10].strip("[]").replace("'", "").split(","):
                    for protocol in app_defaults_dict[app][9].strip("[]").replace("'", "").split(","):
                        entry = {
                            "application": app,
                            "protocol": protocol,
                            "port": port
                        }
                        r["entries"].append(entry)
    if "service" in r and "any" in r["service"]:
        entry = {
            "application": "any",
            "protocol": "any",
            "port": "any"
        }
        r["entries"].append(entry)
    for at in ["port","protocol","application","service"]:
        rules[rule_name][at]=set(rules[rule_name][at])
        if "" in rules[rule_name][at]:
            rules[rule_name][at].remove("")
        rules[rule_name][at]=list(set(rules[rule_name][at]))

# Save rules to file
with open("rules.txt", "w") as f:
    f.write(str(rules))

# Write rules to file
with open("rules.txt", "w") as f:
    f.write(str(rules))
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
end_time = time.time()

# Print time taken for execution
print(f"Execution time: {end_time - start_time} seconds")

# with open("rule.txt", "w") as f:
#     f.write(str(detailed_rules))
# print(detailed_rules["Global_BGP"])
# print(address_dict["AIC_MDF_Management"])