import requests
from bs4 import BeautifulSoup
import json
import re

BASE_URL = "https://download.freebsd.org/ftp/releases/amd64/"
OUTPUT_FILE = "freebsd_autogen.json"

def get_release_links():
    print(f"Fetching FreeBSD directory: {BASE_URL}")
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        print(f"Failed to fetch base directory: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    dirs = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if re.match(r"\d+\.\d+[-RELEASE]+\/", href):
            dirs.append(href.strip('/'))
    return dirs

def get_iso_and_img_links(release):
    iso_img_files = []
    url = f"{BASE_URL}{release}/"
    print(f"Scanning release: {release}")
    resp = requests.get(url)
    if resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    for link in soup.find_all('a'):
        href = link.get('href')
        if href.endswith((".iso", ".img")):
            iso_img_files.append((release, href))
    return iso_img_files

def generate_entry(release, filename):
    version = release.split('-')[0]
    filetype = "ISO" if filename.endswith(".iso") else "IMG"
    arch = "amd64" if "amd64" in filename else "unknown"

    return {
        "codename": f"FreeBSD-{version}",
        "label": f"FreeBSD {version} ({filetype})",
        "version": version,
        "kernel": None,
        "initrd": None,
        "boot_params": None,
        "match_hints": [filename, release],
        "category": "BSD",
        "desktop": "None",
        "architecture": arch,
        "file_type": filetype,
        "filename": filename,
        "url": f"{BASE_URL}{release}/{filename}"
    }

def main():
    releases = get_release_links()
    results = []

    for rel in releases:
        items = get_iso_and_img_links(rel)
        for rel_name, file in items:
            entry = generate_entry(rel_name, file)
            results.append(entry)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
