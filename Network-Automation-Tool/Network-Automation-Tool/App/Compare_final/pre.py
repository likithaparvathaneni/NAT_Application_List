from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
import time
from datetime import datetime
import shutil
import os
 
output_file = ""  # Variable to store output file name
log_file = ""     # Variable to store log file name
error_file = ""   # Variable to store error file name
 
# Get current timestamp
now = datetime.now()
timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
 
# Extract date part from timestamp
date = timestamp[:11]
 
# Function to execute commands on a device
def execute_commands(HOST, net_connect, commands):
    global log_file, output_file, error_file
 
    # Generate file names based on date and host
    log_file = date + "log_" + HOST + ".txt"
    log_file=log_file.strip()
    output_file = date + HOST + ".txt"
    output_file=output_file.strip()
    error_file = date + "Error_" + HOST + ".txt"
    error_file=error_file.strip()
 
    # Open output file for writing
    f = open(output_file, "w")
 
    # Iterate through commands
    for command in commands:
        try:
            now = datetime.now()
 
            # Open log file to append
            l_file = open(log_file, "a+")
            timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
            l_file.write(timestamp + "\n")
            l_file.write(f"Executing command: {command}\n")

            # Find prompt and send command
            prompt = net_connect.find_prompt()
            if prompt[-1]=="#":
                net_connect.send_command("terminal pager 0")
            output = net_connect.send_command(command, expect_string=prompt[-1], read_timeout=20)
 
            # Write command and output to output file
            f.write(f"{prompt}{command}\n{output}\n")
 
            # Write success message to log file
            l_file.write(timestamp + "\n")
            l_file.write(f"{command} executed successfully\n")
            l_file.close()
 
        except Exception as e:
            # Write exception details to log file
            l_file = open(log_file, "a+")
            e_file=open(error_file,"a+")
            now = datetime.now()
            timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
            l_file.write(f"{timestamp} - Exception occurred while executing {command}: {str(e)}\n")
            e_file.write(f"{timestamp} - Exception occurred while executing {command}: {str(e)}\n")
            l_file.close()
            e_file.close()
 
    f.close()
 
# Function to establish connection and execute commands
def helper(HOST, USERNAME, PASSWORD, commands):
    global log_file, error_file
 
    # Generate log and error file names
    log_file = date + "log_" + HOST + ".txt"
    error_file = date + "Error_" + HOST + ".txt"
    count=0
    # Define device parameters
    device = {
        "device_type": "autodetect",
        "host": HOST,
        "username": USERNAME,
        "password": PASSWORD,
        "timeout": 20,
        "global_delay_factor": 4
    }
 
    try:
       
        # Open log file for appending
        l_file = open(log_file, "a+")
        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
       
 
        # Connect to the device
        net_connect = ConnectHandler(**device)
        l_file.write(timestamp + "\n")
        l_file.write("Connection Successful.\n")
        l_file.write(timestamp + "\n")
        time.sleep(5)  # Wait for connection to stabilize
        l_file.write("Login Successful\n")
        l_file.close()
 
        # Execute commands
        execute_commands(HOST, net_connect, commands)
       
        net_connect.disconnect()
 
    except NetMikoAuthenticationException as auth_ex:
        # Handle authentication exceptions
        l_file = open(log_file, "a+")
        e_file = open(error_file, "a+")
        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        l_file.write(timestamp + "\n")
        l_file.write("Connection Successful.\n")
        e_file.write(timestamp + "\n")
        e_file.write(f"Failed to authenticate: {auth_ex}\n")
        l_file.write(timestamp + "\n")
        l_file.write("Login failed, due to incorrect credentials.\n")
        l_file.close()
        e_file.close()
       
    except NetMikoTimeoutException as ssh_ex:
        l_file = open(log_file, "a+")
        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        e_file = open(error_file, "a+")
        e_file.write(timestamp + "\n")
        e_file.write(f"SSH Exception occurred: {ssh_ex}\n")
        l_file.write(timestamp + "\n")
        l_file.write(f"Unable to establish SSH connection: {ssh_ex}\n")
        e_file.close()
        l_file.close()
 
    except Exception as ex:
        l_file = open(log_file, "a+")
        e_file = open(error_file, "a+")
        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        e_file.write(timestamp + "\n")
        e_file.write(f"An error occurred: {ex}\n")
        l_file.write(timestamp + "\n")
        l_file.write(f"An error occurred: {ex}\n")
        l_file.close()
        e_file.close()
 
    finally:
        # Close log file
        l_file = open(log_file, "a+")
        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        l_file.write(timestamp + "\n")
        l_file.write("SSH session closed\n")
        l_file.close()
 
# Function to perform pre-checks
def precheck(HOST, USERNAME, PASSWORD):
    # Read precheck commands from file
    commands_file = open("precheck_commands.txt", "r")
    commands = [cmd.strip() for cmd in commands_file.readlines()]
    commands_file.close()
 
    # Call helper function to establish connection and execute commands
    helper(HOST, USERNAME, PASSWORD, commands)
 
# Function to clean output files
def clean(file, prefix_line, commands):
    # Open input and output files
    infile = open(date + file, "r")
    outfile = open("Cleaned" + file, "w")
 
    # Iterate through lines in input file
    for line in infile:
        # Remove special characters
        clean_line = line.replace('[?1h=', '')
 
        # Check if line is not empty and starts with prefix_line
        if line.strip():
            if line.startswith(prefix_line):
                # Check if line ends with any command from precheck_commands
                if line[line.index(prefix_line) + len(prefix_line):].strip() not in commands:
                    continue
                else:
                    clean_line = line
            outfile.write(clean_line)
 
    infile.close()
    outfile.close()
 
# Main function to process hosts and commands
def main(info, precheck_commands):
    count_devices = 0
    count_devices_success = 0
 
    # Read precheck commands from input
    precheck_commands = precheck_commands.read().decode("utf-8").splitlines()
 
    # Remove empty lines from precheck_commands list
    indexes = []
    for i in range(len(precheck_commands) - 1, -1, -1):
        if precheck_commands[i].strip() == "":
            indexes.append(i)
    for i in indexes:
        precheck_commands.pop(i)
 
    new_name_file_l, new_error_l, new_log_l, name_l = [], [], [], []
 
    # Iterate through each line in info
    if precheck_commands != []:
        for line in info:
            if line.strip() == "":
                continue
            count_devices += 1
 
            # Check if line format is correct
            if (not line) or len(line.strip().split(",")) != 3:
                time.sleep(10)
                continue
 
            HOST, USERNAME, PASSWORD = line.strip().split(",")
 
            # Call precheck function to establish connection and execute commands
            helper(HOST, USERNAME, PASSWORD, precheck_commands)
 
            # Generate file names
            log_file = date + "log_" + HOST + ".txt"
            global output_file
            output_file = date + HOST + ".txt"
            global error_file
            error_file = date + "Error_" + HOST + ".txt"
            file_name = date + HOST + ".txt"
            cleaned_host_file = "cleaned" + HOST + ".txt"
 
            # Check if output file exists
            if not os.path.exists(file_name):
                new_name_file_l.append(cleaned_host_file)
                new_error_l.append(error_file)
                new_log_l.append(log_file)
                name_l.append(HOST)
                continue
 
            # Open output file and find prefix line
            file = open(file_name, "r")
            prefix_line = ""
            for line in file.readlines():
                if line.strip() == "":
                    continue
                for command in precheck_commands:
                    if line.strip().endswith(command):
                        prefix_line = line[:line.index(command)]
                        break
            file.close()
 
            # Extract name from prefix_line
            name = ""
            print(prefix_line)
            if ">" in prefix_line:
                if "@" in prefix_line and "(" in prefix_line:
                    name = prefix_line[prefix_line.index("@") + 1:prefix_line.index("(")]
                elif "@" in prefix_line:
                    name = prefix_line[prefix_line.index("@") + 1:]
                else:
                    name=prefix_line
                if ">" in name:
                    name = name[:name.index(">")]
            elif "#" in prefix_line:
                name = prefix_line[:prefix_line.index("#")]
            else:
                name = prefix_line
 
            # Count successful devices
            if name.strip() != "":
                count_devices_success += 1
 
            # Call clean function to clean output file
            clean(HOST + ".txt", prefix_line, precheck_commands)
            cleaned_host_file = "cleaned" + HOST + ".txt"
 
            # Generate new file names
            new_name_file = date + "_" + name + ".txt"
            new_error = date + "_" + "error_" + name + ".txt"
            new_log = date + "_" + "log_" + name + ".txt"
 
            try:
                # Remove existing files and move cleaned_host_file to new_name_file
                if os.path.exists(new_name_file):
                    os.remove(new_name_file)
                if os.path.exists(new_error):
                    os.remove(new_error)
                if os.path.exists(new_log):
                    os.remove(new_log)
                if os.path.exists(cleaned_host_file):
                    shutil.move(cleaned_host_file, new_name_file)
            except:
                pass
 
            # Move error_file and log_file to new_error and new_log respectively
            if os.path.exists(error_file):
                shutil.move(error_file, new_error)
 
            if os.path.exists(log_file):
                shutil.move(log_file, new_log)
 
            # Remove HOST.txt
            if os.path.exists(HOST + ".txt"):
                os.remove(HOST + ".txt")
 
            # Append new file names to respective lists
            new_name_file_l.append(new_name_file)
            new_error_l.append(new_error)
            new_log_l.append(new_log)
            name_l.append(name)
 
    # Handle cases where info or precheck_commands are empty
    if info == [] and precheck_commands == []:
        f = open("Device_status.txt", "w")
        f.write("Host file and Command Files are both empty")
        f.close()
    elif info == []:
        f = open("Device_status.txt", "w")
        f.write("Host file is empty")
        f.close()
    elif precheck_commands == []:
        f = open("Device_status.txt", "w")
        f.write("command file is empty")
        f.close()
    else:
        count = 0
        for line in info:
            if (len(line.strip().split(",")) != 3):
                count += 1
        if count == len(info):
            f = open("Device_status.txt", "w")
            f.write("Invalid file format for Host file")
            f.close()
        else:
            f = open("Device_status.txt", "w")
            f.write(str(count_devices_success) + " out of " + str(count_devices) + " are successfully executed and outputs are fetched")
            f.close()
 
    # Write end signal to file
    f = open("1.txt", "w")
    f.write("end")
    f.close()
    file_name = date + HOST + ".txt"
    if os.path.exists(file_name):
        os.remove(file_name)
 
    # Return new file names and names list
    return new_name_file_l, new_error_l, new_log_l, name_l