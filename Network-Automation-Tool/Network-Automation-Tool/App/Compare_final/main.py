import webbrowser
import difflib
import re
from difflib import SequenceMatcher
import re
from collections import OrderedDict
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import webbrowser
import os

def clean(file, prefix_line, count):
    """
    Function to clean lines in a file based on a prefix and write to a new file.

    Args:
    file (list): List of lines from the input file.
    prefix_line (str): Prefix string to identify lines to keep.
    count (int): Count number to append to the output file name.
    """
    n = len(file)  # Get the number of lines in the file
    with open("Cleaned_" + str(count) + ".txt", "w") as outfile:  # Open a new file for writing
        for ind in range(len(file)):  # Iterate through each line index in the file
            line = file[ind]  # Get the current line
            next_line = ""  # Initialize an empty string for the next line
            if ind < n - 1:  # Check if there's a next line available
                next_line = file[ind + 1]  # Get the next line if available
            clean_line = line.replace('\x08', '')  # Remove special characters from the line
            if line.strip():  # Check if the line is not empty after stripping
                # Check conditions to skip consecutive lines starting with prefix_line
                if line.startswith(prefix_line) and (next_line and next_line.startswith(prefix_line)):
                    continue  # Skip writing the line to the output file
            outfile.write(clean_line + "\n")  # Write cleaned line to the output file

def process_routing_line(line):
    """
    Function to process a routing line and extract relevant information.

    Args:
    line (str): Routing information line.

    Returns:
    str: Processed routing line with extracted details.
    """
    match = re.match(r'(\S+/\d+)\s+(\d+\.\d+\.\d+\.\d+)', line)  # Regex match to extract destination and next hop IP
    if match:
        destination = match.group(1)  # Extract destination from the match
        nexthop = match.group(2) or ""  # Extract next hop IP from the match or set to empty string if None
        words = line.split(" ")  # Split the line into words
        next_add = False  # Flag to track adding words to flags
        flags = ""  # Variable to store flags
        metric=""
        interface=""
        for word in words:  # Iterate through each word in the line
            if word.isnumeric():  # Check if the word is numeric (metric)
                metric = word  # Assign metric
            if "A" in word:  # Check if 'A' is in the word
                if len(word) == 1 and not next_add:  # Check conditions for flag assignment
                    flags = word  # Assign flag
                    next_add = True  # Set next_add flag to True
                else:
                    flags = word  # Assign flag
                    break  # Break out of the loop
            elif next_add:  # Check if next_add flag is True
                flags += word  # Add word to flags
                next_add = False  # Reset next_add flag
                break  # Break out of the loop
        AS = words[-1].strip()  # Get the AS (Autonomous System) number from the last word
        if not AS.isnumeric():  # Check if AS is not numeric
            AS = ""  # Set AS to empty string

        # Extract interface based on specific conditions (ethernet or IP address format)
        interface = next((word for word in line.split() if "ethernet" in word.lower() or ("." in word and word.count(".") == 1)), "")
        return f"{destination} {nexthop} {metric} {flags} {AS} {interface}"  # Construct formatted output
    return line  # Return original line if no match

def process_lines(lines):
    """
    Function to process multiple lines of routing information.

    Args:
    lines (list): List of lines containing routing information.

    Returns:
    list: Sorted list of processed routing lines.
    """
    return sorted(process_routing_line(line) if "destination" not in line.lower() else line for line in lines)

def find_closest_matches(from_lines, to_lines,command=""):
    if command:
        dic_from = {}
        dic_to = {}
        matches = []

        # Populate dictionaries
        for line in from_lines:
            parts = line.strip().split()
            if parts:
                dic_from[parts[0]] = line.strip()

        for line in to_lines:
            parts = line.strip().split()
            if parts:
                dic_to[parts[0]] = line.strip()

        # Compare entries in dictionaries
        for key in set(dic_from.keys()).union(dic_to.keys()):
            if key not in dic_from:
                matches.append(["", dic_to[key]])
            elif key not in dic_to:
                matches.append([dic_from[key], ""])
            else:
                # Extract the relevant parts after the key
                r1 = dic_from[key][dic_from[key].index(key) + len(key):].strip()
                r2 = dic_to[key][dic_to[key].index(key) + len(key):].strip()
                
                r1_parts = r1.split()
                r2_parts = r2.split()

                # Ensure we have parts to compare
                if r1_parts and r2_parts:
                    if r1_parts[0] == r2_parts[0]:
                        matches.append(["***Ds" + dic_from[key], "***Ds" + dic_to[key]])
                    else:
                        matches.append([dic_from[key], dic_to[key]])
                else:
                    matches.append([dic_from[key], dic_to[key]])

        return matches
    matches = []  # List to store matched pairs of lines
    to_lines_copy = list(to_lines)  # Copy of 'to_lines' list to preserve original
    matcher = difflib.SequenceMatcher()  # SequenceMatcher object for comparing sequences
    l = len(from_lines)  # Length of 'from_lines' list
    count = 0  # Counter to track iterations
    from_lines_copy = list(from_lines)  # Copy of 'from_lines' list to preserve original
    from_lines_copy1 = list(from_lines)  # Another copy of 'from_lines' list to preserve original
    map = {}  # Dictionary to map lines from 'from_lines' to their indices
    # Mapping each line to its indices in 'from_lines'
    for i in range(len(from_lines)):
        if from_lines[i] in map:
            from_lines[i]=from_lines[i].strip()
            map[from_lines[i]].append(i)
        else:
            map[from_lines[i]] = [i]
    to_map = {}  # Dictionary to map lines from 'to_lines' to their indices
    # Mapping each line to its indices in 'to_lines'
    for i in range(len(to_lines)):
        to_lines[i]=to_lines[i].strip()
        if to_lines[i] in to_map:
            to_map[to_lines[i]].append(i)
        else:
            to_map[to_lines[i]] = [i]
    to_lines_copy = list(to_lines)
    from_lines_map = {}  # Dictionary to store final matched pairs based on indices
    # Initialize each index in 'from_lines_map' with an empty list
    for i in range(len(from_lines)):
        from_lines_map[i] = []
            
    # Loop through each line in 'from_lines_copy'
    for from_line in from_lines_copy:
        count += 1  # Increment the counter
        closest_match, highest_ratio = None, 0  # Initialize variables for closest match and highest ratio
        # Loop through each line in 'to_lines_copy'
        for to_line in to_lines_copy:
            matcher = SequenceMatcher(None, from_line, to_line).ratio()  # Compute similarity ratio
            diff = difflib.ndiff(from_line, to_line)
            delta = ''.join(x[2:] for x in diff if x.startswith('- '))
            if matcher >= 0.99 or len(delta.strip())==0:  # Check if ratio is greater than or equal to 0.99
                ind = map[from_line].pop(0)  # Get index of 'from_line' from 'map' and remove from list
                matches.append((from_line, to_line))  # Add matched pair to 'matches'
                from_lines_map[ind] = [from_line, to_line]  # Add pair to 'from_lines_map'
                to_lines_copy.remove(to_line)  # Remove 'to_line' from 'to_lines_copy'
                from_lines_copy1.remove(from_line)  # Remove 'from_line' from 'from_lines_copy1'
                break  # Exit inner loop

    # Update 'from_lines_copy' with 'from_lines_copy1'
    from_lines_copy = list(from_lines_copy1)
    # Repeat matching process with ratio threshold 0.9
    for from_line in from_lines_copy:
        count += 1  # Increment the counter
        closest_match, highest_ratio = None, 0  # Initialize variables for closest match and highest ratio
        # Loop through each line in 'to_lines_copy'
        for to_line in to_lines_copy:
            matcher = SequenceMatcher(None, from_line, to_line).ratio()  # Compute similarity ratio
            if matcher >= 0.9:  # Check if ratio is greater than or equal to 0.9
                ind = map[from_line].pop(0)  # Get index of 'from_line' from 'map' and remove from list
                matches.append((from_line, to_line))  # Add matched pair to 'matches'
                from_lines_map[ind] = [from_line, to_line]  # Add pair to 'from_lines_map'
                from_lines_copy1.remove(from_line)  # Remove 'from_line' from 'from_lines_copy1'
                to_lines_copy.remove(to_line)  # Remove 'to_line' from 'to_lines_copy'
                break  # Exit inner loop

    # Update 'from_lines_copy' with 'from_lines_copy1'
    from_lines_copy = from_lines_copy1
    # Repeat matching process with ratio threshold 0.8
    for from_line in from_lines_copy:
        count += 1  # Increment the counter
        closest_match, highest_ratio = None, 0  # Initialize variables for closest match and highest ratio
        # Loop through each line in 'to_lines_copy'
        for to_line in to_lines_copy:
            matcher = SequenceMatcher(None, from_line, to_line).ratio()  # Compute similarity ratio
            if matcher >= 0.8:  # Check if ratio is greater than or equal to 0.8
                ind = map[from_line].pop(0)  # Get index of 'from_line' from 'map' and remove from list
                matches.append((from_line, to_line))  # Add matched pair to 'matches'
                from_lines_map[ind] = [from_line, to_line]  # Add pair to 'from_lines_map'
                from_lines_copy1.remove(from_line)  # Remove 'from_line' from 'from_lines_copy1'
                to_lines_copy.remove(to_line)  # Remove 'to_line' from 'to_lines_copy'
                break  # Exit inner loop

    closest_match, highest_ratio = None, 0  # Reset variables for closest match and highest ratio
    # Update 'from_lines_copy' with 'from_lines_copy1'
    from_lines_copy = from_lines_copy1
    # Final pass to match remaining 'from_lines_copy' with best available 'to_line'
    for from_line in from_lines_copy:
        count += 1  # Increment the counter
        closest_match, highest_ratio = None, 0  # Initialize variables for closest match and highest ratio
        # Loop through each line in 'to_lines_copy'
        for to_line in to_lines_copy:
            matcher = SequenceMatcher(None, from_line, to_line).ratio()  # Compute similarity ratio
            if matcher > highest_ratio and matcher > 0.5:  # Check if ratio is higher than current highest and above threshold
                highest_ratio = matcher  # Update highest ratio
                closest_match = to_line  # Update closest match
        if closest_match:  # If closest match found
            ind = map[from_line].pop(0)  # Get index of 'from_line' from 'map' and remove from list
            from_lines_map[ind] = [from_line, closest_match]  # Add pair to 'from_lines_map'
            matches.append((from_line, closest_match))  # Add matched pair to 'matches'
            to_lines_copy.remove(closest_match)  # Remove 'closest_match' from 'to_lines_copy'
        else:  # If no match found
            ind = map[from_line].pop(0)  # Get index of 'from_line' from 'map' and remove from list
            from_lines_map[ind] = [from_line, ""]  # Add empty match to 'from_lines_map'
            matches.append((from_line, ""))  # Add (from_line, "") to 'matches'

    # Handle unmatched lines in 'to_lines_copy'
    for i in to_lines_copy:
        ind = to_map[i].pop(0)  # Get index of 'i' from 'to_map' and remove from list
        for j in range(len(from_lines), ind, -1):  # Shift indices in 'from_lines_map' for unmatched lines
            from_lines_map[j] = from_lines_map[j - 1]
        from_lines_map[ind] = ["", i]  # Add unmatched pair to 'from_lines_map'

    return from_lines_map.values()  # Return values of 'from_lines_map' as list of matched pairs


def process_ip_route(fromtext, dic):
    res = []  # List to store results
    characters = []  # List to store uppercase characters
    # Populate 'characters' list with uppercase letters (A-Z)
    for i in range(65, 91):
        characters.append(chr(i))
    l = ""  # Initialize empty string 'l'
    key = ""  # Initialize empty string 'key'
    for i in fromtext:  # Iterate through each item in 'fromtext'
        line = ""  # Initialize empty string 'line'
        i = i.strip()  # Strip leading/trailing whitespace from 'i'
        words = i.split(",")  # Split 'i' by comma and store in 'words'
        for j in range(len(words)):  # Loop through 'words'
            if j == 1:  # Skip index 1 in 'words'
                continue
            line = line + words[j]  # Concatenate 'line' with 'words[j]'
        i = line  # Update 'i' with 'line'
        if i[0] in characters:  # Check if first character of 'i' is in 'characters'
            if key:  # If 'key' is not empty
                dic[key] = l  # Add 'l' to 'dic' with 'key'
                res.append(key)  # Append 'key' to 'res'
            l = i  # Update 'l' with 'i'
            key = i  # Update 'key' with 'i'
        else:
            l = l + ".....#" + i  # Concatenate 'l' with ".....#" and 'i'
    if key:  # If 'key' is not empty
        dic[key] = l  # Add 'l' to 'dic' with 'key'
        res.append(key)  # Append 'key' to 'res'
    return res  # Return 'res'

def generate_diff_html(fromcontent, tocontent, name):
    html_content =  f"""<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<style>
h1 {{ margin: 15px; }}
.add {{ background-color: #56E36C; }}
.remove {{ background-color: #FF848A; }}
.change {{ background-color: #F8D756; }}
.command {{ font-weight: bold; text-align:center; background-color: #f2f2f2; }}
th {{ text-align: center; }}
td {{ overflow: hidden; text-overflow: ellipsis; }}
.table-wrapper {{ display: block; width: 100%; }}
.table-fixed {{ width: 100%; }}
.table-fixed th, .table-fixed td {{ vertical-align: top; }}
.table-fixed .command {{ width: 20%; }}
.table-fixed .precheck {{ width: 40%; }}
.table-fixed .postcheck {{ width: 40%; }}
.command {{ word-wrap: break-word; }}  /* Adjusted for text wrapping */
.legend {{ margin: 15px; font-weight: bold; }}
.legend .item {{ display: inline-block; margin-right: 15px; }}
.legend .color-box {{ display: inline-block; width: 20px; height: 20px; vertical-align: middle; margin-right: 5px;
text-align:center; }}
.legend .add {{ background-color: #56E36C; }}
.legend .remove {{ background-color: #FF848A; }}
.legend .change {{ background-color: #F8D756; }}
</style>
</head>
<body>
<center><h1>Device name: {name}</h1>
<div class="legend">
    <div class="item"><span class="color-box add"></span>Added</div>
    <div class="item"><span class="color-box remove"></span>Removed</div>
    <div class="item"><span class="color-box change"></span>Changed</div>
</div>
<div class="table-wrapper">
<table class="table table-bordered table-hover table-fixed">
<thead class="thead-light">
<tr><th class="command">Command</th><th class="precheck">Precheck</th><th class="postcheck">Postcheck</th></tr>
</thead>
<tbody>
"""
    html_content1 = f"""<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<style>
h1 {{ margin: 15px; }}
.add {{ background-color: #56E36C; }}
.remove {{ background-color: #FF848A; }}
.change {{ background-color: #F8D756; }}
.command {{ font-weight: bold; text-align:center; background-color: #f2f2f2; }}
th {{ text-align: center; }}
td {{ overflow: hidden; text-overflow: ellipsis; }}
.table-wrapper {{ display: block; width: 100%; }}
.table-fixed {{ width: 100%; }}
.table-fixed th, .table-fixed td {{ vertical-align: top; }}
.table-fixed .command {{ width: 20%; }}
.table-fixed .precheck {{ width: 40%; }}
.table-fixed .postcheck {{ width: 40%; }}
.command {{ word-wrap: break-word; }}  /* Adjusted for text wrapping */
.legend {{ margin: 15px; font-weight: bold; }}
.legend .item {{ display: inline-block; margin-right: 15px; }}
.legend .color-box {{ display: inline-block; width: 20px; height: 20px; vertical-align: middle; margin-right: 5px;
text-align:center; }}
.legend .add {{ background-color: #56E36C; }}
.legend .remove {{ background-color: #FF848A; }}
.legend .change {{ background-color: #F8D756; }}
</style>
</head>
<body>
<center><h1>Device name: {name}</h1>
<div class="legend">
    <div class="item"><span class="color-box add"></span>Added</div>
    <div class="item"><span class="color-box remove"></span>Removed</div>
    <div class="item"><span class="color-box change"></span>Changed</div>
</div>
<div class="table-wrapper">
<table class="table table-bordered table-hover table-fixed">
<thead class="thead-light">
<tr><th class="command">Command</th><th class="precheck">Precheck</th><th class="postcheck">Postcheck</th></tr>
</thead>
<tbody>
"""
    ordered_keys = OrderedDict()
    for key in fromcontent.keys():          #Map the commands with None initially
        ordered_keys[key] = None
   
    for key in tocontent.keys():            #Map the commands with None initially
        ordered_keys[key] = None  
   
    keys = list(ordered_keys.keys())
 
    keys_union = keys + [key for key in tocontent.keys() if key not in keys]            #Union of precheck and postcheck files keys
   
    show_ip_route_dic_from={}           #Function for command specific filtering  (show ip route) in Precheck File
    show_ip_route_dic_to={}             #Function for command specific filtering  (show ip route) in Precheck File
    count=0
    matches=[]
    tunnel_to = {}
    tunnel_from = {}
    int_to={}
    int_from={}
    for command in keys_union:
        from_text = fromcontent.get(command, "").splitlines()       #Get the current command to check
        to_text = tocontent.get(command, "").splitlines()
        command=command[command.index(".")+1:]
        f=open("1.txt","w")
        f.write(str(count+1)+" is being executed:"+command)         #Write the information about which command is being executed in a dummy file
        count+=1
        if command.strip()=="show interfaces brief":
            print(to_text.count('Admin up:           yes'),from_text.count('Admin up:           yes'))
        if command.strip() == "show routing route":             #Check for the specific command occurance to change the comparison process
            from_text = process_lines(from_text)
            to_text = process_lines(to_text)
        if command.strip() == "show ip route":                  #Check for the specific command occurance to change the comparison process
            from_text = process_ip_route(from_text,show_ip_route_dic_from)
            to_text = process_ip_route(to_text,show_ip_route_dic_to)
        matches=[]
        if command.strip()=="show rtm rib":
            matches=find_closest_matches(from_text,to_text,command)
        if "tunnel" in command:
            
            def populate_tunnel_dict(text, tunnel_dict):
                k = ""
                s = []
                cross=False
                for i in text:
                    if "Tunnel" in i and "state" in i:
                        if k != "":
                            tunnel_dict[k] = "\n".join(s)
                        k = i
                        s = []
                    s.append(k+" "+i)
                if k != "":
                    tunnel_dict[k] = "\n".join(s)
            
            populate_tunnel_dict(from_text, tunnel_from)
            populate_tunnel_dict(to_text, tunnel_to)
            
            for k in set(tunnel_to.keys()).union(set(tunnel_from.keys())):
                matches.extend(find_closest_matches(tunnel_from.get(k, "").splitlines(), tunnel_to.get(k, "").splitlines()))
        if command.strip()=="show interfaces brief":
            def populate_interface_dict(text, int_dict):
                k = ""
                s = []
                cross=False
                for i in text:
                    if "Interface" in i and "state" in i:
                        if k != "":
                            int_dict[k] = "\n".join(s)
                        k = i
                        s = []
                    s.append(k+" "+i)
                if k != "":
                    int_dict[k] = "\n".join(s)
            
            populate_interface_dict(from_text, int_from)
            populate_interface_dict(to_text, int_to)
            
            for k in set(int_to.keys()).union(set(int_from.keys())):
                matches.extend(find_closest_matches(int_from.get(k, "").splitlines(), int_to.get(k, "").splitlines()))
            

        if matches==[]:
            matches = find_closest_matches(from_text, to_text)          #Analyze the lines for matching them in Precheck and Postcheck files
        visited=set()
        precheck_content = []
        postcheck_content = []
        precheck_content1 = []
        postcheck_content1 = []
        for from_line, to_line in matches:
            key_line=""
            if "Tunnel" in from_line and "state" in from_line:
                key_line=from_line[from_line.index("Tunnel"):from_line.index("state")]
                from_line=from_line[from_line.index("state")+5:]
            if "Interface" in from_line and "state" in from_line:
                key_line=from_line[from_line.index("Interface"):from_line.index("state")]
                from_line=from_line[from_line.index("state")+5:]
            if "Tunnel" in to_line and "state" in to_line:
                key_line=to_line[to_line.index("Tunnel"):to_line.index("state")]
                to_line=to_line[to_line.index("state")+5:]
            if "Interface" in to_line and "state" in to_line:
                key_line=to_line[to_line.index("Interface"):to_line.index("state")]
                to_line=to_line[to_line.index("state")+5:]
            from_line=from_line.strip()
            to_line=to_line.strip()
            if from_line in show_ip_route_dic_from or to_line in show_ip_route_dic_to:
                res1=show_ip_route_dic_from.get(from_line)
                res2=show_ip_route_dic_to.get(to_line)
                if not res1:
                    res1=""
                if not res2:
                    res2=""
                res1 = res1.split(".....#")         #Do a route wise comparison on the lines generated in both precheck and postcheck files
                res2 = res2.split(".....#")
                mat = find_closest_matches(res1, res2)
                change = False          #Flag to check if there is any change
                global change_check         #Make the variable Global
                for from_line, to_line in mat:
                    if from_line != to_line:        #If the line is present in the precheck but not in the postcheck file
                        change = True
                for from_line, to_line in mat:
                    if from_line.startswith("***Ds"):
                        from_line=from_line[5:]
                        to_line=to_line[5:]
                        if change:
                            precheck_content.append(f'<span class="d-block mb-2">{from_line}</span>')
                            postcheck_content.append(f'<span class="d-block mb-2">{to_line}</span>')
                        precheck_content1.append(f'<span class="d-block mb-2">{from_line}</span>')
                        postcheck_content1.append(f'<span class="d-block mb-2">{to_line}</span>')
                    elif from_line != to_line:            #Appending the lines in the HTML page

                        #The colours are assigned as per the classes assigned 
                        #class=remove for removed line in the postcheck file----->Red
                        #class=add for added line in the postcheck file---------->Green
                        #class=change for removed line in the postcheck file----->Yellow
                        if from_line and not to_line:
                            precheck_content.append(f'<span class="remove d-block mb-2">{from_line}</span>')
                            postcheck_content.append(f'<span class="remove d-block mb-2"></br></span>')
                            precheck_content1.append(f'<span class="remove d-block mb-2">{from_line}</span>')
                            postcheck_content1.append(f'<span class="remove d-block mb-2"></br></span>')
                        elif to_line and not from_line:
                            precheck_content.append(f'<span class="add d-block mb-2"></br></span>')
                            postcheck_content.append(f'<span class="add d-block mb-2">{to_line}</span>')
                            precheck_content1.append(f'<span class="add d-block mb-2"></br></span>')
                            postcheck_content1.append(f'<span class="add d-block mb-2">{to_line}</span>')
                        else:
                            precheck_content.append(f'<span class="change d-block mb-2">{from_line}</span>')
                            postcheck_content.append(f'<span class="change d-block mb-2">{to_line}</span>')
                            precheck_content1.append(f'<span class="change d-block mb-2">{from_line}</span>')
                            postcheck_content1.append(f'<span class="change d-block mb-2">{to_line}</span>')
                    else:
                        if change:
                            precheck_content.append(f'<span class="d-block mb-2">{from_line}</span>')
                            postcheck_content.append(f'<span class="d-block mb-2">{to_line}</span>')
                        precheck_content1.append(f'<span class="d-block mb-2">{from_line}</span>')
                        postcheck_content1.append(f'<span class="d-block mb-2">{to_line}</span>')
                continue
 
            if from_line.replace(" ","") !=to_line.replace(" ","") and not from_line.startswith("***Ds") and "Uptime" not in from_line:
                if key_line!="" and key_line.strip() not in visited:
                    precheck_content.append(f'<span class="d-block mb-2">{key_line}</span>')
                    postcheck_content.append(f'<span class="d-block mb-2">{key_line}</span>')
                    visited.add(key_line.strip())
                if from_line and not to_line:
                    precheck_content.append(f'<span class="remove d-block mb-2">{from_line}</span>')
                    postcheck_content.append(f'<span class="remove d-block mb-2"></br></span>')
                    precheck_content1.append(f'<span class="remove d-block mb-2">{from_line}</span>')
                    postcheck_content1.append(f'<span class="remove d-block mb-2"></br></span>')
                elif to_line and not from_line:
                    precheck_content.append(f'<span class="add d-block mb-2"></br></span>')
                    postcheck_content.append(f'<span class="add d-block mb-2">{to_line}</span>')
                    precheck_content1.append(f'<span class="add d-block mb-2"></br></span>')
                    postcheck_content1.append(f'<span class="add d-block mb-2">{to_line}</span>')
                else:
                    precheck_content.append(f'<span class="change d-block mb-2">{from_line}</span>')
                    postcheck_content.append(f'<span class="change d-block mb-2">{to_line}</span>')
                    precheck_content1.append(f'<span class="change d-block mb-2">{from_line}</span>')
                    postcheck_content1.append(f'<span class="change d-block mb-2">{to_line}</span>')
            else:
                if "***Ds" in from_line:
                    from_line=from_line[5:]
                    to_line=to_line[5:]
                precheck_content1.append(f'<span class="d-block mb-2">{from_line}</span>')
                postcheck_content1.append(f'<span class="d-block mb-2">{to_line}</span>')
 
        precheck_html = ''.join(precheck_content)       #Join all the lines to write into the HTML file
        postcheck_html = ''.join(postcheck_content)
        precheck_html1 = ''.join(precheck_content1)
        postcheck_html1 = ''.join(postcheck_content1)
        global change_check
        if len(precheck_content) != 0:
            global change_check
            change_check=True
            if command.strip() == "show ip route":
                precheck_html = f'<div style="white-space: pre-wrap;">{precheck_html}</div>'
                postcheck_html = f'<div style="white-space: pre-wrap;">{postcheck_html}</div>'
            html_content += f'<tr><td class="command">{command}</td><td>{precheck_html}</td><td>{postcheck_html}</td></tr>'
 
        html_content1 += f'<tr><td class="command ">{command}</td><td>{precheck_html1}</td><td>{postcheck_html1}</td></tr>'
    html_content += """</tbody></table></div></div></body></html>"""
    if not change_check:
        html_content = f"""<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
<style>
h1 {{ margin: 15px; }}
.add {{ background-color: #56E36C; }}
.remove {{ background-color: #FF848A; }}
.change {{ background-color: #F8D756; }}
.command {{ font-weight: bold; background-color: #f2f2f2; }}
th {{ text-align: center; }}
td {{ overflow: hidden; text-overflow: ellipsis; }}
.table-wrapper {{ display: block; width: auto }}
.table-fixed {{ width: 100%; }}
.table-fixed th, .table-fixed td {{ vertical-align: top; }}
.table-fixed .command {{ width: 20%; }}
.table-fixed .precheck {{ width: 40%; }}
.table-fixed .postcheck {{ width: 40%; }}
.command {{ word-wrap: break-word; }}  /* Adjusted for text wrapping */
.legend {{ margin: 15px; font-weight: bold; }}
.legend .item {{ display: inline-block; margin-right: 15px; }}
.legend .color-box {{ display: inline-block; width: 20px; height: 20px; vertical-align: middle; margin-right: 5px;
text-align:center; }}
.legend .add {{ background-color: #56E36C; }}
.legend .remove {{ background-color: #FF848A; }}
.legend .change {{ background-color: #F8D756; }}
</style>
</head>
<body>
<center><h1>Device name: {name}</h1>
<div class="legend">
    <div class="item"><span class="color-box add"></span>Added</div>
    <div class="item"><span class="color-box remove"></span>Removed</div>
    <div class="item"><span class="color-box change"></span>Changed</div>
</div>
<div class="table-wrapper">
<table class="table table-bordered table-hover table-fixed">
"""
        html_content+='<div style="font-weight: bold; font-size: 40px; margin-top: 20px;">NO DIFFERENCES FOUND between the current files</div>'
    html_content1 += """
</tbody>
</table>
</div>
</div>
</body>
</html>
"""
    return html_content, html_content1

def parse_content(lines, prefix_line):
    count = 0
    command_output = OrderedDict()
    current_block = ""       #Take the current block(command and output)
    command = None
    count_command={}
    for line in lines:
        if "7mlines" in line:    #To make the comparison work for any file, if there are any unknown characters due to the spaces or keyboard interaction, they are eliminiated from the checking
            continue
        line = line.strip()         #To remove extra spaces and new line characters
        if not re.search(r'[a-zA-Z0-9]', line):     #Remove empty lines
            continue
 
        if line.startswith(prefix_line):        #To Check if the current line contains the command
            count += 1
            if command!=None:
                command_output[command.strip()] = current_block         #Update the current command output block
            command = line[len(prefix_line):].strip()           #Strip the line of empty spaces and next line characters
            if command in count_command:
                count_command[command]+=1           #Check for the re-occurance of a command again in the file
            else:
                count_command[command]=0
            n1=count_command[command]
            n=count_command[command]
            count_dig=0
            while(n):               #Handling repeated commands
                n=n//10
                count_dig+=1
            count_dig=max(1,count_dig)
            command=str(n1+1)+"."+command
            current_block = ""
        else:
            if "pid" in line and "(" in line:               #To remove pid from comparison as it is not a significant value to compare
                line = line[:line.index("(")] + line[line.index(")") + 1:]
            current_block += line + "\n"
 
    if current_block and command:
        command_output[command] = current_block.strip()
    return command_output
 
 
def files(fromfile,tofile):
    prefix_line=""          #Set the line for capturing the command line as NULL
    from_dic={}             #Dictionary for the Precheck File
    to_dic={}               #Dictionary for the Postcheck File
    fromlines=fromfile.read().decode("utf-8").splitlines()          #Read all the lines in the file and save into a list
    tolines=tofile.read().decode("utf-8").splitlines()              #Read all the lines in the file and save into a list
    
    #For the Precheck File
    for line in fromlines:
        if line and (line[0]=="#" or line[0]==">"):                 #Check the line for the command if there is no command then remove the line from comparison
            continue
        if  ">" in line:            #Check the line for command
            rem=line[line.index(">")+1:]        #Strip the remaining and extract the command
            line=line[:line.index(">")+1]
            if rem.strip()=="":
                continue
        elif "#" in line:
            rem=line[line.index("#")+1:]            #Check the line for command
            line=line[:line.index("#")+1]           #Strip the remaining and extract the command
            if rem.strip()=="":
                continue
        else:
            continue
        if line.strip()=="":
            continue
        if line in from_dic:
            from_dic[line]+=1           #Check multiple occurances of the command in the Precheck file
        else:
            from_dic[line]=1            
    
    #For the Postcheck File
    for line in tolines:
        if line and (line[0]=="#" or line[0]==">"):
            continue
        if  ">" in line:
            rem=line[line.index(">")+1:]
            line=line[:line.index(">")+1]
            if rem.strip()=="":
                continue
        elif "#" in line:
            rem=line[line.index("#")+1:]
            line=line[:line.index("#")+1]
            if rem.strip()=="":
                continue
        else:
            continue
        if line.strip()=="":
            continue
        if line in to_dic:
            to_dic[line]+=1
        else:
            to_dic[line]=1
    from_key_set = set(from_dic.keys())         #Remove the repeated parts from the dictionary
    to_key_set = set(to_dic.keys())             #Remove the repeated parts from the dictionary
   
    keys = from_key_set.intersection(to_key_set)            #Find the common keys from both the dictionaries
    if len(keys)==0:            #If the files are empty then another page must be opened with an alert saying empty files
        with open("report.html", "w") as f:
            f.write("""<html>
            <head>
                <title>Empty File Alert</title>
                    <center><h1>Atleast one of the file is empty or is in invalid format</h1><center>
                <script>
                    function redirectToHomeCheck() {
                        window.close();
                    }
 
                    document.addEventListener('DOMContentLoaded', function() {
                        setTimeout(function() {
                            document.getElementById('alertMessage').style.display = 'block';
                            alert("Redirecting to comparison page");
                            redirectToHomeCheck();
                        }, 2000); // 2000 milliseconds = 2 seconds
                    });
                </script>
                <style>
                    #alertMessage {
                        display: none;
                    }
                </style>
            </head>
            <body>
                <center><h1 id="alertMessage">At least one of the files is in invalid format</h1></center>
            </body>
            </html>""")
 
        webbrowser.open("report.html")          #Automatically open the generated report into the browser
 
 
    else:
        # Initialize variables for finding the highest combined frequency
        highest_combined_key = None
        highest_combined_freq = 0
       
       # Iterate through keys to find the one with the highest combined frequency
        for key in keys:
            combined_freq = from_dic[key] + to_dic[key]
            if combined_freq > highest_combined_freq:
                highest_combined_key = key
                highest_combined_freq = combined_freq
        
        # Set prefix_line to the key with the highest combined frequency
        prefix_line=highest_combined_key

        # If Prefix line is none set to empty string
        if not prefix_line:
            prefix_line=""
        #Initialize count for cleaning the files
        count=1
        #Clean the Precheck File for redundant lines
        clean(fromlines,prefix_line,count)
        count+=1
        #Clean the Postcheck file for redundant lines
        clean(tolines,prefix_line,count)

        #Define the file names for cleaned Files
        fromfile="Cleaned_1.txt"
        tofile="Cleaned_2.txt"
        #Extract lines from the files
        with open(fromfile, 'r', errors='ignore') as f:
            fromlines = f.readlines()
        #Extract lines from the files
        with open(tofile, 'r', errors='ignore') as f:
            tolines = f.readlines()

        #Parse both the contents
        fromcontent = parse_content(fromlines,prefix_line)
        tocontent = parse_content(tolines,prefix_line)

        #Extract name from the prefix lines
        if ">" in prefix_line:
            if "@" in prefix_line and "(" in prefix_line:       #Firewall Hostname extraction
                name=prefix_line[prefix_line.index("@")+1:prefix_line.index("(")]
            elif "@" in prefix_line:        #Firewall Hostname extraction
                name=prefix_line[prefix_line.index("@")+1:]
            else:           #Router Hostname extraction
                name=prefix_line[:prefix_line.index(">")]
        elif "#" in prefix_line:        #Router Hostname extraction
            name=prefix_line[:prefix_line.index("#")]
        else:
            name=prefix_line
        html_diff,html_diff1 = generate_diff_html(fromcontent, tocontent,name)      #Pass the files into the function to generate the report

        with open("quick_report.html", "w") as f:               #Write the content into the html file
            f.write(html_diff)
        with open("complete_report.html", "w") as f:            #Write the content into the html file
            f.write(html_diff1)
        f=open("1.txt","w")
        f.write("end")
        f.close()

        # Function to extract modifications from the HTML
        def extract_modifications(html_content):
            soup = BeautifulSoup(html_content, 'html.parser')
            modifications = {'change': 0, 'add': 0, 'remove': 0, 'normal': 0}
            
            for span in soup.find_all('span'):
                class_list = span.get('class', [])
                matched = False
                for class_name in class_list:
                    if class_name in modifications:
                        modifications[class_name] += 1
                        matched = True
                if not matched:
                    modifications['normal'] += 1
            
            # Adjust counts
            for change in modifications:
                if modifications[change] != 0:
                    modifications[change] -= 1
                modifications[change] = modifications[change] // 2
            
            return modifications

        # Function to filter HTML based on modification type and add headers
        def filter_html(html_content, filter_value):
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Forcefully add an <h1> element
            if not soup.find('h1'):
                h1 = soup.new_tag('h1')
                h1.string = f'Report for Modification Type: {filter_value.capitalize()}'
                if soup.body:
                    soup.body.insert(0, h1)
                else:
                    soup.insert(0, h1)

            table = soup.find('table')

            if table is None:
                return str(soup)
            
            thead = soup.new_tag('thead')
            header_row = soup.new_tag('tr')

            command_header = soup.new_tag('th', **{'class': 'command'})
            command_header.string = 'Command'
            precheck_header = soup.new_tag('th', **{'class': 'precheck'})
            precheck_header.string = 'Precheck'
            postcheck_header = soup.new_tag('th', **{'class': 'postcheck'})
            postcheck_header.string = 'Postcheck'

            header_row.append(command_header)
            header_row.append(precheck_header)
            header_row.append(postcheck_header)
            thead.append(header_row)
            table.insert(0, thead)

            # Remove rows that do not contain the filter_value
            for span in table.find_all('span'):
                class_list = span.get('class', [])
                if filter_value not in class_list:
                    span.decompose()

            # Remove rows with no content
            for tr in table.find_all('tr'):
                if not tr.find_all('span'):
                    tr.decompose()
            
            return str(soup)

        # Read the HTML file
        html_file_path = 'complete_report.html'
        with open(html_file_path, 'r') as file:
            html_content = file.read()

        # Extract modifications
        modifications = extract_modifications(html_content)
        modifications_df = pd.DataFrame(list(modifications.items()), columns=['Modification', 'Count'])

        # Create and save interactive pie chart
        fig = px.pie(
            modifications_df,
            values='Count',
            names='Modification',
            title='Distribution of Changes',
            color='Modification',
            color_discrete_map={'add': 'green', 'change': 'yellow', 'remove': 'red', 'normal': 'lightgray'},
            labels={'Modification': 'Modification Type', 'Count': 'Number of Modifications'},
            hole=0.4  # Makes a donut chart
        )

        # Update chart aesthetics
        fig.update_traces(
            textinfo='label+percent',  # Show label and percentage
            hoverinfo='label+percent',  # Show label and percentage on hover
            marker=dict(line=dict(color='white', width=2))  # Add border to segments
        )

        fig.update_layout(
            title_text='Modification Types Distribution',
            title_x=0.5,
            title_font_size=24,
            legend_title_text='Modification Type',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                xanchor='center',
                x=0.5,
                y=-0.2
            ),
            autosize=True,
            height=500,
            width=700,
            plot_bgcolor='rgba(255,255,255,0.5)',  # Light white with transparency
            paper_bgcolor='rgba(255,255,255,0.5)',  # Light white with transparency
            font=dict(family="Arial, sans-serif", size=14, color="black"),
            margin=dict(t=50, b=50, l=50, r=50)  # Adjust margins for better centering
        )

        # Save Plotly chart to HTML string
        plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        # Save filtered HTML content to variables
        filtered_html_content = {}
        for modification in modifications.keys():
            filtered_html_content[modification] = filter_html(html_content, modification)

        # Generate the main HTML content with the plot and links
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Comparission Summary</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    text-align: center;
                    background: url('https://images.unsplash.com/photo-1526374842536-dfd2e058c3e4') no-repeat center center fixed; /* Beautiful network image */
                    background-size: cover;
                }}

                .container {{
                    display: inline-block;
                    background-color: rgba(255, 255, 255, 0.8); /* Light translucent background for the box */
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0px 4px 8px rgba(0,0,0,0.2); /* Subtle shadow effect */
                }}

                .button-container {{
                    display: flex;
                    justify-content: center;
                    flex-wrap: wrap;
                    margin-top: 20px;
                }}

                .button {{
                    background-color: #4CAF50; /* Default Green */
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 10px;
                    cursor: pointer;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}

                .button.add {{
                    background-color: #4CAF50; /* Green */
                }}

                .button.change {{
                    background-color: #FFEB3B; /* Yellow */
                    color: #000; /* Black text */
                }}

                .button.remove {{
                    background-color: #F44336; /* Red */
                }}

                .button.complete {{
                    background-color: #2196F3; /* Blue */
                }}

                .button.quick {{
                    background-color: #9E9E9E; /* Gray */
                }}

                .button:hover {{
                    opacity: 0.8;
                }}

                .button i {{
                    margin-right: 8px;
                }}

                #plot {{
                    margin-top: 20px;
                    display: inline-block;
                    text-align: center;
                }}

                h1 {{
                    color: #333;
                }}

            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.19.0/plotly.min.js"></script>
            <script>
                function openFilteredHtml(modification) {{
                    // Define URLs or content to display based on the modification type
                    const urls = {{
                        add: 'filtered_add_modifications.html',
                        change: 'filtered_change_modifications.html',
                        remove: 'filtered_remove_modifications.html',
                        normal: 'filtered_normal_modifications.html'
                    }};

                    // Use window.open to open the file in a new tab
                    if (urls[modification]) {{
                        window.open(urls[modification], '_blank');
                    }} else {{
                        console.error('Invalid modification type:', modification);
                    }}
                }}

                function openQuickReport() {{
                    // Open the quick report in a new tab
                    window.open('quick_report.html', '_blank');
                }}

                function handlePlotClick(eventData) {{
                    // Get modification type from plot click event
                    var modification = eventData.points[0].label.toLowerCase();
                    openFilteredHtml(modification);
                }}

                document.addEventListener('DOMContentLoaded', function() {{
                    var plotDiv = document.getElementById('plot');
                    Plotly.d3.select(plotDiv).on('plotly_click', handlePlotClick);
                }});
            </script>
        </head>
        <body>
            <center><h1>Modifications Report</h1></center>
            <div class="container">
                <div id="plot">{plotly_html}</div>
            </div>
            <div class="button-container">
                <button class="button add" onclick="openFilteredHtml('add')"><i class="fas fa-plus"></i> View Add Modifications</button>
                <button class="button change" onclick="openFilteredHtml('change')"><i class="fas fa-exchange-alt"></i> View Change Modifications</button>
                <button class="button remove" onclick="openFilteredHtml('remove')"><i class="fas fa-trash"></i> View Remove Modifications</button>
                <button class="button complete" onclick="window.open('complete_report.html', '_blank')"><i class="fas fa-file-alt"></i> View Complete Report</button>
                <button class="button quick" onclick="openQuickReport()"><i class="fas fa-rocket"></i> Quick Report</button>
            </div>
        </body>
        </html>
        """

        # Save the main HTML to a file
        report_file_path = "report.html"
        with open(report_file_path, "w") as f:
            f.write(html_template)
        def add_table_headers(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
        
            soup = BeautifulSoup(content, 'html.parser')
        
            table = soup.find('table')
            thead = soup.new_tag('thead')
            header_row = soup.new_tag('tr')

            command_header = soup.new_tag('th', **{'class': 'command'})
            command_header.string = 'Command'
            precheck_header = soup.new_tag('th', **{'class': 'precheck'})
            precheck_header.string = 'Precheck'
            postcheck_header = soup.new_tag('th', **{'class': 'postcheck'})
            postcheck_header.string = 'Postcheck'

            header_row.append(command_header)
            header_row.append(precheck_header)
            header_row.append(postcheck_header)
            thead.append(header_row)
            table.insert(0, thead)
        
            with open(file_path, 'w') as f:
                f.write(str(soup))
        
        # Apply the header addition to each filtered HTML file
        for mod_type in ['add', 'change', 'remove']:
            file_path = f'filtered_{mod_type}_modifications.html'
            add_table_headers(file_path)

        # Save the filtered HTML content to individual files
        for mod_type, content in filtered_html_content.items():
            file_path = f'filtered_{mod_type}_modifications.html'
            with open(file_path, 'w') as f:
                f.write(content)
            add_table_headers(file_path)
            print(f'Saved {file_path}')

        # Open the generated HTML file in a web browser
        if os.path.isfile(report_file_path):
            webbrowser.open(report_file_path)
        else:
            print(f"Failed to create {report_file_path}")