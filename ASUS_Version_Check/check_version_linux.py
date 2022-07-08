
from subprocess import PIPE
from packaging import version
import requests as r
import subprocess
import json
import os
import webbrowser

headers = {'User-Agent': 'lol'}
bios_json = r.get("https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=us&model=PRIME-X570-PRO&pdhashedid=aDvY2vRFhs99nFdl", headers=headers).json()

global update
update = False

def is_version(str):
    str.strip(".")
    for char in str:
        if not char.isdigit:
            return False
    return True

def get_installed_version():
    version = subprocess.run("sudo dmidecode -s bios-version", stdout=PIPE, text=True).stdout.strip()
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
    dic_json = {
        "prefs": {
            "check_beta": True
        }
    }

    ser_json = json.dumps(dic_json, indent = 2)
    with open("config.json", "w") as configfile:
        configfile.write(ser_json)

def should_check_beta():
    with open("config.json", "r") as configfile:
        return json.load(configfile)["prefs"]["check_beta"]

def config_exists():
    return os.path.isfile("config.json")

def check_corrupt():
    try:
        with open("config.json", "r") as configfile:
            json.load(configfile)
    except ValueError:
        print("Corrupt config file, creating new file and renaming old one.")
        if os.path.isfile("config_corrupt.json"):
            os.remove("config_corrupt.json")
        os.rename("config.json", "config_corrupt.json")
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
    print(notes + "\n")

def check_for_updates():
    print("\t- Bios -")

    installed = get_installed_version()
    newest = get_newest_version()

    if installed == -1 or newest == -1:
        return
    
    betastop = not (should_check_beta() or is_release())

    if version.parse(installed) < version.parse(newest) and not betastop:
        print("There is a newer Bios available!")
        print("Installed version: " + installed)
        print("Newest version: " + newest + "\n")
        if not (is_release()):
            print("Warning! This is a beta version.\n")
        return True
    else:
        print("You have the latest Bios")
        print("Installed version: " + installed + "\n")
        
if not config_exists():
    print("No config found, creating...")
    create_config()
    
check_corrupt()
if check_for_updates():
    show_update_description()
    download_updates()