#!/usr/bin/env python3

from subprocess import PIPE
import tomllib as toml
import tomli_w
from packaging import version
import requests as r
import subprocess
import json
import os
import webbrowser

global bios_json

def is_version(str):
    coolstr = str.replace(".", "")
    if coolstr.isdigit():
        return True
    return False

def get_installed_version():
    version = subprocess.run(["sudo", "dmidecode", "-s", "bios-version"], stdout=PIPE, text=True).stdout.strip()
    if is_version(version):
        return version
    else:
        print("Unable to get installed version.")
        return -1

def get_newest_version():
    version = bios_json['Result']['Obj'][0]['Files'][0]['Version']

    if is_version(version):
        return version
    else:
        print("Unable to get newest version.")
        return -1

def is_release():
    is_release  = bios_json['Result']['Obj'][0]['Files'][0]['IsRelease']

    if is_release == "0":
        return False
    # Also say it's a release if it can't find out
    else:
        return True

def create_config():
    data_dic = {
        "prefs": {
            "check_beta": True
        },
        "ignore_version": {
            "bios": []
        }
    }

    with open("config.toml", "wb") as configfile:
        tomli_w.dump(data_dic, configfile)

def should_check_beta():
    with open("config.toml", "rb") as configfile:
        return toml.load(configfile)["prefs"]["check_beta"]

def should_check_version(version):
    with open("config.toml", "rb") as configfile:
        ignore_versions = toml.load(configfile)["ignore_version"]["bios"]
        if version in ignore_versions:
            return True
        return False

def config_exists():
    return os.path.isfile("config.toml")

def check_corrupt():
    try:
        should_check_beta()
        should_check_version("1")
    except:
        print("Corrupt config file, creating new file and renaming old one.")
        if os.path.isfile("config_corrupt.toml"):
            os.remove("config_corrupt.toml")
        os.rename("config.toml", "config_corrupt.toml")
        create_config()

def get_download_link():
    download_link = bios_json['Result']['Obj'][0]['Files'][0]['DownloadUrl']['Global']

    if "http" in download_link:
        return download_link
    else:
        print("Can't get download link.")
        return ""

def download_updates():
    answer = input("Would you like to download the update(s)? This will open your default browser. (Y/n)")
    if answer == "y" or answer == "":
        link = get_download_link()
        if not link == "":
            webbrowser.open(link)

def show_update_description():
    notes = bios_json['Result']['Obj'][0]['Files'][0]['Description']

    print("Bios update log")
    print("--------------------")
    if notes != "":
        print(notes + "\n")
    else:
        print("No update log")

def check_for_updates():
    print("\t- Bios -")

    installed = get_installed_version()
    newest = get_newest_version()

    if installed == -1 or newest == -1:
        return
    
    betastop = not (should_check_beta() or is_release())
    ignoreversionstop = should_check_version(newest)

    if version.parse(installed) < version.parse(newest) and not betastop and not ignoreversionstop:
        print("There is a newer Bios available!")
        print("Installed version: " + installed)
        print("Newest version: " + newest)
        if not (is_release()):
            print("Warning! This is a beta version.")
        return True
    else:
        print("You have the latest Bios")
        print("Installed version: " + installed)
        
if not config_exists():
    print("No config found, creating...")
    create_config()
    
check_corrupt()
try:
    headers = {'User-Agent': 'lol'}
    bios_response = r.get("https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=us&model=PRIME-X570-PRO&pdhashedid=aDvY2vRFhs99nFdl", headers=headers)
    bios_json = bios_response.json()
    if check_for_updates():
        print()
        show_update_description()
        print()
        download_updates()
except r.ConnectionError:
    print("ASUS bios API not available")
