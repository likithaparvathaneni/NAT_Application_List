import ipaddress
import sqlite3
import socket
from netmiko import ConnectHandler
import pandas as pd
import time

def resolve_fqdn_to_ip(fqdn):
    try:
        ip_addresses = socket.gethostbyname_ex(fqdn)[2]
        return ip_addresses[0]
    except socket.gaierror:
        return fqdn


# def firewall_db(src_zone,source,dest_zone, destination,protocol,port):
#     firewall_matches = {}
#     print(src_zone,source,dest_zone, destination,protocol,port)
#     try:
#         # Connect to DB and create a cursor
#         conn = sqlite3.connect('sql.db')
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM firewall")
#         rows = cursor.fetchall()

#         for row in rows:
#             firewall_name = row[1]
#             firewall_ip = row[0]
#             zones = row[3].split(",")
#             subnets = row[2].split(",")
#             # print(subnets)
#             for i in range(len(subnets)):
#                 if subnets[i] == "N/A":
#                     continue
#                 if zones[i].strip() == "":
#                     zones[i] = "N/A"
#                 try:
#                     destination_network = ipaddress.ip_network(resolve_fqdn_to_ip(destination), strict=False) if destination != "any" else None
#                     source_network = ipaddress.ip_network(resolve_fqdn_to_ip(source), strict=False) if source != "any" else None
#                     subnet_network = ipaddress.ip_network(resolve_fqdn_to_ip(subnets[i]), strict=False) if subnets[i] != "any" else None

#                     if ((subnet_network and source_network and (subnet_network.subnet_of(source_network) or source_network.subnet_of(subnet_network))) or 
#                         (subnet_network and destination_network and (subnet_network.supernet_of(destination_network) or destination_network.subnet_of(subnet_network)))) or \
#                         (source == "any" or destination == "any" or subnets[i] == "any"):

#                         if firewall_ip not in firewall_matches:
#                             firewall_matches[firewall_ip] = []
#                         firewall_matches[firewall_ip].append(firewall_name)
#                 except Exception as e:
#                     print(e)
#                     continue

#     except Exception as e:
#         print(e)
#         with open("Device_status.txt", "w") as f:
#             f.write(f"Error occurred: {e}")
#         time.sleep(10)
#     finally:
#         conn.close()
#     print("matched",list(firewall_matches.keys())[0])
#     # Reading device credentials from a file
#     devices = []
#     with open("host.txt", "r") as df:
#         for row in df.readlines():
#             device = {
#                 'ip': row.split(",")[0],
#                 'username': row.split(",")[1],
#                 'password': row.split(",")[2]
#             }
#             devices.append(device)

#     rule_results = []
#     for device in devices:
#         device_info = {
#             "device_type": "autodetect",
#             "host": device["ip"],
#             "username": device["username"],
#             "password": device["password"],
#             "timeout": 20,
#             "global_delay_factor": 4
#         }
#         if device["ip"] not in firewall_matches:
#             continue

#         try:
#             df = pd.read_excel("protocols.xlsx")
#             protocol_row = df[df['Protocol'].str.lower() == protocol.lower()]
#             if protocol_row.empty:
#                 raise ValueError(f"Protocol name '{protocol}' not found in Excel file.")
#             protocol_number = int(protocol_row['Number'].values[0])

#             net_connect = ConnectHandler(**device_info)
#             time.sleep(5)
#             prompt = net_connect.find_prompt()
#             if prompt[-1] == "#":
#                 net_connect.send_command("terminal pager 0")
#                 command = (
#                     f"test security-policy-match from {src_zone} to {dest_zone} "
#                     f"destination-port {port} protocol {protocol_number} "
#                     f"source {source} destination {destination}"
#                 )
#                 output = net_connect.send_command(command, expect_string=prompt[-1], read_timeout=20)
#                 if "{" in output:
#                     rules=[]
#                     rule=""
#                     for line in output.strip().split("\n"):
#                         if "{" in line:
#                             if rule!="":
#                                 status = "Allowed" if "allow" in output.lower() else "Deny"  # Placeholder for status extraction
#                                 rule_results.append({device["ip"]: {"rule_name": rule, "status": status}})
#                                 rule=line
#                         else:
#                             rule+=line
#                     if rule:
#                         status = "Allowed" if "allow" in output.lower() else "Deny"  # Placeholder for status extraction
#                         rule_results.append({device["ip"]: {"rule_name": rule, "status": status}})
#             else:
#                 print("Unexpected prompt:", prompt)
#         except Exception as e:
#             print(f"Error processing device {device['ip']}: {e}")
#     generate_html_page(rule_results, firewall_matches, source, destination, src_zone, dest_zone, protocol, port)

def generate_html_page(rule_results, firewall_matches, source, destination, src_zone, dest_zone, protocol, port):
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Firewall Rules Report</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0; }}
            .container {{ margin-top: 50px; }}
            .report-title {{ text-align: center; margin-bottom: 30px; }}
            .passed-inputs {{ margin-bottom: 30px; padding: 20px; background-color: #e9ecef; border-radius: 5px; }}
            .table-container {{ display: flex; justify-content: center; margin-bottom: 30px; }}
            table {{ width: 100%; max-width: 800px; border-collapse: collapse; text-align: left; }}
            .table thead {{ background-color: #343a40; color: #fff; }}
            .table tbody tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .table tbody tr.status-allow {{ background-color: #d4edda; color: #155724; }}
            .table tbody tr.status-deny {{ background-color: #f8d7da; color: #721c24; }}
            .rule-details {{ white-space: pre-wrap; word-break: break-word; }}
            .close-button {{ display: flex; justify-content: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 class="report-title">Firewall Rules Report</h2>
            <div class="passed-inputs">
                <h5>Passed Inputs</h5>
                <p><strong>Source:</strong> {source}</p>
                <p><strong>Destination:</strong> {destination}</p>
                <p><strong>Source Zone:</strong> {src_zone}</p>
                <p><strong>Destination Zone:</strong> {dest_zone}</p>
                <p><strong>Protocol:</strong> {protocol}</p>
                <p><strong>Port:</strong> {port}</p>
            </div>
            <div class="table-container">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Firewall Name</th>
                            <th>Rule</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
    '''

    if not rule_results:
        html_content += '''
                        <tr>
                            <td colspan="3" class="text-center">No rules found.</td>
                        </tr>
        '''
    else:
        for result in rule_results:
            for firewall_ip, rule_info in result.items():
                firewall_names = firewall_matches.get(firewall_ip, [])
                for firewall_name in firewall_names:
                    # Split rule details into readable format
                    rule_details = rule_info['rule_name'].strip().split('\n')
                    rule_string = '<br>'.join([f'{detail.strip()}' for detail in rule_details])
                    status_class = "status-allow" if rule_info['status'] == "allow" else "status-deny"
                    html_content += f'''
                    <tr class="{status_class}">
                        <td>{firewall_name}</td>
                        <td class="rule-details">{rule_string}</td>
                        <td>{rule_info['status']}</td>
                    </tr>
                    '''

    html_content += '''
                    </tbody>
                </table>
            </div>
            <div class="close-button">
                <button class="btn btn-danger" onclick="window.close();">Close Window</button>
            </div>
        </div>
    </body>
    </html>
    '''

    with open('firewall_report.html', 'w') as f:
        f.write(html_content)


def firewall_db(src_zone,source,dest_zone, destination,protocol,port):
    firewall_matches = {}
    print(src_zone,source,dest_zone, destination,protocol,port)
    try:
        # Connect to DB and create a cursor
        conn = sqlite3.connect('sql.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM firewall")
        rows = cursor.fetchall()

        for row in rows:
            firewall_name = row[1]
            firewall_ip = row[0]
            zones = row[3].split(",")
            subnets = row[2].split(",")
            # print(subnets)
            for i in range(len(subnets)):
                if subnets[i] == "N/A":
                    continue
                if zones[i].strip() == "":
                    zones[i] = "N/A"
                try:
                    destination_network = ipaddress.ip_network(resolve_fqdn_to_ip(destination), strict=False) if destination != "any" else None
                    source_network = ipaddress.ip_network(resolve_fqdn_to_ip(source), strict=False) if source != "any" else None
                    subnet_network = ipaddress.ip_network(resolve_fqdn_to_ip(subnets[i]), strict=False) if subnets[i] != "any" else None

                    if ((subnet_network and source_network and (subnet_network.subnet_of(source_network) or source_network.subnet_of(subnet_network))) or 
                        (subnet_network and destination_network and (subnet_network.supernet_of(destination_network) or destination_network.subnet_of(subnet_network)))) or \
                        (source == "any" or destination == "any" or subnets[i] == "any"):

                        if firewall_ip not in firewall_matches:
                            firewall_matches[firewall_ip] = []
                        firewall_matches[firewall_ip].append(firewall_name)
                except Exception as e:
                    print(e)
                    continue

    except Exception as e:
        print(e)
        with open("Device_status.txt", "w") as f:
            f.write(f"Error occurred: {e}")
        time.sleep(10)
    finally:
        conn.close()
    print("matched",list(firewall_matches.keys())[0])
    return list(firewall_matches.keys())
    