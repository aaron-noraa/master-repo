import requests
from bs4 import BeautifulSoup
import json
import re

# URL of the Debian live CD images directory
BASE_URL = "https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/"

# Fetch page content
def fetch_iso_listing(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None

# Extract ISO or IMG links from HTML
def extract_files(html, extensions=[".iso", ".img"]):
    soup = BeautifulSoup(html, "html.parser")
    files = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and any(href.endswith(ext) for ext in extensions):
            files.append(href)
    return files

# Guess desktop environment from filename
def guess_de_flavor(filename):
    for de in ["gnome", "kde", "xfce", "lxde", "lxqt", "mate", "cinnamon"]:
        if de in filename.lower():
            return de.upper()
    return "Unknown"

# Convert to EchoBoot-style JSON entry
def build_json_entries(file_list):
    entries = []
    for f in file_list:
        match = re.search(r"debian-(\d{1,2})\.(\d+).*-(\w+)\.(iso|img)", f)
        if not match:
            continue
        major, minor, flavor, ext = match.groups()
        label = f"Debian {major}.{minor} {flavor.capitalize()}"
        codename = "bookworm" if major == "12" else "unknown"
        entry = {
            "label": label,
            "codename": codename,
            "version": f"{major}.{minor}",
            "flavor": flavor.lower(),
            "desktop": guess_de_flavor(f),
            "filename": f,
            "match_hints": [f"debian-{major}", flavor],
            "boot_params": "",
        }
        entries.append(entry)
    return entries

# Main flow
if __name__ == "__main__":
    html = fetch_iso_listing(BASE_URL)
    if html:
        iso_img_files = extract_files(html)
        print(f"[INFO] Found {len(iso_img_files)} files (.iso/.img)")
        entries = build_json_entries(iso_img_files)
        with open("debian_autogen.json", "w") as f:
            json.dump(entries, f, indent=2)
        print("[SUCCESS] JSON written to debian_autogen.json")
