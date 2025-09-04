# import requests
# import pandas as pd
# import time

# # Replace 'your_port_number' with the port number you're querying
# port_number = '1'
# api_endpoint = f'http://applipedia.sourcenet.ch/?app=tcp%2F{port_number}'

# def fetch_application_name(api_endpoint, retries=3, delay=5):
#     for attempt in range(retries):
#         try:
#             # Make the web request
#             response = requests.get(api_endpoint)
#             response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            
#             # Check if the response is in JSON format
#             try:
#                 app_data = response.json()
#                 return app_data.get('application_name', 'Application name not found')
#             except ValueError:
#                 print("Error: Response is not in JSON format.")
#                 return 'Application name not found'

#         except requests.RequestException as e:
#             print(f"HTTP Request failed: {e}")
#             if attempt < retries - 1:
#                 print(f"Retrying in {delay} seconds...")
#                 time.sleep(delay)  # Wait before retrying
#             else:
#                 return 'Application name not found'

# # Fetch the application name
# app_name = fetch_application_name(api_endpoint)

# # Organize data into a DataFrame
# df = pd.DataFrame({'Port Number': [port_number], 'Application Name': [app_name]})

# # Export to Excel
# df.to_excel('palo_alto_lookup.xlsx', index=False)



from difflib import SequenceMatcher
matcher = SequenceMatcher(None, "S    0.0.0.0 0.0.0.0 [255/0] via 10.130.129.1, inside tunneled","S        0.0.0.0 0.0.0.0 [255/0] via 10.130.129.1, inside tunneled").ratio()
print(matcher)