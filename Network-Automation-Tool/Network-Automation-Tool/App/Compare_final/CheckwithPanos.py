import pandas as pd
app_defaults = pd.read_csv(r"C:\Users\gopiprashanth.raju\OneDrive - Providence St. Joseph Health\Desktop\Network-Automation-Tool-Gopi (3)\Network-Automation-Tool-Gopi\Network-Automation-Tool-Gopi\App\Compare_final\applipedia_data_cleaned.csv")

# Convert the app_defaults to a dictionary for faster access
app_defaults_dict = app_defaults.set_index('Name').T.to_dict('list')
print(app_defaults_dict["ssl"])