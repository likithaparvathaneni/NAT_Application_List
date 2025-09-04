import sqlite3
from netmiko import ConnectHandler
from datetime import datetime
# Get current timestamp
import time
now = datetime.now()
timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
# Extract date part from timestamp
date = timestamp[:11]
def update_db():
    name = ""
    df = open("host.txt","r")
    devices = []
    for row in df.readlines():
        print(row)
        device = {
            'ip': row.split(",")[0],
            'username': row.split(",")[1],
            'password': row.split(",")[2]
        }
        print(device)
        devices.append(device)
    for device in devices:
        device = {
        "device_type": "autodetect",
        "host": device["ip"],
        "username": device["username"],
        "password": device["password"],
        "timeout": 20,
        "global_delay_factor": 4
    }
        try:
            net_connect = ConnectHandler(**device)
            time.sleep(5)
            prompt = net_connect.find_prompt()
            if prompt[-1]=="#":
                net_connect.send_command("terminal pager 0")
            output = net_connect.send_command("show interface all", expect_string=prompt[-1], read_timeout=20)
            prefix_line=prompt
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
            def parse_interface_output(output):
                interfaces = []
                lines = output.strip().split('\n')  # Skip the header lines
                flag=False
                for line in lines:
                    if "name" in line and "id" in line and "vsys" in line and "zone" in line and "forwarding" in line:
                        flag=True
                    if flag==False or( "name" in line and "id" in line and "zone" in line):
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
                return interfaces
            firewall_map = {}

            interfaces = parse_interface_output(output)
            firewall_map[name] = {
                'ip': device["host"],
                    'interfaces': interfaces,
                }
            # Connect to DB and create a cursor
            conn = sqlite3.connect('sql.db')
            ###print("Connection successful!")

            cursor = conn.cursor()

            # Drop the table if it already exists
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
                cursor.execute(insert_data_query, (data["ip"], name, subnets, zones,date))
                conn.commit()  
        except Exception as e:
             print(e)
update_db()
