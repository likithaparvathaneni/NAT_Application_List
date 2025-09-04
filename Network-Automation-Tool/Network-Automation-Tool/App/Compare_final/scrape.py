import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = "https://applipedia.paloaltonetworks.com/"

# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content of the page using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)
f=open("scrape.html","w")
f.write(str(soup))
f.close()