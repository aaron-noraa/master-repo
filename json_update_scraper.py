# json_update.py
# EchoBoot Feed Sync Script v0.1 "Pulse of the Mirrors"
# Purpose: Automatically scrape official distro mirrors or RSS feeds to update ISO/IMG release data

import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Define a base class for scraper modules
class MirrorScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_page(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Could not fetch {url}: {e}")
            return None

    def extract_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        return links

    def is_valid_iso_or_img(self, filename):
        return filename.endswith(".iso") or filename.endswith(".img")

    def parse_entries(self, links):
        raise NotImplementedError("parse_entries must be implemented by subclasses")

    def update_json(self, output_file):
        page = self.fetch_page(self.base_url)
        if not page:
            return
        links = self.extract_links(page)
        entries = self.parse_entries(links)
        with open(output_file, "w") as f:
            json.dump(entries, f, indent=2)
        print(f"[OK] Saved {len(entries)} entries to {output_file}")

# Debian Mirror Scraper (Example)
class DebianScraper(MirrorScraper):
    def parse_entries(self, links):
        entries = []
        for link in links:
            if self.is_valid_iso_or_img(link):
                version_match = re.search(r"(\d{1,2}\.\d+|\d{4})", link)
                flavor_match = re.search(r"(xfce|gnome|kde|lxde|lxqt|netinst|live)", link, re.IGNORECASE)
                label = link.replace("-", " ").replace(".iso", "").replace(".img", "").strip()
                entries.append({
                    "label": f"Debian {label.title()}",
                    "version": version_match.group(1) if version_match else "Unknown",
                    "codename": "",
                    "flavor": flavor_match.group(1).upper() if flavor_match else "Standard",
                    "filename": link,
                    "match_hints": [link.lower()],
                    "boot_params": ""
                })
        return entries

if __name__ == "__main__":
    debian_url = "https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/"
    scraper = DebianScraper(debian_url)
    scraper.update_json("debian_autogen.json")
