import requests
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

# Function to create directory structure based on URL path
def create_dir_structure(url, base_dir="downloads"):
    parsed_url = urlparse(url)
    path = parsed_url.path.lstrip('/').rstrip('/')
    dir_path = os.path.join(base_dir, path)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

# Function to download and save images
def download_images(soup, base_url, save_dir):
    for img in soup.find_all('img'):
        img_url = img.get('src')
        img_url = urljoin(base_url, img_url)
        img_name = os.path.basename(img_url)

        try:
            img_resp = requests.get(img_url)
            if img_resp.status_code == 200:
                img_path = os.path.join(save_dir, img_name)
                with open(img_path, 'wb') as img_file:
                    img_file.write(img_resp.content)
                print(f"Downloaded image: {img_name}")
                img['src'] = os.path.relpath(img_path, start=save_dir)
            else:
                print(f"Failed to download image: {img_name}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading the image {img_name}: {e}")

# Function to process a URL
def process_url(url, base_dir="downloads", base_path="", visited=set()):
    if url in visited:
        return
    visited.add(url)

    try:
        resp = requests.get(url)
        print(f"Status Code ({url}):", resp.status_code)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            save_dir = create_dir_structure(url, base_dir)
            download_images(soup, url, save_dir)

            markdown_content = md(
                soup.prettify(),
                heading_style="ATX",
                bullets="-",
            )

            output_file_path = os.path.join(save_dir, 'output.md')
            with open(output_file_path, 'w') as file:
                file.write(markdown_content)

            print(f"\nMarkdown content has been written to {output_file_path}")

            links = [a.get('href') for a in soup.find_all('a', href=True)]
            for link in links:
                link_url = urljoin(url, link)
                if link_url.startswith(base_path):
                    process_url(link_url, base_dir, base_path, visited)
        else:
            print(f"Failed to retrieve the content from {url}. Status code:", resp.status_code)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request to {url}: {e}")

# Define the URL of the website to scrape and the base path to limit the scope
BASE_URL = "https://www.chemedx.org/JCESoft/jcesoftSubscriber/CCA/CCA3/"
process_url(BASE_URL, base_path=BASE_URL)