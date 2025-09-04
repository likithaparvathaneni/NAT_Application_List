import os
import sqlite3
import xml.etree.ElementTree as ET

# Database and table name constants
DATABASE = r"C:\Users\adminuser\Downloads\Network-Automation-Tool\Network-Automation-Tool\App\subnets.db"
TABLE_NAME = "subnets"

# Function to parse the firewall name and IP from the filename
def parse_filename(filename):
    print(filename)
    name, _ = os.path.splitext(filename)
    parts = name.rsplit("_", 1)  # Split into two parts, firewall_name and firewall_ip
    if len(parts) == 2:
        firewall_name, firewall_ip = parts
        print(firewall_name,firewall_ip)
        return firewall_name, firewall_ip
    else:
        raise ValueError(f"Invalid filename format: {filename}. Expected format: 'name_ip.xml'")

# Function to insert data into the database
def save_to_database(firewall_name, firewall_ip, data):
    os.chmod(DATABASE, 0o666)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    print("hello")
    # Create the table with all required columns
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        
            firewall_ip TEXT NOT NULL,
            firewall_name TEXT NOT NULL,
            virtual_router TEXT,
            destination TEXT NOT NULL,
            nexthop TEXT,
            metric INTEGER,
            flags TEXT,
            age INTEGER,
            interface TEXT,
            route_table TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("DELETE FROM subnets WHERE firewall_name = ?", (firewall_name,))
    # cursor.execute("DELETE FROM interfaces WHERE firewall_name = ?", (firewall_name,))
    for entry in data:
        cursor.execute(f"""
            INSERT OR Replace INTO {TABLE_NAME} (
                firewall_ip, firewall_name, virtual_router, destination, nexthop, metric,
                flags, age, interface, route_table
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            firewall_ip, firewall_name, entry['virtual_router'], entry['destination'], 
            entry['nexthop'], entry['metric'], entry['flags'], entry['age'], 
            entry['interface'], entry['route_table']
        ))

    conn.commit()
    conn.close()

# Main function to process an XML file
def process_xml(file_path):
    filename = os.path.basename(file_path)
    firewall_name, firewall_ip = parse_filename(filename)

    data = []

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Navigate to the <result> element
    result = root.find("./result")
    if result is None:
        print(f"No <result> element found in file: {file_path}")
        return

    fibs = result.find("./fibs")
    if fibs is None:
        print(f"No <fibs> element found in file: {file_path}")
        return

    # Iterate through each FIB <entry>
    for fib_entry in fibs.findall("./entry"):
        vr = fib_entry.findtext("vr")  # Virtual router
        route_table = fib_entry.findtext("id")  # Optional: maybe treat as route table id
        
        entries_container = fib_entry.find("./entries")
        if entries_container is None:
            continue

        for route_entry in entries_container.findall("./entry"):
            record = {
                "virtual_router": vr,
                "destination": route_entry.findtext("dst"),
                "nexthop": route_entry.findtext("nexthop"),
                "metric": 0,  # Not present in this structure; set default
                "flags": route_entry.findtext("flags"),
                "age": 0,  # Not present; default to 0
                "interface": route_entry.findtext("interface"),
                "route_table": route_table
            }
            print(record)
            data.append(record)

    if not data:
        print(f"No valid entries found in file: {file_path}")
        return

    # Save parsed data to the database
    save_to_database(firewall_name, firewall_ip, data)


# Script execution entry point
def main(file_name):

    print(file_name)
    if file_name.endswith(".xml") and not file_name.startswith("Interface"):
        file_path = file_name
        print("hello",file_name)
        try:
            process_xml(file_path)
            # os.remove(file_path)
            print(f"Processed file: {file_name}")
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")