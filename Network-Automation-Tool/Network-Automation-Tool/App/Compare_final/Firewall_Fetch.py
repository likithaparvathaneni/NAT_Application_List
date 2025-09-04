import time
import xml.etree.ElementTree as ET
from netmiko import ConnectHandler


def parse_system_info(output):
    """Parses system info XML to extract firewall name."""
    try:
        root = ET.fromstring(output)
        firewall_name = root.findtext(".//hostname", "Unknown")
    except ET.ParseError:
        raise RuntimeError("Failed to parse system info XML.")
    return firewall_name


def main(HOST, USERNAME, PASSWORD):
    print(HOST, USERNAME, PASSWORD)
    
    # Define device connection
    device = {
        "device_type": "autodetect",
        "host": HOST,
        "username": USERNAME,
        "password": PASSWORD,
        "timeout": 20,
        "global_delay_factor": 4,
        'session_log': 'session.log'
    }

    try:
        # Establish SSH connection
        conn = ConnectHandler(**device)
        prompt = conn.find_prompt()

        # Disable pagination and set XML output
        conn.send_command("set cli pager off", delay_factor=5)
        conn.send_command("set cli op-command-xml-output on", delay_factor=5)

        # Retrieve system, interface, and routing data
        system_info_output = conn.send_command("show system info", expect_string=r">")
        interface_output = conn.send_command("show interface all", expect_string=r">")
        time.sleep(2)
        routing_output = conn.send_command("show routing fib", expect_string=r">")
        f=open("check.txt","w")
        f.write(routing_output)
        f.close()

        # Open the session log and parse the required information
        with open("session.log", "r") as f:
            contents = f.read().split(prompt)

        for content in contents:
            if "show system info" in content and "<response" in content and "</response>" in content:
                output = content[content.index("<response"):content.index("</response>") + len("</response>")]
                firewall_name = parse_system_info(output)

            # Writing interface data to XML file
            if "show interface all" in content and "<response" in content and "</response>" in content:
                interface_output = content[content.index("<response"):content.index("</response>") + len("</response>")]
                with open(f"Interface_{firewall_name}_{HOST}.xml", 'w') as f:
                    f.write(interface_output)

            # Writing routing data to XML file
            if "show routing fib" in content and "<response" in content and "</response>" in content:
                routing_output = content[content.index("<response"):content.index("</response>") + len("</response>")]
                with open(f"{firewall_name}_{HOST}.xml", 'w') as f:
                    f.write(routing_output)
                print(routing_output)

        return [f"Interface_{firewall_name}_{HOST}.xml", f"{firewall_name}_{HOST}.xml"]

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
