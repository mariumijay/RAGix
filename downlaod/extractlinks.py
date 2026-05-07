import requests
from bs4 import BeautifulSoup

url = "https://www.freeilm.com/9th-class-urdu-notes-pdf-matric-part-1/"

res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

links = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    if "drive.google.com" in href:
        links.append(href)

# remove duplicates
links = list(set(links))

print(f"Found {len(links)} links:\n")

for i, link in enumerate(links, 1):
    print(f"{i}: {link}")