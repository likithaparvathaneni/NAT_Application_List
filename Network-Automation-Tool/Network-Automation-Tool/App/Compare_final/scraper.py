from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import re  # Import regex to extract ID

# Initialize WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (optional)
options.add_argument("--disable-blink-features=AutomationControlled")  # Reduce bot detection
options.add_argument("--log-level=3")  # Suppress logs
options.add_argument("--incognito")  # Start in incognito mode

def init_driver():
    """Initialize and return a new WebDriver instance."""
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Start WebDriver
driver = init_driver()

# Open the website
url = "https://applipedia.paloaltonetworks.com/"
driver.get(url)

# Allow time for JavaScript to load
time.sleep(5)

# Extract table rows
rows = driver.find_elements(By.XPATH, '//tbody[@id="bodyScrollingTable"]/tr')

data = []
count = 0  # Progress counter
retries = 3  # Number of retries for each entry

for row in rows:
    count += 1  # Increment counter
    columns = row.find_elements(By.TAG_NAME, "td")

    if len(columns) >= 5:
        try:
            name_element = columns[0].find_element(By.TAG_NAME, "a")  # Link inside the Name column
            name = name_element.text.strip()
            category = columns[1].text.strip()
            subcategory = columns[2].text.strip()
            risk = columns[3].text.strip()
            technology = columns[4].text.strip()

            # Extract the 'onclick' attribute
            onclick_attr = name_element.get_attribute("onclick")  
            
            # Extract ID using regex
            app_id_match = re.search(r"ShowApplicationDetail\('(\d+)',", onclick_attr)
            app_id = app_id_match.group(1) if app_id_match else "N/A"

            # Retry logic for clicking
            for attempt in range(retries):
                try:
                    ActionChains(driver).move_to_element(name_element).click().perform()
                    break  # Exit loop if successful
                except Exception as e:
                    print(f"⚠️ Retry {attempt+1}/{retries} for {name}")
                    time.sleep(1)  # Wait before retrying
            
            # Extract standard ports and protocols
            try:
                ports_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'Standard Ports')]/following-sibling::td"))
                )
                standard_ports = ports_element.text.strip()
            except:
                standard_ports = "N/A"

            # Store the extracted data
            data.append([app_id, name, category, subcategory, risk, technology, standard_ports, onclick_attr])

            # Print progress
            print(f"✅ Processed {count}/{len(rows)}: {name} (ID: {app_id}) - Ports: {standard_ports}")

            # Close the popup (if required)
            try:
                close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ui-icon-closethick"))
                )
                close_button.click()
            except:
                print(f"⚠️ Could not close popup for {name}")

        except Exception as e:
            print(f"❌ Error processing {name}: {e}")
# Close browser
driver.quit()

# Convert to DataFrame and save
df = pd.DataFrame(data, columns=["App ID", "Name", "Category", "Subcategory", "Risk", "Technology", "Standard Ports", "OnClick"])
print(df.head())  # Display first few rows
df.to_csv("applipedia_data_with_onclick_fixed.csv", index=False)

print(f"✅ Data saved to 'applipedia_data_with_onclick_fixed.csv' (Total Processed: {count})")
