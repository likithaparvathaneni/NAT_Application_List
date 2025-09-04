import pandas as pd
import re
import os
# Load CSV file
df = pd.read_csv("applipedia_data_with_onclick_fixed.csv")

# Function to extract the last digit from OnClick
def extract_last_digit(onclick):
    match = re.search(r"ShowApplicationDetail\('\d+', '[^']+', '(\d+)'\)", str(onclick))
    return int(match.group(1)) if match else None

def split_ports(ports):
    if pd.isna(ports) or ports == "N/A" or ports.strip() == "":
        return [], []
    
    protocols = []
    port_numbers = []
    
    # Remove any extra spaces around commas
    # ports = ports.replace(' ', '')
    
    # Split the string based on comma
    port_groups = ports.split(" ")
    
    for group in port_groups:
        # Check if the group has both protocol and port(s)
        if '/' in group:
            protocol, port_list = group.split('/', 1)
            # Handle case where the port list is 'dynamic'
            if 'dynamic' in port_list:
                protocols.append(protocol)
                port_numbers.append('49152-65535')
                for port in port_list.split(","):
                    if port!='dynamic':
                        port = port.strip()
                        match = re.match(r"(\d+(-\d+)?)", port)
                        if match:
                            protocols.append(protocol)
                            port_numbers.append(match.group(1))
            else:
                for port in port_list.split(","):
                    port = port.strip()
                    match = re.match(r"(\d+(-\d+)?)", port)
                    if match:
                        protocols.append(protocol)
                        port_numbers.append(match.group(1))
    
    return list(set(protocols)), list(set(port_numbers))

# Apply functions
df["OnClick_Last_Digit"] = df["OnClick"].apply(extract_last_digit)
df["Protocol"], df["Ports"] = zip(*df["Standard Ports"].apply(split_ports))

# List to store processed rows
updated_rows = []
temp_rows = []  # Store rows with OnClick = 1 that need filling
accumulated_ports = []
accumulated_protocols = []

for index, row in df.iterrows():
    if row["OnClick_Last_Digit"] == 1:
        # Store row but do not append yet
        temp_rows.append(row)

        # Accumulate ports and protocols
        accumulated_ports.extend(row["Ports"])
        accumulated_protocols.extend(row["Protocol"])

    else:
        if temp_rows:  
            # Apply accumulated data to all stored rows
            for stored_row in temp_rows:
                stored_row["Ports"] = list(set(stored_row["Ports"] + accumulated_ports))
                stored_row["Protocol"] = list(set(stored_row["Protocol"] + accumulated_protocols))

                updated_rows.append(stored_row)  # Add only once

            temp_rows = []  # Reset temp storage
            accumulated_ports = []
            accumulated_protocols = []

        # Add the current row normally
        updated_rows.append(row)

# Convert back to DataFrame
df_updated = pd.DataFrame(updated_rows)

filename = "applipedia_data_cleaned.csv"

# Check if the file exists and remove it
if os.path.exists(filename):
    os.remove(filename)

# Save the DataFrame to a new CSV file
df_updated.to_csv(filename, index=False)

print("✅ Processed CSV saved as 'applipedia_data_cleaned.csv' - All entries properly merged!")
