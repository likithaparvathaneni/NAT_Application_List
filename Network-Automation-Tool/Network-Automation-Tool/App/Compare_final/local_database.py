import subprocess
import ipaddress
import sqlite3
import ipaddress
import socket
import pandas as pd
import re
import datetime
def firewall_db(source,destination,src_zone,dest_zone,protocol,port):
    ###print(source,destination)
    def resolve_port(port):
         if not port.isnumeric() and port!="any":
            df=pd.read_excel("palo_alto_services_30.xlsx")
            for ind in range(len(df)):
                row=df.iloc[ind]
                if row["Service"].lower()==port.lower():
                    return row["Port"]
            else:
                #print("invalid port ")
                return
         return port
    
    port=resolve_port(port)
    #print("port",port,protocol)
    def resolve_fqdn_to_ip(fqdn):
        try:
            ip_addresses = socket.gethostbyname_ex(fqdn)[2]
            return ip_addresses[0]
        except socket.gaierror as e:
            ###print(f"Error resolving FQDN {fqdn}: {e}")
            return fqdn
    def get_traceroute(destination_ip):
        try:
            result = subprocess.run(["traceroute", destination_ip], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"An exception occurred: {e}"

    ###print(get_traceroute("8.8.8.8"))

    firewall1_interface_output = """
    gicadmin@APO-NFM-wDASSAsfdMDF-0322_Primary(active-primary)> show 
gicadmin@APO-NFW-PMDF-02_Primary(active-primary)> show interface all
total configured hardware interfaces: 15

name                    id    speed/duplex/state            mac address       
--------------------------------------------------------------------------------
ethernet1/5             68    10000/full/up                 5c:58:e6:80:4e:44 
ethernet1/6             69    10000/full/up                 5c:58:e6:80:4e:45 
ethernet1/13            76    10000/full/up                 5c:58:e6:80:4e:4c 
ethernet1/14            77    10000/full/up                 5c:58:e6:80:4e:4d 
ethernet1/20            83    10000/full/up                 5c:58:e6:80:4e:53 
ethernet1/21            84    40000/full/up                 5c:58:e6:80:4e:54 
ethernet1/22            85    40000/full/up                 5c:58:e6:80:4e:55 
ae1                     16    [n/a]/[n/a]/up                5c:58:e6:80:4e:10 
ae8                     23    [n/a]/[n/a]/up                5c:58:e6:80:4e:17 
ha1-a                   5     1000/full/up                  08:66:1f:05:38:7d 
ha1-b                   7     1000/full/up                  08:66:1f:05:38:7e 
vlan                    1     [n/a]/[n/a]/up                5c:58:e6:80:4e:01 
loopback                3     [n/a]/[n/a]/up                5c:58:e6:80:4e:03 
tunnel                  4     [n/a]/[n/a]/up                5c:58:e6:80:4e:04 
hsci                    8     40000/full/up                 5c:58:e6:80:4e:08 

aggregation groups: 2
ae1 members:
  ethernet1/5 ethernet1/13 
ae8 members:
  ethernet1/21 ethernet1/22 
total configured logical interfaces: 48

name                id    vsys zone             forwarding               tag    address                                         
------------------- ----- ---- ---------------- ------------------------ ------ ------------------
ethernet1/6         69    1    OutsideToSP      vr:default               0      100.64.0.18/29    
ethernet1/14        77    1    InsideToCore     vr:default               0      100.64.0.41/29    
ethernet1/20        83    0                     ha                       0      N/A               
ae1                 16    1                     vr:default               0      N/A               
ae1.751             132   1    Galvanon         vr:default               751    10.67.204.2/23    
ae1.756             133   1    NurseCall        vr:default               756    10.67.222.2/23    
ae1.970             134   1    Biomed1          vr:default               970    10.67.10.2/24     
ae1.971             135   1    Biomed2          vr:default               971    10.67.11.2/24     
ae1.972             136   1    Biomed3          vr:default               972    10.67.12.2/24     
ae1.973             137   1    Cerner           vr:default               973    10.67.13.2/24     
ae1.974             138   1    BioCareAware     vr:default               974    10.67.14.2/24     
ae1.975             139   1    Pyxis_BD         vr:default               975    10.67.15.2/24     
ae1.976             140   1    PCI              vr:default               976    10.67.16.2/24     
ae1.978             141   1    Philips_Surveill vr:default               978    10.67.18.2/23     
ae1.979             142   1    Philips_Telemetr vr:default               979    10.67.20.2/22     
ae1.980             143   1    Philips_Bedsides vr:default               980    10.67.24.2/23     
ae1.981             144   1    TimeClock        vr:default               981    10.67.100.2/24    
ae1.982             145   1    BACNet           vr:default               982    10.67.26.2/24     
ae1.983             146   1    Nova             vr:default               983    10.67.28.2/24     
ae1.984             147   1    BYOD             vr:default               984    10.67.30.2/23     
ae1.986             148   1    Swisslog         vr:default               986    10.67.50.2/24     
ae1.992             149   1    PACS             vr:default               992    10.64.242.2/24    
ae1.1305            150   1    Tablo            vr:default               1305   10.67.57.2/27     
ae1.1329            151   1    EAP_PCI          vr:default               1329   10.67.34.2/25     
ae1.1335            152   1    Natus            vr:default               1335   10.67.224.2/26    
ae1.1378            153   1    Getwell          vr:default               1378   10.67.196.2/23    
ae1.1389            154   1    Vyaire           vr:default               1389   10.67.51.2/27     
ae1.1410            155   1    UDEV-IF-PUMP     vr:default               1410   10.67.120.2/23    
ae1.1411            156   1    UDEV-PT-MONITOR  vr:default               1411   10.67.122.2/23    
ae1.1412            157   1    UDEV-NURSE-CALL  vr:default               1412   10.67.124.2/25    
ae1.1413            158   1    UDEV-POC-DIAG    vr:default               1413   10.67.124.130/26  
ae1.1414            159   1    UDEV-MDS         vr:default               1414   10.67.124.194/26  
ae1.1415            160   1    UDEV-PACS        vr:default               1415   10.67.125.162/27  
ae1.1416            161   1    UDEV-PTS         vr:default               1416   10.67.125.2/26    
ae1.1417            162   1    UDEV-ULTRASOUNDS vr:default               1417   10.67.125.66/27   
ae1.1418            163   1    UDEV-MEDIA-WRITE vr:default               1418   10.67.125.98/27   
ae1.1419            164   1    UDEV-ECG         vr:default               1419   10.67.125.130/27  
ae1.1460            128   1    OutsideToSP      vr:default               1460   100.64.0.2/29     
ae1.1461            130   1    OutsideToSP      vr:default               1461   N/A               
ae1.1462            129   1    InsideToCore     vr:default               1462   100.64.0.33/29    
ae1.1465            131   1    InsideToCore     vr:default               1465   N/A               
ae8                 23    0                     ha                       0      N/A               
ha1-a               5     0                     ha                       0      198.51.100.1/30   
ha1-b               7     0                     ha                       0      198.51.100.5/30   
vlan                1     1                     N/A                      0      N/A               
loopback            3     1                     N/A                      0      N/A               
tunnel              4     1                     N/A                      0      N/A               
hsci                8     0                     N/A                      0      N/A               
"""
    name = ""
    lines = firewall1_interface_output.strip().split('\n')
    prefix_line=lines[0]
    if ">" in prefix_line:
        if "@" in prefix_line and "(" in prefix_line:
                name = prefix_line[prefix_line.index("@") + 1:prefix_line.index("(")]
        elif "@" in prefix_line:
                name = prefix_line[prefix_line.index("@") + 1:]
        else:
                name = prefix_line[:prefix_line.index(">")]
    elif "#" in prefix_line:
            name = prefix_line[:prefix_line.index("#")]
    else:
        name = prefix_line
    from faker import Faker

    # Initialize Faker object
    fake = Faker()
    name=fake.name()
    def parse_interface_output(output):
        interfaces = []
        lines = output.strip().split('\n')[2:]  # Skip the header lines
        flag=False
        for line in lines:
            if "name" in line and "id" in line and "vsys" in line and "zone" in line and "forwarding" in line:
                flag=True
            if flag==False or "name" in line and "id" in line and "zone" in line:
                continue
            if "-" in line and line.count("-")>=4:
                continue
            parts = line.split()
            if len(parts) >= 7:
                interfaces.append({
                    'name': parts[0],
                    'id': parts[1],
                    'vsys': parts[2],
                    'zone': parts[3],
                    'forwarding': parts[4],
                    'tag': parts[5],
                    'address': parts[6],
                })
            else:
                interfaces.append({
                    'name': parts[0],
                    'id': parts[1],
                    'vsys': parts[2],
                    'zone': "",
                    'forwarding': parts[3],
                    'tag': parts[4],
                    'address': parts[5],
                })

        ###print(interfaces)
        return interfaces

    # Extract firewall and interface data
    firewalls = name

    firewall_map = {}

    interfaces = parse_interface_output(firewall1_interface_output)
    firewall_map[name] = {
        'ip': "ip3",
            'interfaces': interfaces
        }

    try:
        # Connect to DB and create a cursor
        conn = sqlite3.connect('sql.db')
        ###print("Connection successful!")

        cursor = conn.cursor()

        # Drop the table if it already exists
        cursor.execute("DROP TABLE IF EXISTS firewall")
 
        # Create table with the new schema
        # Create table with the new schema
        cursor.execute("DROP TABLE IF EXISTS firewall")

        # Create table with the new schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS firewall (
                FIREWALL_IP TEXT PRIMARY KEY NOT NULL,
                NAME TEXT NOT NULL,
                SUBNETS TEXT NOT NULL,
                ZONES TEXT NOT NULL,
                DATE TEXT NOT NULL
            )
        ''')
        for name, data in firewall_map.items():
            subnets = ','.join([iface['address'] for iface in data['interfaces']])
            zones = ','.join([iface['zone'] for iface in data['interfaces']])
            insert_data_query = '''
                INSERT INTO firewall (FIREWALL_IP, NAME, SUBNETS, ZONES,DATE) VALUES (?, ?, ?, ?,?)
                '''
            # ##print(name,data)
            #print(name)
            now = datetime.now()
            timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
            
            # Extract date part from timestamp
            date = timestamp[:11]
            cursor.execute(insert_data_query, ("ip"+str(i+1), name, subnets, zones,date))

        # Retrieve all data from the firewall table
        cursor.execute("SELECT * FROM firewall")
        rows = cursor.fetchall()
        # Check if any interface matches the destination IP
        destination_ip = "192.168.1.100"
        destination_ip = resolve_fqdn_to_ip(destination_ip)
        destination_network = ipaddress.ip_network(destination_ip, strict=False)
        for row in rows:
            name=row[1]
            ip=row[0]
            zones=row[3]
            zones=zones.split(",")
            subnets=row[2]
            subnets=subnets.split(",")
            n = len(subnets)
            firewall_flag=False
            for i in range(n):
                if subnets[i]=="N/A":
                    continue
                # ##print(subnets[i],source,destination)
                if zones[i].strip()=="":
                    zones[i]="N/A"
                if destination!="any":
                    destination_network=ipaddress.ip_network(resolve_fqdn_to_ip(destination),strict=False)
                if source!="any":
                    source_network=ipaddress.ip_network(resolve_fqdn_to_ip(source),strict=False)
                if subnets[i]!="any":
                    subnets[i]=ipaddress.ip_network(resolve_fqdn_to_ip(subnets[i]),False)
                if (subnets[i]=="any" or source=="any" or subnets[i].subnet_of(source_network) or subnets[i].supernet_of(source_network) or source_network.subnet_of(subnets[i])) or (  destination=="any" or  destination_network.supernet_of(subnets[i]) or destination_network.subnet_of(subnets[i]) or subnets[i].supernet_of(destination_network) or destination_network.subnet_of(subnets[i]) ):
                    ##print("name",name,"ip",ip,"zone",zones[i],"subnets",subnets[i])
                    firewall_flag=True
            ###print(firewall_found)
            if not firewall_flag:
                print("Not found")
            


    except Exception as e:
        pass
        ###print(2)
        ##print(e)
    finally:
        # Close the database connection
        conn.close()
    # Raw firewall rules output
    raw_rules = """
    Global_Rule_1; index: 1" {

    from ZoneA;

    source 10.0.0.1/24;

    source-region US-East;

    to ZoneB;

    destination 192.168.1.1/24;

    destination-region US-West;

    user admin;

    source-device server1;

    destination-device server2;

    category web;

    application/service [0:http/tcp/any/80 1:https/tcp/any/443 ];

    action deny;

    icmp-unreachable: yes;

    terminal no;

}

Global_Rule_2; index: 2" {

    from ZoneB;

    source 10.0.1.0/24;

    source-region Europe;

    to ZoneC;

    destination 172.16.0.0/16;

    destination-region Asia;

    user guest;

    source-device laptop;

    destination-device ##printer;

    category email;

    application/service [0:smtp/tcp/any/25 1:imap/tcp/any/143 ];

    action allow;

    icmp-unreachable: no;

    terminal yes;

}

Global_Rule_3; index: 3" {

    from ZoneC;

    source 192.168.10.0/24;

    source-region South-America;

    to ZoneA;

    destination 10.1.1.1/32;

    destination-region North-America;

    user user123;

    source-device workstation;

    destination-device firewall;

    category ftp;

    application/service [0:ftp/tcp/any/21 ];

    action allow;

    icmp-unreachable: no;

    terminal yes;

}

Global_Rule_4; index: 4" {

    from ZoneD;

    source 172.16.1.0/24;

    source-region Asia;

    to ZoneE;

    destination 10.0.0.0/8;

    destination-region Europe;

    user any;

    source-device any;

    destination-device any;

    category vpn;

    application/service [0:vpn/tcp/any/1194 ];

    action deny;

    icmp-unreachable: yes;

    terminal no;

}

Global_Rule_5; index: 5" {

    from ZoneE;

    source 192.168.0.0/16;

    source-region Africa;

    to ZoneF;

    destination 172.16.0.0/12;

    destination-region South-America;

    user admin;

    source-device router;

    destination-device server;

    category database;

    application/service [0:mysql/tcp/any/3306 ];

    action allow;

    icmp-unreachable: yes;

    terminal yes;

}

Global_Rule_6; index: 6" {

    from ZoneF;

    source 10.10.10.0/24;

    source-region North-America;

    to ZoneG;

    destination 192.168.100.0/24;

    destination-region Asia;

    user employee;

    source-device workstation;

    destination-device switch;

    category internal;

    application/service [0:ldap/tcp/any/389 ];

    action deny;

    icmp-unreachable: no;

    terminal no;

}

Global_Rule_7; index: 7" {

    from ZoneG;

    source 10.0.0.0/8;

    source-region Australia;

    to ZoneH;

    destination 172.16.1.1/32;

    destination-region US-West;

    user support;

    source-device firewall;

    destination-device router;

    category monitoring;

    application/service [0:snmp/udp/any/161 ];

    action allow;

    icmp-unreachable: yes;

    terminal yes;

}

Global_Rule_8; index: 8" {

    from ZoneH;

    source 192.168.1.1/32;

    source-region North-America;

    to ZoneI;

    destination 10.10.0.0/16;

    destination-region Europe;

    user any;

    source-device any;

    destination-device any;

    category voice;

    application/service [0:voip/tcp/any/5060 ];

    action deny;

    icmp-unreachable: no;

    terminal no;

}

Global_Rule_9; index: 9" {

    from ZoneI;

    source 172.16.5.0/24;

    source-region South-America;

    to ZoneJ;

    destination 192.168.2.0/24;

    destination-region Africa;

    user admin;

    source-device server;

    destination-device laptop;

    category remote;

    application/service [0:ssh/tcp/any/22 ];

    action allow;

    icmp-unreachable: yes;

    terminal yes;

}

Global_Rule_10; index: 10" {

    from ZoneJ;

    source 10.0.2.0/24;

    source-region Europe;

    to ZoneA;

    destination 172.16.10.0/24;

    destination-region Asia;

    user any;

    source-device any;

    destination-device any;

    category security;

    application/service [0:udp/any/any/23 ];

    action deny;

    icmp-unreachable: no;

    terminal no;

}  



Global_OSPF-Outbound; index: 6 {
        from InsideToCore;
        source [ 100.64.0.49 100.64.0.41 100.64.0.33 100.64.0.57 ];
        source-region none;
        to InsideToCore;
        destination [ 100.64.0.58 100.64.0.50 100.64.0.42 100.64.0.34 ];
        destination-region none;
        user any;
        source-device any;
        destination-device any;
        category any;
        application/service 0:ospf/89/any/any;
        action allow;
        icmp-unreachable: no
        terminal yes;
}
 Global_SP_PAN_PING; index: 7 {
        from OutsideToSP;
        source [ 100.64.0.9 100.64.0.17 100.64.0.25 100.64.0.1 ];
        source-region none;
        to OutsideToSP;
        destination [ 100.64.0.10 100.64.0.2 100.64.0.18 100.64.0.26 ];
        destination-region none;
        user any;
        source-device any;
        destination-device any;
        category any;
        application/service 0:ping/icmp/any/any;
        action allow;
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
            "src_zone":"",
            "dest_zone":"",
            "action":"" ,
            "application_service":{}
            }
        for line in raw_rules.strip().split('\n'):
            if not current_rule["name"] and  "{" in line:
                current_rule["name"] =line[:line.index(";")].strip()
            if not current_rule["source"]  and  "source" in line:
                new_l=line[line.index("source")+6:len(line)-1].strip()
                if "[" in new_l:
                    new_l=new_l[new_l.index("[")+1:new_l.index("]")]
                    ips=new_l.strip().split()
                else:
                    ips=new_l
                current_rule["source"] =ips
            if not current_rule["destination"] and  "destination" in line:
                current_rule["destination"] =line[line.index("destination")+11:len(line)-1].strip()
            if not current_rule["action"]  and  "action" in line:
                current_rule["action"]=line[line.index("action")+6:len(line)-1].strip()
            if not current_rule["src_zone"] and "from" in line:
                current_rule["src_zone"]=line[line.index("from")+4:len(line)-1].strip()
            if not current_rule["dest_zone"] and "to" in line:
                current_rule["dest_zone"]=line[line.index("to")+2:len(line)-1].strip()
            if not current_rule["application_service"] and "application/service"in line:
            # Use regex to find the last element in square brackets
                line=line[line.index("service")+7:].strip()
                if "[" in line and "]" in line:
                    line_l=line[line.index("[")+1:line.index("]")]
                else:
                    line_l=line
                line_l=line_l.strip().split()
                for l in line_l:
                    sep=l.split("/")
                    #print(sep)
                    if "ospf" in l.lower():
                        current_rule["application_service"]["ospf"]={}
                        current_rule["application_service"]["ospf"][sep[1]]={}
                        continue
                    elif sep[1] not in  current_rule["application_service"]:
                        current_rule["application_service"][sep[1]]={}

                    current_rule["application_service"][sep[1]][sep[3]]={}
            if "}" in line:
                rules.append(deepcopy(current_rule))
                current_rule["name"]=""
                current_rule["action"]=""
                current_rule["source"]=""
                current_rule["destination"]=""
                current_rule["application_service"]={}

        #print(rules)
        return rules
    def check_if_rule_exists(src, dest,src_zone,dest_zone, rules):
        ##print(src, dest,src_zone,dest_zone)
        res=[] 
        for rule in rules:
            if protocol in rule["application_service"]:
                if str(port) not in rule["application_service"][protocol] and "any" not in rule["application_service"][protocol] :
                    continue
                else:
                    print(rule,protocol,port)
            try:
                if dest!="any":
                    destination_network=ipaddress.ip_network(resolve_fqdn_to_ip(dest),strict=False)
                if src!="any":
                    source_network=ipaddress.ip_network(resolve_fqdn_to_ip(src),strict=False)
                if rule["source"]!="any":
                    rule["source"]=ipaddress.ip_network(resolve_fqdn_to_ip(rule["source"]),False)
                if rule["destination"]!="any":
                    rule["destination"]=ipaddress.ip_network(resolve_fqdn_to_ip(rule["destination"]),False)
                # #print(src, dest,src_zone,dest_zone)
                if (rule["source"]=="any" or src=="any" or rule["source"].subnet_of(source_network) or rule["source"].supernet_of(source_network) or source_network.subnet_of(rule["source"])) and( rule["destination"]=="any" or dest=="any" or  destination_network.supernet_of(rule["destination"]) or destination_network.subnet_of(rule["destination"]) or rule["destination"].supernet_of(destination_network) or rule["destination"].subnet_of(destination_network) ) and (src_zone.lower()=="any" or src_zone.strip().lower()==rule["src_zone"].lower() or rule["src_zone"].lower()=="any") and (dest_zone.lower()=="any" or dest_zone.strip().lower()==rule["dest_zone"].lower() or rule["dest_zone"].lower()=="any") :
                    res.append([ True,rule["name"],rule["action"]])
            except Exception as e:
                print(e)
                pass
        res.append([False, None,None])
        return res

    # Parse the rules from the raw output
    firewall_rules = parse_firewall_rules(raw_rules)
    rule_exists = check_if_rule_exists(source, destination,src_zone,dest_zone, firewall_rules)
    for rule_exist in rule_exists:
        # #print(rule_exist)
        if rule_exist[0]:
            print(f"The source '{source}' and destination '{destination}' share the rule '{rule_exist[1]}'. with {rule_exist[2]}")
    for rule in rule_exists:
        if rule[0]:
            break
    else:
        print(f"No common rule found for the source '{source}' and destination '{destination}'.")
firewall_db("10.0.2.0/24","1.23.56.65","fsfg","daad","tcp","http")
# firewall_db("10.0.0.0/8","172.16.1.1/32","any","any","udp","any")
# firewall_db("any","any","any","any","tcp","any")
