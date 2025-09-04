import pymssql
import subprocess
import ipaddress

import ipaddress
import socket
def firewall_db(source,destination,port):
    print(source,destination)
    def resolve_fqdn_to_ip(fqdn):
        try:
            ip_addresses = socket.gethostbyname_ex(fqdn)[2]
            return ip_addresses[0]
        except socket.gaierror as e:
            print(f"Error resolving FQDN {fqdn}: {e}")
            return fqdn
    # def get_traceroute(destination_ip):
    #     try:
    #         result = subprocess.run(["traceroute", destination_ip], capture_output=True, text=True)
    #         if result.returncode == 0:
    #             return result.stdout
    #         else:
    #             return f"Error: {result.stderr}"
    #     except Exception as e:
    #         return f"An exception occurred: {e}"

    # print(get_traceroute("8.8.8.8"))

    # panorama_output = """
    # Serial Number: 0123456789
    # Name: Firewall1
    # IP Address: 192.168.1.1
    # Model: PA-220

    # Serial Number: 9876543210
    # Name: Firewall2
    # IP Address: 192.168.1.2
    # Model: PA-820
    # """

    # default_group_output = """
    # Firewall1 default group: Group1
    # Firewall2 default group: Group2
    # """

    # firewall1_interface_output = """
    # name                id    vsys zone             forwarding               tag    address                                         
    # ------------------- ----- ---- ---------------- ------------------------ ------ ------------------
    # ethernet1/1         69    1    OutssddsideToSP      vr:default               0      19.168.1.1/24    
    # ethernet1/2         77    1    InsideToCore     vr:default               0      192.18.2.1/24    
    # ethernet1/3         83    0                     ha                       0      N/A               
    # ae1                 16    1                     vr:default               0      N/A
    # ae1.978             141   1    OutssddsideToSP vr:default               978    1.67.18.2/23     
    # ae1.gt979             142   1    OutssddsideToSP vr:default               979    10.67.20.2/22     
    # ae1.ds980             143   1    OutssddsideToSP vr:default               980    1.67.24.2/23     
    # ae1dss.981             144   1    OutssddsideToSP        vr:default               981    10.67.100.2/24    
    # ae1.s982             145   1    OutssddsideToSP           vr:default               982    10.67.26.2/24     
    # ae1.ss983             146   1    dsfNova             vr:default               983    10.67.28.2/24     
    # ae1.s984             147   1    BYOD             vr:default               984    20.67.30.2/23     
    # ae1.s986             148   1    Swisslog         vr:default               986    3.67.50.2/24     
    # ae1.9s92             149   1    PACS             vr:default               992    40.64.242.2/24    
    # ae1.13ssa05            150   1    Tablo            vr:default               1305   70.67.57.2/27     
    # ae1.ZAS1329            151   1    InsideToCore          vr:default               1329   10.67.34.2/25     
    # ae1.1sas335            152   1    Natus            vr:default               1335   170.67.224.2/26    
    # ae1.1378            153   1    Getwell          vr:default               1378   10.67.1596.2/23    
    # ae1.1389            154   1    Vyaire           vr:default               1389   10.67.551.2/27     
    # ae1.14fd10            155   1    UDEV-IF-PUMP     vr:default               1410   10.647.120.2/23    
    # ae1.14ssa11            156   1    UDEV-PT-MONITOR  vr:default               1411   10.637.122.2/23    
    # ae1.14asd12            157   1    UDEV-NURSE-CALL  vr:default               1412   10.637.124.2/25    
    # ae1.14dsa13            158   1    OutssddsideToSP    vr:default               1413   103.67.124.130/26  
    # ae1.14dssd14            159   1    OutssddsideToSP        vr:default               1414   102.67.124.194/26  
    # ae1.1415            160   1     OutssddsideToSP       vr:default               1415   10.67.125.162/27  
    # ae1.14sd16            161   1    OutssddsideToSP         vr:default               1416   10.67.125.2/26    
    # ae1.1417            162   1    OutssddsideToSP vr:default               1417   10.67.125.66/27   
    # ae1.14ds18            163   1    OutssddsideToSP vr:default               1418   10.67.125.98/27   
    # ae1.1sd419            164   1    OutssddsideToSP        vr:default               1419   10.67.125.130/27  
    # ae1.1460            128   1    OutsideToSP      vr:default               1460   100.624.0.2/29     
    # ae1.1461            130   1    OutsideToSP      vr:default               1461   N/A               
    # ae1.1d462            129   1    InsideToCore     vr:default               1462   100.634.0.33/29    
    # ae1.1465            131   1    InsideToCore     vr:default               1465   N/A               
    # ae8                 23    0                     ha                       0      N/A               
    # ha1-a               5     0                     ha                       0      198.51.100.1/30   
    # ha1-b               7     0                     ha                       0      198.51.100.5/30   
    # vlfdsan                1     1                     N/A                      0      N/A               
    # lofdsopback            3     1                     N/A                      0      N/A               
    # tunfdsnel              4     1                     N/A                      0      N/A               
    # hscsdfi                8     0                     N/A                      0      N/A               
    # """

    # firewall2_interface_output = """
    # name                id    vsys zone             forwarding               tag    address                                         
    # ------------------- ----- ---- ---------------- ------------------------ ------ ------------------
    # ethernet1/6         69    1    OutsideToSP      vr:default               0      192.168.3.1/24    
    # ethernet1/14        77    1    InsideToCore     vr:default               0      192.168.4.1/24    
    # ethernet1/20        83    0                     ha                       0      N/A               
    # ae1                 16    1                     vr:default               0      N/A
    # """

    # def parse_panorama_output(output):
    #     firewalls = []
    #     lines = output.strip().split('\n')
    #     firewall = {}
        
    #     for line in lines:
    #         if line.startswith('Serial Number:'):
    #             if firewall:
    #                 firewalls.append(firewall)
    #                 firewall = {}
    #             firewall['serial'] = line.split(': ')[1]
    #         elif line.startswith('Name:'):
    #             firewall['name'] = line.split(': ')[1]
    #         elif line.startswith('IP Address:'):
    #             firewall['ip'] = line.split(': ')[1]
    #         elif line.startswith('Model:'):
    #             firewall['model'] = line.split(': ')[1]
        
    #     if firewall:
    #         firewalls.append(firewall)
        
    #     return firewalls

    # def parse_default_group_output(output):
    #     default_groups = {}
    #     lines = output.strip().split('\n')
        
    #     for line in lines:
    #         parts = line.split(' default group: ')
    #         if len(parts) == 2:
    #             default_groups[parts[0]] = parts[1]
        
    #     return default_groups

    # def parse_interface_output(output):
    #     interfaces = []
    #     lines = output.strip().split('\n')[2:]  # Skip the header lines
        
    #     for line in lines:
    #         parts = line.split()
    #         if len(parts) >= 7:
    #             interfaces.append({
    #                 'name': parts[0],
    #                 'id': parts[1],
    #                 'vsys': parts[2],
    #                 'zone': parts[3],
    #                 'forwarding': parts[4],
    #                 'tag': parts[5],
    #                 'address': parts[6],
    #             })
    #         else:
    #             interfaces.append({
    #                 'name': parts[0],
    #                 'id': parts[1],
    #                 'vsys': parts[2],
    #                 'zone': "",
    #                 'forwarding': parts[3],
    #                 'tag': parts[4],
    #                 'address': parts[5],
    #             })

    #     print(interfaces)
    #     return interfaces

    # def fetch_firewall_interface_output(firewall_name):
    #     if firewall_name == 'Firewall1':
    #         return firewall1_interface_output
    #     elif firewall_name == 'Firewall2':
    #         return firewall2_interface_output
    #     return ""

    # # Extract firewall and interface data
    # firewalls = parse_panorama_output(panorama_output)
    # default_groups = parse_default_group_output(default_group_output)

    # firewall_map = {}

    # for firewall in firewalls:
    #     name = firewall['name']
    #     interface_output = fetch_firewall_interface_output(name)
    #     interfaces = parse_interface_output(interface_output)
    #     firewall_map[name] = {
    #         'ip': firewall['ip'],
    #         'default_group': default_groups.get(name, 'Unknown'),
    #         'interfaces': interfaces
    #     }

    # Connect to the database
    server = 'networkops-dbs.database.windows.net'
    database = 'networkops-db'
    username = 'sqladmin'
    password = 'M@sterAcc3ss'

    try:
        conn = pymssql.connect(
            server=server,
            user=username,
            password=password,
            database=database,
            as_dict=True,
            port=1433,
            tds_version='7.4',
            timeout=30
        )
        print("Connection successful!")

        cursor = conn.cursor()

        # # Drop the table if it already exists
        # cursor.execute("IF OBJECT_ID('firewall', 'U') IS NOT NULL DROP TABLE firewall")

        # # Create table with the new schema
        # create_table_query = '''
        # CREATE TABLE firewall (
        #     FIREWALL_IP NVARCHAR(15) PRIMARY KEY,
        #     NAME NVARCHAR(50) NOT NULL,
        #     SUBNETS NVARCHAR(MAX) NOT NULL,
        #     ZONES NVARCHAR(MAX) NOT NULL,
        #     DEFAULT_GROUP NVARCHAR(50) NOT NULL
        # )
        # '''
        # cursor.execute(create_table_query)
        # print("Table created successfully!")

        # Check if the table 'firewall' is empty before inserting data
        # cursor.execute("SELECT COUNT(*) as count FROM firewall")
        # count = cursor.fetchone()['count']

        # if count == 0:
        #     for name, data in firewall_map.items():
        #         subnets = ','.join([iface['address'] for iface in data['interfaces']])
        #         zones = ','.join([iface['zone'] for iface in data['interfaces']])
        #         insert_data_query = '''
        #         INSERT INTO firewall (FIREWALL_IP, NAME, SUBNETS, ZONES, DEFAULT_GROUP) VALUES (%s, %s, %s, %s, %s)
        #         '''
        #         cursor.execute(insert_data_query, (data['ip'], name, subnets, zones, data['default_group']))
        #     print("Data inserted successfully!")

        #     # Commit the transaction
        #     conn.commit()

        # Retrieve all data from the firewall table
        cursor.execute("SELECT * FROM firewall")
        rows = cursor.fetchall()
        # Check if any interface matches the destination IP
        destination_ip = "192.168.1.100"
        destination_ip = resolve_fqdn_to_ip(destination_ip)
        destination_network = ipaddress.ip_network(destination_ip, strict=False)
        for row in rows:
            subnets = row['SUBNETS'].split(',')
            zones = row['ZONES'].split(',')
            n = len(subnets)
            firewall_found=set()
            for i in range(n):
                if subnets[i].lower() != 'n/a':
                    rule_network = ipaddress.ip_network(subnets[i],False)
                    if destination_network.subnet_of(rule_network) or destination_network.supernet_of(rule_network) or rule_network.subnet_of(destination_network) or rule_network.supernet_of(destination_network):
                        firewall_found.add(row['NAME'])
                        break
            else:
                print("Not found")
            print(firewall_found)

    except Exception as e:
        print(2)
        print(e)
    finally:
        # Close the database connection
        conn.close()
    # Raw firewall rules output
    raw_rules = """
    Global_BGP; index: 1" {

            from Fromzone;

            source 1.1.1.1/23

            source-region none;

            to ToZone;

            destination 2.2.2.2/28;

            destination-region none;

            user any;

            source-device any;

            destination-device any;

            category any;

            application/service [0:bgp/tcp/any/179 1:bgp/udp/any/179 2:ping/icmp/any/any ];

            action allow;

            icmp-unreachable: no

            terminal yes;

    }
    Global_DGP; index: 1" {

            from Fromzone;

            source 1.2.1.1/23

            source-region in;

            to ToZone;

            destination 2.2.2.2/28;

            destination-region none;

            user any;

            source-device any;

            destination-device any;

            category any;

            application/service [0:bgp/tcp/any/179 1:bgp/udp/any/179 2:ping/icmp/any/any ];

            action deny;

            icmp-unreachable: no

            terminal yes;

    }
    
    """
    from copy import deepcopy
    def parse_firewall_rules(raw_rules):
        rules = []
        current_rule = None
        rules=[]
        current_rule={
            "name":"",
            "source":"",
            "destination":"",
            "action":"" 
            }
        for line in raw_rules.strip().split('\n'):
            if not current_rule["name"] and  "{" in line:
                current_rule["name"] =line[:line.index(";")]
            if not current_rule["source"]  and  "source" in line:
                current_rule["source"] =line[line.index("source")+6:].strip()
            if not current_rule["destination"] and  "destination" in line:
                current_rule["destination"] =line[line.index("destination")+11:].strip()
            if not current_rule["action"]  and  "action" in line:
                current_rule["action"]=line[line.index("action")+6:].strip()
            if "}" in line:
                rules.append(deepcopy(current_rule))
                current_rule["name"]=""
                current_rule["action"]=""
                current_rule["source"]=""
                current_rule["destination"]=""

            
        return rules

    def check_if_rule_exists(src, dest, rules):
        for rule in rules:
            try:
                if dest!="any":
                    destination_network=ipaddress.ip_network(resolve_fqdn_to_ip(dest),strict=False)
                if src!="any":
                    source_network=ipaddress.ip_network(resolve_fqdn_to_ip(src),strict=False)
                if rule["source"]!="any":
                    rule["source"]=ipaddress.ip_network(resolve_fqdn_to_ip(rule["source"]),False)
                if rule["destination"]!="any":
                    rule["destination"]=ipaddress.ip_network(resolve_fqdn_to_ip(rule["destination"]),False)
                if (rule["source"]=="any" or src=="any" or rule["source"].subnet_of(source_network) or rule["source"].supernet_of(source_network) or source_network.subnet_of(rule["source"])) and( rule["destination"]=="any" or dest=="any" or  destination_network.supernet_of(rule["destination"]) or destination_network.subnet_of(rule["destination"]) or rule["destination"].supernet_of(destination_network) or destination_network.subnet_of(rule_network) ):
                    return True,rule["name"]
            except Exception as e:
                print(e)
        return False, None

    # Parse the rules from the raw output
    firewall_rules = parse_firewall_rules(raw_rules)
    rule_exists, rule_name = check_if_rule_exists(source, destination, firewall_rules)

    if rule_exists:
        print(f"The source '{source}' and destination '{destination}' share the rule '{rule_name}'.")
    else:
        print(f"No common rule found for the source '{source}' and destination '{destination}'.")
