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
from collections import OrderedDict
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
    if 'negate-source' in rule and rule['negate-source'] and src!="any":
         src_flag=not src_flag
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
                
                if dest=="any" or start_ip <=  ipaddress.ip_address(dest) <= end_ip:
                        dest_flag=True
            else:
                dest_flag = (d == "any" or dest == "any" or
                                (ipaddress.ip_network(d, strict=False).version == ipaddress.ip_network(dest, strict=False).version and
                                (ipaddress.ip_network(d, strict=False).supernet_of(ipaddress.ip_network(dest, strict=False)) or
                                ipaddress.ip_network(dest, strict=False).subnet_of(ipaddress.ip_network(d, strict=False)))))
        except Exception as e:
            continue
    if 'negate-destination' in rule and rule['negate-destination']=="yes" and dest!="any":
         dest_flag=not dest_flag
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
    if [src_flag, dest_flag, src_zone_flag, dest_zone_flag, port_flag, protocol_flag, application_flag].count(False)==1 and (rule["action"].strip() == action or action == "any") and ('negate-source' in rule and rule['negate-source']!="yes" and 'negate-destination' in rule and rule["negate-destination"]!="yes"):
        return True, rule["name"], [src_flag, dest_flag, src_zone_flag, dest_zone_flag, port_flag, protocol_flag, application_flag]
    else:
        return False, rule["name"], []

def check_if_rule_exists(rule, src, dest, src_zone, dest_zone, port, protocol, action, application):
    result, rule_name, result_arr = match_rule(rule, src, dest, src_zone, dest_zone, port, protocol, action, application)
    r = OrderedDict()

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

def main( source_ip, dest_ip, src_zone, dest_zone, port, protocol, action, application,rules):
    res = []
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
    return res
