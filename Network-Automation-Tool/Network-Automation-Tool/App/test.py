# # rule_results = [
# #     {"ip": {"rule_name": """Global_Rule_1; index: 1
# #     from ZoneA;
# #     source 10.0.0.1/24;
# #     source-region US-East;
# #     to ZoneB;
# #     destination 192.168.1.1/24;
# #     destination-region US-West;
# #     user admin;
# #     source-device server1;
# #     destination-device server2;
# #     category web;
# #     application/service [0:http/tcp/any/80 1:https/tcp/any/443];
# #     action deny;
# #     icmp-unreachable: yes;
# #     terminal no;
# #     """, "status": "deny"}},
# #     {"ip": {"rule_name": """Global_Rule_1; index: 1
# #     from ZoneA;
# #     source 10.0.0.1/24;
# #     source-region US-East;
# #     to ZoneB;
# #     destination 192.168.1.1/24;
# #     destination-region US-West;
# #     user admin;
# #     source-device server1;
# #     destination-device server2;
# #     category web;
# #     application/service [0:http/tcp/any/80 1:https/tcp/any/443];
# #     action deny;
# #     icmp-unreachable: yes;
# #     terminal no;
# #     """, "status": "deny"}}
# # ]

# # def generate_html_page(rule_results, firewall_matches, source, destination, src_zone, dest_zone, protocol, port):
# #     html_content = f'''
# #     <!DOCTYPE html>
# #     <html lang="en">
# #     <head>
# #         <meta charset="UTF-8">
# #         <meta name="viewport" content="width=device-width, initial-scale=1.0">
# #         <title>Firewall Rules Report</title>
# #         <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
# #         <style>
# #             body {{ font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0; }}
# #             .container {{ margin-top: 50px; }}
# #             .report-title {{ text-align: center; margin-bottom: 30px; }}
# #             .passed-inputs {{ margin-bottom: 30px; padding: 20px; background-color: #e9ecef; border-radius: 5px; }}
# #             .table-container {{ display: flex; justify-content: center; margin-bottom: 30px; }}
# #             table {{ width: 100%; max-width: 800px; border-collapse: collapse; text-align: left; }}
# #             .table thead {{ background-color: #343a40; color: #fff; }}
# #             .table tbody tr:nth-child(even) {{ background-color: #f2f2f2; }}
# #             .table tbody tr.status-allow {{ background-color: #d4edda; color: #155724; }}
# #             .table tbody tr.status-deny {{ background-color: #f8d7da; color: #721c24; }}
# #             .rule-details {{ white-space: pre-wrap; word-break: break-word; }}
# #             .close-button {{ display: flex; justify-content: center; margin-top: 30px; }}
# #         </style>
# #     </head>
# #     <body>
# #         <div class="container">
# #             <h2 class="report-title">Firewall Rules Report</h2>
# #             <div class="passed-inputs">
# #                 <h5>Passed Inputs</h5>
# #                 <p><strong>Source:</strong> {source}</p>
# #                 <p><strong>Destination:</strong> {destination}</p>
# #                 <p><strong>Source Zone:</strong> {src_zone}</p>
# #                 <p><strong>Destination Zone:</strong> {dest_zone}</p>
# #                 <p><strong>Protocol:</strong> {protocol}</p>
# #                 <p><strong>Port:</strong> {port}</p>
# #             </div>
# #             <div class="table-container">
# #                 <table class="table table-bordered">
# #                     <thead>
# #                         <tr>
# #                             <th>Firewall Name</th>
# #                             <th>Rule</th>
# #                             <th>Status</th>
# #                         </tr>
# #                     </thead>
# #                     <tbody>
# #     '''

# #     if not rule_results:
# #         html_content += '''
# #                         <tr>
# #                             <td colspan="3" class="text-center">No rules found.</td>
# #                         </tr>
# #         '''
# #     else:
# #         for result in rule_results:
# #             for firewall_ip, rule_info in result.items():
# #                 firewall_names = firewall_matches.get(firewall_ip, [])
# #                 for firewall_name in firewall_names:
# #                     # Split rule details into readable format
# #                     rule_details = rule_info['rule_name'].strip().split('\n')
# #                     rule_string = '<br>'.join([f'{detail.strip()}' for detail in rule_details])
# #                     status_class = "status-allow" if rule_info['status'] == "allow" else "status-deny"
# #                     html_content += f'''
# #                     <tr class="{status_class}">
# #                         <td>{firewall_name}</td>
# #                         <td class="rule-details">{rule_string}</td>
# #                         <td>{rule_info['status']}</td>
# #                     </tr>
# #                     '''

# #     html_content += '''
# #                     </tbody>
# #                 </table>
# #             </div>
# #             <div class="close-button">
# #                 <button class="btn btn-danger" onclick="window.close();">Close Window</button>
# #             </div>
# #         </div>
# #     </body>
# #     </html>
# #     '''

# #     with open('firewall_report.html', 'w') as f:
# #         f.write(html_content)

# # # Example usage
# # firewall_matches = {"ip": ["Firewall_1"]}
# # source = "10.0.0.1"
# # destination = "192.168.1.1"
# # src_zone = "ZoneA"
# # dest_zone = "ZoneB"
# # protocol = "tcp"
# # port = "80"

# # generate_html_page(rule_results, firewall_matches, source, destination, src_zone, dest_zone, protocol, port)


# # # output=" aekjsd fsdhdf Alloweddd"
# # # status = "Allowed" if "allow" in output.lower() else "Deny"
# # # print(status)
# # # Get current timestamp
# # # from datetime import datetime
# # # now = datetime.now()
# # # timestamp = str(now.strftime("%Y-%m-%d %H:%M:%S"))
 
# # # # Extract date part from timestamp
# # # date = timestamp[:11]
# # # import sqlite3
# # # conn = sqlite3.connect('sql.db')
# # # cursor = conn.cursor()
# # # firewall_map={}
# # # firewall_map["firewall1"] = {
# # #         'ip': "ip3",
# # #             'interfaces': [{
# # #                     'name': "parts[0]",
# # #                     'id': "parts[1]",
# # #                     'vsys': "parts[2]",
# # #                     'zone': "",
# # #                     'forwarding': "parts[3]",
# # #                     'tag': "arts[4]",
# # #                     'address':" parts[5]",
# # #                 }]
# # #         }
# # # # Create table with the new schema if it doesn't exist
# # # cursor.execute('''
# # #     CREATE TABLE IF NOT EXISTS firewall (
# # #         FIREWALL_IP TEXT PRIMARY KEY NOT NULL,
# # #         NAME TEXT NOT NULL,
# # #         SUBNETS TEXT NOT NULL,
# # #         ZONES TEXT NOT NULL,
# # #         DATE TEXT NOT NULL
# # #     )
# # # ''')

# # # for name, data in firewall_map.items():
# # #     print(data)
# # #     subnets = ','.join([iface['address'] for iface in data['interfaces']])
# # #     zones = ','.join([iface['zone'] for iface in data['interfaces']])
    
# # #     # Check if the record exists
# # #     cursor.execute("SELECT COUNT(*) FROM firewall WHERE FIREWALL_IP = ?", (data['ip'],))
# # #     record_exists = cursor.fetchone()[0]

# # #     if record_exists:
# # #         print(record_exists)
# # #         # Update existing record
# # #         update_data_query = '''
# # #             UPDATE firewall
# # #             SET NAME = ?, SUBNETS = ?, ZONES = ?, DATE= ?
# # #             WHERE FIREWALL_IP = ?
# # #         '''
# # #         cursor.execute(update_data_query, (name, subnets, zones,date, data['ip']))
# # #         conn.commit()
# # #         conn.close()
# f=open("Host.txt","w")
# for i in range(100):
#     f.write("R"+str(i)+",cisco,cisco\n")
# f.close()
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import webbrowser
import os

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
    title='Distribution of Modifications',
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
    <title>Modifications Report</title>
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
