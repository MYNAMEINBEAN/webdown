from flask import Flask, request, render_template_string
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Downloader</title>
</head>
<body>
    <h1>Website Downloader</h1>
    <form action="/download" method="post">
        <label for="url">Enter Website URL:</label>
        <input type="text" id="url" name="url" required>
        <button type="submit">Download</button>
    </form>
</body>
</html>
"""

def download_website(url, output_folder="downloaded_site", zip_name="website.zip"):
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching website: {e}"
    
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
            continue
    
    zip_path = os.path.join(output_folder, zip_name)
    with ZipFile(zip_path, "w") as zipf:
        zipf.write(html_path, os.path.basename(html_path))
        for asset in assets:
            zipf.write(asset, os.path.basename(asset))
    
    return f"Website downloaded and saved as {zip_path}"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    result = download_website(url)
    return f"<p>{result}</p><a href='/'>Go back</a>"

if __name__ == "__main__":
    app.run(debug=True)
