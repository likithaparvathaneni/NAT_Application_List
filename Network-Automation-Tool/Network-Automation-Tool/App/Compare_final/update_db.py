import sqlite3
import pandas as pd
from netmiko import ConnectHandler
import time
# Get current timestamp
from datetime import datetime
now = datetime.now()
timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
 
# Extract date part from timestamp
date = timestamp[:11]
def update_db(db):
    name = ""
    df = open("host.txt","r")
    devices = []

    # Collect device details from the Excel file
    for row in df.readlines():
        if row[0].split(",") not in db:
            continue
        device = {
            'ip': row.split(",")[0],
            'username': row.split(",")[1],
            'password': row.split(",")[2]
        }
        devices.append(device)

    firewall_map = {}

    for device in devices:
        device_params = {
            "device_type": "autodetect",
            "host": device["ip"],
            "username": device["username"],
            "password": device["password"],
            "timeout": 20,
            "global_delay_factor": 4
        }
        try:
            net_connect = ConnectHandler(**device_params)
            time.sleep(5)
            prompt = net_connect.find_prompt()
            if prompt[-1] == "#":
                net_connect.send_command("terminal pager 0")
            output = net_connect.send_command("show interfaces all", expect_string=prompt[-1], read_timeout=20)
            prefix_line = prompt

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
                flag = False
                for line in lines:
                    if "name" in line and "id" in line and "vsys" in line and "zone" in line and "forwarding" in line:
                        flag = True
                    if not flag or ("name" in line and "id" in line and "zone" in line):
                        continue
                    if "-" in line and line.count("-") >= 4:
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

            interfaces = parse_interface_output(output)
            firewall_map[name] = {
                'ip': device["host"],
                'interfaces': interfaces
            }
        except Exception as e:
            print(f"Failed to process device {device['ip']}: {e}")
            continue

    try:
        # Connect to DB and create a cursor
        conn = sqlite3.connect('sql.db')
        cursor = conn.cursor()

        # Create table with the new schema if it doesn't exist
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
            
            # Check if the record exists
            cursor.execute("SELECT COUNT(*) FROM firewall WHERE FIREWALL_IP = ?", (data['ip'],))
            record_exists = cursor.fetchone()[0]

            if record_exists:
                # Update existing record
                update_data_query = '''
                    UPDATE firewall
                    SET NAME = ?, SUBNETS = ?, ZONES = ?, DATE= ?
                    WHERE FIREWALL_IP = ?
                '''
                cursor.execute(update_data_query, (name, subnets, zones,date, data['ip']))
            else:
                # Insert new record
                insert_data_query = '''
                    INSERT INTO firewall (FIREWALL_IP, NAME, SUBNETS, ZONES,DATE)
                    VALUES (?, ?, ?, ?,?)
                '''
                cursor.execute(insert_data_query, (data['ip'], name, subnets, zones,date))
        
        # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()

# Example usage
db = ["192.168.1.1", "192.168.1.2"]  # Example list of IPs to check
update_db(db)
