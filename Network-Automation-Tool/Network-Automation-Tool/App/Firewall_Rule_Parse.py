import ipaddress
import socket
from netmiko import ConnectHandler
import pandas as pd
import time
from ipaddress import ip_network
import os
import concurrent.futures

def resolve_fqdn_to_ip(fqdn):
    try:
        ip_addresses = socket.gethostbyname_ex(fqdn)[2]
        return ip_addresses[0]
    except socket.gaierror:
        return fqdn
    



import threading
from queue import Queue
import ipaddress
from copy import deepcopy

import xml.etree.ElementTree as ET
import time
import socket

# Measure start time
# start_time = time.time()
def rules_write(firewall,ET):
    if firewall=="S1" or firewall=="A1":
        with open(r"Compare_final\pah-pri-xml-eff-conf.txt", 'r') as file:
            xml_content = file.read()
    else:
        with open(r"Compare_final\SMM-NFW-SMDF-02_Secondary_eff_rules", 'r') as file:
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
                    entry_dict[child.tag] = [subchild.text.strip() if subchild.text is not None else '' for subchild in child]
                    if child.tag=="action":
                        entry_dict[child.tag]=child.text
                rule_dict[entry.attrib['name']] = entry_dict
            return rule_dict

    rule_dict = store_rule_in_dict(rules)
    def print_address(element, address):
        if element.tag == "address-group" or element.tag == "address":
            address.append(ET.tostring(element, encoding='unicode'))
        else:
            for child in element:
                print_address(child, address)

    address = []
    print_address(root, address)

    # Convert all collected address strings to elements
    address_elements = [ET.fromstring(addr) for addr in address]

    # Function to store addresses in a dictionary
    def store_address_in_dict(elements):
        address_dict = {}
        for element in elements:
            if element.tag == "address-group" or element.tag == "address":
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

    address_dict = store_address_in_dict(address_elements)

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
                if a=="RFC1918_Private_Networks":
                    print(a)
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
                    memo1[ser]["service"].append(a)
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
    app_defaults = pd.read_csv( r"Compare_final\applipedia_data_cleaned.csv"
    )

    # Convert the app_defaults to a dictionary for faster access
    app_defaults_dict = app_defaults.set_index('Name').T.to_dict('list')
    rules = {}
    res=[]
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
        rules[rule_name]["source"] = list(set(source_address))

        # Process destination addresses
        destination_address = []
        if "destination" in rule:
            for add in rule["destination"]:
                if add in memo:
                    destination_address.extend(memo[add])
                else:
                    destination_address.append(add)
        rules[rule_name]["destination"] = list(set(destination_address))

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
        if "service" in rule and "service-http" in rule["service"]:
            protocols.append("tcp")
            ports.append("80")
        if "serive" in rule and  "service-https" in rule["service"]:
            protocols.append(tcp)
            ports.append("443")
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
                        "destination_port": port
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
                                "destination_port": port
                            }
                            r["entries"].append(entry)
        if "service" in r and "any" in r["service"]:
            entry = {
                "application": "any",
                "protocol": "any",
                "destination_port": "any"
            }
            r["entries"].append(entry)
        for at in ["port","protocol","application","service"]:
            rules[rule_name][at]=set(rules[rule_name][at])
            if "" in rules[rule_name][at]:
                rules[rule_name][at].remove("")
            rules[rule_name][at]=list(set(rules[rule_name][at]))
            r=rules[rule_name]
            r["name"]=rule_name
            res.append(r)
        if "entries" in rule:
            for entry in rule["entries"]:
                    if "service" in entry:
                            del entry[service]
    # Save rules to file
    with open("rules.txt", "w") as f:
        f.write(str(res))
    rules=res
    # Write rules to file
    with open("rules.txt", "w") as f:
        f.write(str(rules))
    return rules,memo,memo1
# def parse_palo_alto_rule(rule):
#     parsed_entries = []
#     # Split the rule into individual entries
#     if "[" in rule:
#         entries = rule[rule.index("[")+1:rule.index("]")].strip().split(" ")
#     else:
#         rule = rule[rule.index("application/service")+len("application/service"):]
#         rule = rule[rule.index(" "):rule.index(";")]
#         entries = rule.strip().split()

#     # Iterate over each entry
#     for entry in entries:
#         if entry.strip() == "...":
#             continue
#         # Split the entry into components
#         val = entry.split('/')
#         application, protocol, src_port, dst_port = val[:4]

#         # Further split the app_protocol into application and protocol
#         x, app_protocol = application.split(':')

#         # Create a dictionary for the parsed entry
#         parsed_entry = {
#             'application': app_protocol,
#             'protocol': protocol,
#             'source_port': src_port,
#             'destination_port': dst_port
#         }
#         parsed_entries.append(parsed_entry)
#     return parsed_entries

# def parse_firewall_rules(raw_rules):
#     from copy import deepcopy

#     rules = []
#     current_rule = {
#         "name": "",
#         "source": "",
#         "destination": "",
#         "action": "",
#         "src_negate": False,
#         "dest_negate": False,
#     }

#     for line in raw_rules.strip().split('\n'):
#         if not current_rule["name"] and "{" in line:
#             current_rule = {
#                 "name": "",
#                 "source": "",
#                 "destination": "",
#                 "action": "",
#                 "src_negate": False,
#                 "dest_negate": False,
#             }
#             current_rule["name"] = line[:line.index(";")][1:]
#         if "index:" in line:
#             line = line[line.index("index"):]
#             current_rule["index"] = int(line[line.index("index:")+len("index: "):line.index('"')])+1
#         if not current_rule["source"] and "source" in line:
#             src = line[line.index("source")+6:line.index(";")].strip()
#             if "(negate)" in src:
#                 current_rule["src_negate"] = True
#                 src = src.replace("(negate)", "").strip()
#             if "[" in src:
#                 src = src[src.index("[")+1:src.index("]")]
#             current_rule["source"] = []
#             for s in src.strip().split():
#                 current_rule["source"].append(s)
#         if not current_rule["destination"] and "destination" in line:
#             dest = line[line.index("destination")+11:line.index(";")].strip()
#             if "(negate)" in dest:
#                 current_rule["dest_negate"] = True
#                 dest = dest.replace("(negate)", "").strip()
#             if "[" in dest:
#                 dest = dest[dest.index("[")+1:dest.index("]")]
#             current_rule["destination"] = []
#             for d in dest.strip().split():
#                 current_rule["destination"].append(d)
#         if not current_rule["action"] and "action" in line:
#             current_rule["action"] = line[line.index("action")+6:line.index(";")].strip()
#         if "from" in line:
#             current_rule["from"] = []
#             fr = line[line.index("from")+4:line.index(";")].strip()
#             if "[" in fr:
#                 fr = fr[fr.index("[")+1:fr.index("]")]
#             for f in fr.strip().split():
#                 current_rule["from"].append(f)
#         if "to" in line and "to" not in current_rule:
#             current_rule["to"] = []
#             to = line[line.index("to")+2:line.index(";")].strip()
#             if "[" in to:
#                 to = to[to.index("[")+1:to.index("]")]
#             for t in to.strip().split():
#                 current_rule["to"].append(t)
#         if "application/service" in line:
#             current_rule["entries"] = parse_palo_alto_rule(line)
#         if "}" in line:
#             rules.append(deepcopy(current_rule))
#             current_rule["name"] = ""
#             current_rule["action"] = ""
#             current_rule["source"] = ""
#             current_rule["destination"] = ""
#             current_rule["src_negate"] = False
#             current_rule["dest_negate"] = False
#     return rules
# import concurrent.futures
# import ipaddress

def match_rule(rule, src, dest, src_zone, dest_zone, port, Protocol, action, application):
    src_flag = False
    dest_flag = False
    dest_zone_flag = False
    src_zone_flag = False
    port_flag = False
    protocol_flag = False
    application_flag = False
    arr=["source","destination","to","from"]
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
            else:
                src_flag = (s == "any" or src == "any" or
                                (ipaddress.ip_network(s, strict=False).version == ipaddress.ip_network(src, strict=False).version and
                                (ipaddress.ip_network(s, strict=False).subnet_of(ipaddress.ip_network(src, strict=False)) or
                                ipaddress.ip_network(s, strict=False).supernet_of(ipaddress.ip_network(src, strict=False)) or
                                ipaddress.ip_network(src, strict=False).subnet_of(ipaddress.ip_network(s, strict=False)))))
        except Exception as e:
            continue
    if 'negate-source' in rule and rule['negate-source']:
         src_flag=False
    for d in rule["destination"]:
        if dest_flag:
            continue
        if d == "...":
            continue
        try:
            if "-" in d:
                start_ip,end_ip=d.split("-")
                start_ip = ipaddress.ip_address(start_ip)
                end_ip = ipaddress.ip_address(end_ip)
        
                # Check if IP falls within the range
                
                if src=="any" or start_ip <=  ipaddress.ip_address(dest) <= end_ip:
                        dest_flag=True
            else:
                dest_flag = (d == "any" or dest == "any" or
                                (ipaddress.ip_network(d, strict=False).version == ipaddress.ip_network(dest, strict=False).version and
                                (ipaddress.ip_network(d, strict=False).supernet_of(ipaddress.ip_network(dest, strict=False)) or
                                ipaddress.ip_network(dest, strict=False).subnet_of(ipaddress.ip_network(d, strict=False)))))
        except Exception as e:
            continue
    if 'negate-destination' in rule and rule['negate-destination']=="yes":
         dest_flag=False
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
                if isinstance(port,list):
                        p=port
                        for port in p:
                                if "-" in port:
                                        s1,e1=port.split("-")
                                        s1=int(s1)
                                        e1=int(e1)
                                        if "-" in entry["destination_port"]:
                                                start_port,end_port=entry["destination_port"].split("-")
                                                start_port = int(start_port)
                                                end_port = int(end_port)
                                                if s1>=start_port and e1<=end_port:
                                                        if (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                                protocol_flag = entry["protocol"]
                                                                port_flag=entry["destination_port"]
                                                                application_flag = entry["application"]
                                        else:
                                                if (entry["destination_port"] == "any" or port == "any" or entry["destination_port"] == port or s1<=int(entry["destination_port"])<=e1) and (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                        port_flag = entry["destination_port"]
                                                        protocol_flag = entry["protocol"]
                                                        application_flag = entry["application"]
                                                



                                if "-" in entry["destination_port"] and entry["destination_port"]!="app-default" and port!="any":
                                        start_port,end_port=entry["destination_port"].split("-")
                                        start_port = int(start_port)
                                        end_port = int(end_port)
                                        # Check if IP falls within the range
                                        check_port=int(port)
                                        if start_port <=  check_port <= end_port:
                                                if (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and \
                                                        (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                        protocol_flag = entry["protocol"]
                                                        port_flag=entry["destination_port"]
                                                        application_flag = entry["application"]
                                else:
                                        if port_flag:
                                                continue
                                        if (entry["destination_port"] == "any" or port == "any" or entry["destination_port"] == port) and (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and \
                                                (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                port_flag = entry["destination_port"]
                                                protocol_flag = entry["protocol"]
                                                application_flag = entry["application"]
                else:
                        if not isinstance(port,list) and  "-" in port:
                                s1,e1=port.split("-")
                                s1=int(s1)
                                e1=int(e1)
                                if "-" in entry["destination_port"]:
                                        start_port,end_port=entry["destination_port"].split("-")
                                        start_port = int(start_port)
                                        end_port = int(end_port)
                                        if s1>=start_port and e1<=end_port:
                                                if (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and \
                                                (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                        protocol_flag = entry["protocol"]
                                                        port_flag=entry["destination_port"]
                                                        application_flag = entry["application"]
                                else:
                                        if (entry["destination_port"] == "any" or port == "any" or entry["destination_port"] == port or s1<=int(entry["destination_port"])<=e1) and (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and  (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                port_flag = entry["destination_port"]
                                                protocol_flag = entry["protocol"]
                                                application_flag = entry["application"]
                                        


                        else:
                                if "-" in entry["destination_port"] and entry["destination_port"]!="app-default" and port!="any":
                                        start_port,end_port=entry["destination_port"].split("-")
                                        start_port = int(start_port)
                                        end_port = int(end_port)
                                        # Check if IP falls within the range
                                        check_port=int(port)
                                        if start_port <=  check_port <= end_port:
                                                if (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                        protocol_flag = entry["protocol"]
                                                        port_flag=entry["destination_port"]
                                                        application_flag = entry["application"]
                                else:
                                        if port_flag:
                                                continue
                                        if (entry["destination_port"] == "any" or port == "any" or entry["destination_port"] == port) and (entry["protocol"] == "any" or Protocol == "any" or entry["protocol"] == Protocol) and \
                                                (entry["application"] == "any" or application == "any" or entry["application"] == application):
                                                port_flag = entry["destination_port"]
                                                protocol_flag = entry["protocol"]
                                                application_flag = entry["application"]
        except Exception as e:
                print(f"Invalid port: {entry}", " Error", e)
    if src_flag and dest_flag and src_zone_flag and dest_zone_flag and port_flag and application_flag and (rule["action"].strip() == action or action == "any"):
        return True, rule["name"], [src_flag, dest_flag, src_zone_flag, dest_zone_flag, port_flag, protocol_flag, application_flag]
    else:
        return False, rule["name"], []

def check_if_rule_exists(rule, src, dest, src_zone, dest_zone, port, protocol, action, application):
    result, rule_name, result_arr = match_rule(rule, src, dest, src_zone, dest_zone, port, protocol, action, application)
    r = {}
    if rule_name:
        rule_name = rule_name[1:]
    if result:
        for k in rule:
            r[k] = rule[k]
        # r["source"] = [result_arr[0]]
        # r["destination"] = [result_arr[1]]
        # r["from"] = [result_arr[2]]
        # r["to"] = [result_arr[3]]
        # r["destination_port"] = [result_arr[4]]
        # r["protocol"] = [result_arr[5]]
        # r["application"] = [result_arr[6]]
    return result, rule_name, r

def parallel_check_rules(rules, source_ip, dest_ip, src_zone, dest_zone, port, protocol, action, application):
    res = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(check_if_rule_exists, rule, source_ip, dest_ip,
                                   src_zone, dest_zone,
                                   port, protocol,
                                   action,
                                   application) for rule in rules]
        
        for future in concurrent.futures.as_completed(futures):
            exists, rule_name, rule = future.result()
            if exists:
                res.append(rule)
    
    return res

def main(firewall, source_ip, dest_ip, src_zone, dest_zone, port, protocol, action, application, q):
    firewall_name= firewall
    res = []
    rules,memo,memo1=rules_write(firewall_name,ET)
    res = parallel_check_rules(rules,
                                       source_ip,
                                       dest_ip,
                                       src_zone,
                                       dest_zone,
                                       port,
                                       protocol,
                                       action,
                                       application)
    res1=[]
    for i in res:
        if i not in res1:
                res1.append(i)
    res=res1
    for i in memo1:
        memo[i]=memo1[i]
    f=open("memo.txt","w")
    f.write(str(memo))
    f.close()
    if res:
        q.put([firewall_name, res,memo])
    else:
        print(23)
        q.put([firewall_name, "No rule Found",memo])
    return res or ["No rule Found"]
