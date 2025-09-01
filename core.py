# EchoBoot v0.7 - "Liminal Flame" Edition
# Refactored base module from Gemini EchoBoot v.2
# This file: core.py (main CLI logic and backend functions)

import os
import platform
import subprocess
import time
import zipfile
import requests
import psutil
import shutil
import json

# Constants
REFIND_URL = "https://sourceforge.net/projects/refind/files/latest/download"
SYSLINUX_URL = "https://www.kernel.org/pub/linux/utils/boot/syslinux/syslinux-6.03.zip"
DOWNLOAD_DIR = "temp_downloads"
EXTRACT_DIR = "temp_extracted"
BOOT_PARTITION_LABEL = "BOOT"
DATA_PARTITION_LABEL = "DATA"
BOOT_PARTITION_SIZE_MB = 200
ISO_DEFINITIONS_FILE = "iso_definitions.json"

# --- Utility Functions ---
def print_info(msg): print(f"[INFO] {msg}")
def print_warn(msg): print(f"[WARN] {msg}")
def print_error(msg): print(f"[ERROR] {msg}"); exit(1)

def run_command(command, shell=False):
    try:
        process = subprocess.Popen(
            command, shell=shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print_error(f"Command failed: {' '.join(command)}\n{stderr}")
        return stdout.strip()
    except FileNotFoundError:
        print_error(f"Command not found: {command[0]}")

# --- Drive Detection ---
def get_removable_drives():
    # Platform-specific drive detection...
    # (Trimmed for brevity, will re-add full cross-platform in final build)
    return []

def select_drive():
    drives = get_removable_drives()
    if not drives: print_error("No USB drives found.")
    # Prompt user choice...
    return drives[0]['device']

# --- Partitioning ---
def partition_and_format(device):
    system = platform.system()
    print_info(f"Partitioning {device} on {system}...")
    # Trimmed for brevity: unmount + parted/diskutil/diskpart

# --- Bootloader Installation ---
def install_bootloaders(device):
    mount_point = get_mount_point(BOOT_PARTITION_LABEL)
    if not mount_point:
        print_error(f"Couldn't find mount for BOOT.")
    print_info("Installing bootloaders...")
    # Download and install rEFInd and Syslinux (trimmed)

# --- Mount Helpers ---
def get_mount_point(label):
    for part in psutil.disk_partitions(all=True):
        if label in part.mountpoint: return part.mountpoint
    return None

# --- Boot Entry Logic ---
def match_iso_to_definition(iso_name, definitions):
    for entry in definitions:
        for hint in entry.get("match_hints", []):
            if hint.lower() in iso_name.lower():
                return entry
    return None

def update_boot_entries():
    print_info("Scanning for ISOs...")
    if not os.path.exists(ISO_DEFINITIONS_FILE):
        print_warn("No iso_definitions.json found.")
        return

    with open(ISO_DEFINITIONS_FILE, 'r') as f:
        definitions = json.load(f)

    boot_mount = get_mount_point(BOOT_PARTITION_LABEL)
    data_mount = get_mount_point(DATA_PARTITION_LABEL)
    if not (boot_mount and data_mount):
        print_error("Cannot find BOOT/DATA partitions.")

    isos = [f for f in os.listdir(data_mount) if f.endswith(".iso")]
    if not isos:
        print_warn("No ISOs found on DATA partition.")
        return

    syslinux_cfg = []
    refind_cfg = []

    for iso in isos:
        match = match_iso_to_definition(iso, definitions)
        if not match:
            print_warn(f"No match for {iso}")
            continue
        print_info(f"Matched {iso} to {match['label']}")
        syslinux_cfg.append(f"\nLABEL {match['codename'].lower()}{match['version']}\n  MENU LABEL {match['label']}\n  LINUX memdisk\n  INITRD /{iso}\n  APPEND iso\n")
        refind_cfg.append(f"\nmenuentry \"{match['label']}\" {{\n  disabled\n  loader /EFI/tools/loader.efi\n  initrd /{iso}\n}}\n")

    # Write to syslinux.cfg
    with open(os.path.join(boot_mount, "syslinux.cfg"), 'a') as f:
        f.write("\n# --- Auto-generated ---\n")
        f.writelines(syslinux_cfg)

    with open(os.path.join(boot_mount, "EFI", "BOOT", "refind.conf"), 'a') as f:
        f.write("\n# --- Auto-generated ---\n")
        f.writelines(refind_cfg)

    print_info("Boot entries updated.")

# --- Entry Point ---
def main():
    print_info("Welcome to EchoBoot v0.7 – Liminal Flame Edition")
    device = select_drive()
    print_warn(f"ALL DATA on {device} will be erased.")
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != "yes": return
    partition_and_format(device)
    install_bootloaders(device)
    input("Copy ISOs to DATA partition. Press Enter when done.")
    update_boot_entries()
    print_info("Complete.")

if __name__ == "__main__":
    main()
