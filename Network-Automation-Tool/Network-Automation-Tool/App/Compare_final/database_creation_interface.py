import sqlite3
import xml.etree.ElementTree as ET
import re
import os
def main(filepath):
    db_name = "subnets.db"  
    os.chmod(db_name, 0o666)
    # Connect to SQLite database (single connection used for all operations)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create `interfaces` table (updated to include hw info)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interfaces (
        
        firewall_name TEXT NOT NULL,
        firewall_ip TEXT NOT NULL,
        name TEXT NOT NULL,
        interface_id INTEGER NOT NULL,
        type INTEGER,
        mac TEXT,
        speed TEXT,
        duplex TEXT,
        state TEXT,
        mode TEXT,
        st TEXT,
        tag INTEGER,
        vsys INTEGER,
        zone TEXT,
        fwd TEXT,
        ip TEXT,
        hw_id INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        Primary Key(firewall_name,interface_id,zone,ip)
    );
    """)

    # Parse firewall name and IP from filename
    def parse_filename(filename):
        print(filename)
        # cursor.execute("DELETE FROM interfaces WHERE firewall_name = ?", (firewall_name,))
        name, _ = os.path.splitext(filename)
        parts = name.rsplit("_", 1)  # Split into two parts, firewall_name and firewall_ip
        if len(parts) == 2:
            firewall_name, firewall_ip = parts
            print(firewall_name,firewall_ip)
            firewall_name=firewall_name[10:]
            return firewall_name, firewall_ip
        else:
            raise ValueError(f"Invalid filename format: {filename}. Expected format: 'name_ip.xml'")
        

    # Process XML for interfaces
    def process_xml_file(filepath, firewall_name, firewall_ip):
        try:
            cursor.execute("DELETE FROM interfaces WHERE firewall_name = ?", (firewall_name,))
            # Read XML data from the file
            with open(filepath, "r") as file:
                xml_data = file.read()
            
            root = ET.fromstring(xml_data)

            # Find all <entry> elements for interfaces
            for interface in root.findall(".//entry"):
                name = interface.findtext("name", default="")
                zone = interface.findtext("zone", default="")
                fwd = interface.findtext("fwd", default="")
                vsys = interface.findtext("vsys", default="")
                tag = interface.findtext("tag", default="")
                ip = interface.findtext("ip", default="N/A")
                interface_id = interface.findtext("id", default="")
                
                # Insert or update interface data
                cursor.execute("""
                    INSERT OR Replace INTO interfaces (
                        firewall_name, firewall_ip, name, interface_id, zone, fwd, vsys, tag, ip
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (firewall_name, firewall_ip, name, interface_id, zone, fwd, vsys, tag, ip))
                print("inserted")
                # Now process the hardware details under <hw> for this interface
                hw_entry = root.find(f".//hw/entry[name='{name}']")
                if hw_entry is not None:
                    duplex = hw_entry.findtext("duplex", default="")
                    type_ = hw_entry.findtext("type", default="")
                    state = hw_entry.findtext("state", default="")
                    st = hw_entry.findtext("st", default="")
                    mac = hw_entry.findtext("mac", default="")
                    mode = hw_entry.findtext("mode", default="")
                    speed = hw_entry.findtext("speed", default="")
                    hw_id = hw_entry.findtext("id", default="")

                    # Update or insert hardware info in the database for this interface
                    cursor.execute("""
                        UPDATE OR IGNORE interfaces
                        SET mac = ?, speed = ?, duplex = ?, state = ?, mode = ?, hw_id = ?
                        WHERE firewall_name = ? AND firewall_ip = ? AND name = ?
                    """, (mac, speed, duplex, state, mode, hw_id, firewall_name, firewall_ip, name))
            
            print(f"Successfully processed file: {filepath}")

        except (ET.ParseError, sqlite3.Error, Exception) as e:
            print(f"Error processing file {filepath}: {str(e)}")

    firewall_name, firewall_ip = parse_filename(filepath)
    process_xml_file(filepath,firewall_name,firewall_ip)
            

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("All XML files processed successfully.")

