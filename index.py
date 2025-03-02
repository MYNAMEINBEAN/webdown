import os
import requests
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

def download_website(url, output_folder="downloaded_site", zip_name="website.zip"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch website.")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    assets = []
    
    # Download and save the main HTML file
    html_path = os.path.join(output_folder, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    # Download assets (CSS, JS, Images)
    for tag in soup.find_all(["link", "script", "img"]):
        if tag.name == "link" and tag.get("rel") == ["stylesheet"]:
            src = tag.get("href")
        elif tag.name == "script" and tag.get("src"):
            src = tag.get("src")
        elif tag.name == "img" and tag.get("src"):
            src = tag.get("src")
        else:
            continue
        
        full_url = urljoin(url, src)
        file_path = os.path.join(output_folder, os.path.basename(urlparse(full_url).path))
        
        try:
            asset_data = requests.get(full_url).content
            with open(file_path, "wb") as asset_file:
                asset_file.write(asset_data)
            assets.append(file_path)
        except Exception as e:
            print(f"Failed to download {full_url}: {e}")
    
    # Create a ZIP archive
    zip_path = os.path.join(output_folder, zip_name)
    with ZipFile(zip_path, "w") as zipf:
        zipf.write(html_path, os.path.basename(html_path))
        for asset in assets:
            zipf.write(asset, os.path.basename(asset))
    
    print(f"Website downloaded and saved as {zip_path}")
    
if __name__ == "__main__":
    url = input("Enter the website URL: ")
    download_website(url)
