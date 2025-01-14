
from subprocess import PIPE
import tomllib as toml
import tomli_w
from packaging import version
from bs4 import BeautifulSoup
import requests as r
import subprocess
import json
import os
import webbrowser

update_arr = []
unavailable = []

def set_links():
    global asus_osid
    global amd_osid
    global driver_json
    global bios_json
    global amdsite
    global headers
    headers = {'User-Agent': 'lol'}

    iswin11 = "11" in subprocess.run("powershell.exe -EncodedCommand \"RwBlAHQALQBDAGkAbQBJAG4AcwB0AGEAbgBjAGUAIABXAGkAbgAzADIAXwBPAHAAZQByAGEAdABpAG4AZwBTAHkAcwB0AGUAbQAgAHwAIABTAGUAbABlAGMAdAAgAEMAYQBwAHQAaQBvAG4A\"", capture_output=True, text=True).stdout.strip("\n ")
    if iswin11:
        asus_osid = "52"
        amd_osid = 0
    else:
        asus_osid = "45"
        amd_osid = 9

    try:
        driver_response = r.get("https://www.asus.com/support/api/product.asmx/GetPDDrivers?website=us&pdid=10953&osid=" + asus_osid, headers=headers)
        driver_json = driver_response.json()
    except r.ConnectionError:
        print("ASUS driver API not available, skipping...")
        unavailable.append("networkdriver")
        unavailable.append("audiodriver")
        if not should_check_amdsite():
            unavailable.append("chipsetdriver")

    try:
        bios_response = r.get("https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=us&pdid=10953", headers=headers)
        bios_json = bios_response.json()
    except r.ConnectionError:
        print("ASUS bios API not available, skipping...")
        unavailable.append("bios")

    if should_check_amdsite():
        try:
            amdsite = r.get("https://www.amd.com/en/support/chipsets/amd-socket-am4/x570", headers=headers)
        except r.ConnectionError:
            print("AMD driver page not available, skipping...")
            unavailable.append("chipsetdriver")

def is_version(str):
    coolstr = str.replace(".", "")
    if coolstr.isdigit():
        return True
    return False

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
            if should_check_amdsite():
                version = BeautifulSoup(amdsite.text, 'html.parser').select('div.col-6 p')[amd_osid].text
            else:
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
            if should_check_amdsite():
                # AMD site does not say if it's a beta version
                is_release = True
            else:
                is_release = driver_json['Result']['Obj'][1]['Files'][0]['IsRelease']
        case "audiodriver":
            is_release  = driver_json['Result']['Obj'][2]['Files'][0]['IsRelease']

    if is_release == "0":
        return False
    # Also say it's a release if it can't find out
    else:
        return True

def create_config():
    data_dic = {
        "checks": {
            "bios": True,
            "networkdriver": True,
            "chipsetdriver": True,
            "audiodriver": True
        },
        "prefs": {
            "check_beta": True,
            "amdsite_check": False 
        },
        "ignore_version": {
            "bios": [],
            "networkdriver": [],
            "chipsetdriver": [],
            "audiodriver": []
        }
    }

    with open("config.toml", "wb") as configfile:
        tomli_w.dump(data_dic, configfile)
    

def should_check(to_check):
    if to_check in unavailable:
        return False
    with open("config.toml", "rb") as configfile:
        return toml.load(configfile)["checks"][to_check]

def should_check_beta():
    with open("config.toml", "rb") as configfile:
        return toml.load(configfile)["prefs"]["check_beta"]

def should_check_amdsite():
    with open("config.toml", "rb") as configfile:
        return toml.load(configfile)["prefs"]["amdsite_check"]

def should_check_version(to_check, version):
    with open("config.toml", "rb") as configfile:
        ignore_versions = toml.load(configfile)["ignore_version"][to_check]
        if version in ignore_versions:
            return True
        return False

def config_exists():
    return os.path.isfile("config.toml")

def check_corrupt():
    try:
        should_check("bios")
        should_check("networkdriver")
        should_check("chipsetdriver")
        should_check("audiodriver")
        should_check_version("bios", "1")
        should_check_version("networkdriver", "1")
        should_check_version("chipsetdriver", "1")
        should_check_version("audiodriver", "1")
        should_check_beta()
        should_check_amdsite()
    except:
        print("Corrupt config file, creating new file and renaming old one.")
        if os.path.isfile("config_corrupt.toml"):
            os.remove("config_corrupt.toml")
        os.rename("config.toml", "config_corrupt.toml")
        create_config()

def get_download_link(item):
    match item:
        case "bios":
            download_link = bios_json['Result']['Obj'][0]['Files'][0]['DownloadUrl']['Global']
        case "networkdriver":
            download_link = driver_json['Result']['Obj'][0]['Files'][0]['DownloadUrl']['Global']
        case "chipsetdriver":
            if should_check_amdsite():
                # AMD site does not allow direct downloads >:(
                download_link = "https://www.amd.com/en/support/downloads/drivers.html/chipsets/am4/x570.html"
            else:
                download_link = driver_json['Result']['Obj'][1]['Files'][0]['DownloadUrl']['Global']
        case "audiodriver":
            download_link = driver_json['Result']['Obj'][2]['Files'][0]['DownloadUrl']['Global']

    if "http" in download_link:
        return download_link
    else:
        print("Can't get download link.")
        return ""

def download_updates():
    answer = input("Would you like to download the update(s)? This will open your default browser. (Y/n)")
    if answer == "y" or answer == "":
        for update in update_arr:
            link = get_download_link(update)
            if not link == "":
                webbrowser.open(link)

def show_update_description():
    for update in update_arr:
        match update:
            case "bios":
                notes = bios_json['Result']['Obj'][0]['Files'][0]['Description']
            case "networkdriver":
                notes = driver_json['Result']['Obj'][0]['Files'][0]['Description']
            case "chipsetdriver":
                if should_check_amdsite():
                    notes = amdsite_releasenotes()
                else:
                    notes = driver_json['Result']['Obj'][1]['Files'][0]['Description']
            case "audiodriver":
                notes = driver_json['Result']['Obj'][2]['Files'][0]['Description']

        print(update.capitalize() + " update log")
        print("--------------------")
        if notes != "":
            print(notes + "\n")
        else:
            print("No update log")
        

def amdsite_releasenotes():
    version = get_newest_version("chipsetdriver")
    dash_version = version.replace(".", "-")
    mainlink = 'https://www.amd.com/en/resources/support-articles/release-notes/amd-ryzen--chipset-driver-release-notes-'
    fallbacklink = 'https://www.amd.com/en/resources/support-articles/release-notes/RN-RYZEN-CHIPSET-'

    try:
        response = r.get(mainlink + dash_version + '.html', headers=headers)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser').find('h2', string='Release Highlights').next_sibling.next_sibling.text
    except AttributeError:
        pass
    
    try:
        response = r.get(fallbacklink + dash_version + '.html', headers=headers)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'html.parser').find('h2', string='Release Highlights').next_sibling.next_sibling.text
    except AttributeError:
        pass
    
    return ""

def check_for_updates(to_check):
    print("\t- " + to_check.capitalize() + " -")

    installed = get_installed_version(to_check)
    newest = get_newest_version(to_check)

    if installed == -1 or newest == -1:
        return
    
    betastop = not (should_check_beta() or is_release(to_check))
    ignoreversionstop = should_check_version(to_check, newest)

    if version.parse(installed) < version.parse(newest) and not betastop and not ignoreversionstop:
        update_arr.append(to_check)
        print("There is a newer " + to_check + " available!")
        print("Installed version: " + installed)
        print("Newest version: " + newest)
        if not (is_release(to_check)):
            print("Warning! This is a beta version.")
    else:
        print("You have the latest " + to_check)
        print("Installed version: " + installed)
        
if not config_exists():
    print("No config found, creating...")
    create_config()

check_corrupt()
set_links()
if should_check("bios"):
    check_for_updates("bios")
    print()

if should_check("networkdriver"):
    check_for_updates("networkdriver")
    print()

if should_check("chipsetdriver"):
    check_for_updates("chipsetdriver")
    print()

if should_check("audiodriver"):
    check_for_updates("audiodriver")
    print()

if len(update_arr) > 0:
    show_update_description()
    print()
    download_updates()