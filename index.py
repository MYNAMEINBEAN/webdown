import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

def download_website(url, output_folder="downloaded_site", zip_name="website.zip"):
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    assets = []
    
    html_path = os.path.join(output_folder, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    for tag in soup.find_all(["link", "script", "img"]):
        src = tag.get("href") if tag.name == "link" else tag.get("src")
        if not src:
            continue
        
        full_url = urljoin(url, src)
        file_name = os.path.basename(urlparse(full_url).path)
        file_path = os.path.join(output_folder, file_name)
        
        try:
            asset_data = requests.get(full_url).content
            with open(file_path, "wb") as asset_file:
                asset_file.write(asset_data)
            assets.append(file_path)
        except requests.RequestException:
            print(f"Failed to download {full_url}")
    
    zip_path = os.path.join(output_folder, zip_name)
    with ZipFile(zip_path, "w") as zipf:
        zipf.write(html_path, os.path.basename(html_path))
        for asset in assets:
            zipf.write(asset, os.path.basename(asset))
    
    print(f"Website downloaded and saved as {zip_path}")
    
if __name__ == "__main__":
    url = input("Enter the website URL: ")
    download_website(url)
