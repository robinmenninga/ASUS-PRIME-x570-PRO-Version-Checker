
from subprocess import PIPE
from packaging import version
import requests as r
import subprocess
import json
import os
import webbrowser

headers = {'User-Agent': 'lol'}
bios_json = r.get("https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=us&model=PRIME-X570-PRO&pdhashedid=aDvY2vRFhs99nFdl", headers=headers).json()

if "11" in subprocess.run("powershell.exe -EncodedCommand \"RwBlAHQALQBDAGkAbQBJAG4AcwB0AGEAbgBjAGUAIABXAGkAbgAzADIAXwBPAHAAZQByAGEAdABpAG4AZwBTAHkAcwB0AGUAbQAgAHwAIABTAGUAbABlAGMAdAAgAEMAYQBwAHQAaQBvAG4A\"", capture_output=True, text=True).stdout.strip("\n "):
    driver_json = r.get("https://www.asus.com/support/api/product.asmx/GetPDDrivers?website=us&model=PRIME-X570-PRO&pdhashedid=aDvY2vRFhs99nFdl&osid=52", headers=headers).json()
else:
    driver_json = r.get("https://www.asus.com/support/api/product.asmx/GetPDDrivers?website=us&model=PRIME-X570-PRO&pdhashedid=aDvY2vRFhs99nFdl&osid=45", headers=headers).json()

update_arr = []

def is_version(str):
    str.strip(".")
    for char in str:
        if not char.isdigit:
            return False
    return True

def get_installed_version(to_check):
    match to_check:
        case "bios":
            command = subprocess.run("wmic bios get name", stdout=PIPE, text=True)
            version = command.stdout.strip("Name \n")
        case "networkdriver":
            command = subprocess.run("powershell.exe -EncodedCommand \"RwBlAHQALQBXAG0AaQBPAGIAagBlAGMAdAAgAFcAaQBuADMAMgBfAFAAbgBQAFMAaQBnAG4AZQBkAEQAcgBpAHYAZQByACAALQBGAGkAbAB0AGUAcgAgACIARABlAHYAaQBjAGUATgBhAG0AZQAgAD0AIAAnAEkAbgB0AGUAbAAoAFIAKQAgAEkAMgAxADEAIABHAGkAZwBhAGIAaQB0ACAATgBlAHQAdwBvAHIAawAgAEMAbwBuAG4AZQBjAHQAaQBvAG4AJwAiACAAfAAgAHMAZQBsAGUAYwB0ACAAZAByAGkAdgBlAHIAdgBlAHIAcwBpAG8AbgAgAHwAIABGAG8AcgBtAGEAdAAtAFQAYQBiAGwAZQAgAC0ASABpAGQAZQBUAGEAYgBsAGUASABlAGEAZABlAHIAcwA=\"", capture_output=True, text=True)
            version = command.stdout.strip("\n ")
        case "chipsetdriver":
            command = subprocess.run("wmic datafile where 'name=\"C:\\\\Program Files (x86)\\\\AMD\\\\Chipset_Software\\\\AMD_Chipset_Drivers.exe\"' get version", capture_output=True, text=True)
            version = command.stdout.strip("Version \n")
        case "audiodriver":
            command = subprocess.run("powershell.exe -EncodedCommand \"RwBlAHQALQBXAG0AaQBPAGIAagBlAGMAdAAgAFcAaQBuADMAMgBfAFAAbgBQAFMAaQBnAG4AZQBkAEQAcgBpAHYAZQByACAALQBGAGkAbAB0AGUAcgAgACIARABlAHYAaQBjAGUATgBhAG0AZQAgAD0AIAAnAFIAZQBhAGwAdABlAGsAIABIAGkAZwBoACAARABlAGYAaQBuAGkAdABpAG8AbgAgAEEAdQBkAGkAbwAnACIAIAB8ACAAcwBlAGwAZQBjAHQAIABkAHIAaQB2AGUAcgB2AGUAcgBzAGkAbwBuACAAfAAgAEYAbwByAG0AYQB0AC0AVABhAGIAbABlACAALQBIAGkAZABlAFQAYQBiAGwAZQBIAGUAYQBkAGUAcgBzAA==\"", capture_output=True, text=True)
            version = command.stdout.strip("\n ")
    
    if is_version(version):
        return version
    else:
        print("Unable to get installed version.")
        return -1

def get_newest_version(to_check):
    match to_check:
        case "bios":
            version = bios_json['Result']['Obj'][0]['Files'][0]['Version']
        case "networkdriver":
            version = driver_json['Result']['Obj'][0]['Files'][0]['Version']
        case "chipsetdriver":
            version = driver_json['Result']['Obj'][1]['Files'][0]['Version']
        case "audiodriver":
            version = driver_json['Result']['Obj'][2]['Files'][0]['Version']

    if is_version(version):
        return version
    else:
        print("Unable to get newest version.")
        return -1

def is_release(to_check):
    match to_check:
        case "bios":
            is_release  = bios_json['Result']['Obj'][0]['Files'][0]['IsRelease']
        case "networkdriver":
            is_release  = driver_json['Result']['Obj'][0]['Files'][0]['IsRelease']
        case "chipsetdriver":
            is_release  = driver_json['Result']['Obj'][1]['Files'][0]['IsRelease']
        case "audiodriver":
            is_release  = driver_json['Result']['Obj'][2]['Files'][0]['IsRelease']

    if is_release == "0":
        return False
    # Also say it's a release if it can't find out
    else:
        return True

def create_config():
    dic_json = {
        "checks": {
            "bios": True,
            "networkdriver": True,
            "chipsetdriver": True,
            "audiodriver": True
        },
        "prefs": {
            "check_beta": True
        }
    }

    ser_json = json.dumps(dic_json, indent = 2)
    with open("config.json", "w") as configfile:
        configfile.write(ser_json)

def should_check(to_check):
    with open("config.json", "r") as configfile:
        return json.load(configfile)["checks"][to_check]

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

def get_download_link(item):
    match item:
        case "bios":
            download_link = bios_json['Result']['Obj'][0]['Files'][0]['DownloadUrl']['Global']
        case "networkdriver":
            download_link = driver_json['Result']['Obj'][0]['Files'][0]['DownloadUrl']['Global']
        case "chipsetdriver":
            download_link = driver_json['Result']['Obj'][1]['Files'][0]['DownloadUrl']['Global']
        case "audiodriver":
            download_link = driver_json['Result']['Obj'][2]['Files'][0]['DownloadUrl']['Global']

    if "http" in download_link:
        return download_link
    else:
        print("Can't get download link.")
        return ""

def download_updates():
    answer = input("Would you like to download the updates? This will open your default browser. (Y/n)")
    if answer == "y" or answer == "":
        for update in update_arr:
            link = get_download_link(update)
            webbrowser.open(link)

def show_update_description():
    for update in update_arr:
        match update:
            case "bios":
                notes = bios_json['Result']['Obj'][0]['Files'][0]['Description']
            case "networkdriver":
                notes = driver_json['Result']['Obj'][0]['Files'][0]['Description']
            case "chipsetdriver":
                notes = driver_json['Result']['Obj'][1]['Files'][0]['Description']
            case "audiodriver":
                notes = driver_json['Result']['Obj'][2]['Files'][0]['Description']

        print(update.capitalize() + " update log")
        print("--------------------")
        print(notes + "\n")

def check_for_updates(to_check):
    print("\t- " + to_check.capitalize() + " -")

    installed = get_installed_version(to_check)
    newest = get_newest_version(to_check)

    if installed == -1 or newest == -1:
        return
    
    betastop = not (should_check_beta() or is_release(to_check))

    if version.parse(installed) < version.parse(newest) and not betastop:
        update_arr.append(to_check)
        print("There is a newer " + to_check + " available!")
        print("Installed version: " + installed)
        print("Newest version: " + newest + "\n")
        if not (is_release(to_check)):
            print("Warning! This is a beta version.\n")
    else:
        print("You have the latest " + to_check)
        print("Installed version: " + installed + "\n")
        
if not config_exists():
    print("No config found, creating...")
    create_config()
    
check_corrupt()
if should_check("bios"):
    check_for_updates("bios")

if should_check("networkdriver"):
    check_for_updates("networkdriver")

if should_check("chipsetdriver"):
    check_for_updates("chipsetdriver")

if should_check("audiodriver"):
    check_for_updates("audiodriver")

if len(update_arr) > 0:
    show_update_description()
    download_updates()