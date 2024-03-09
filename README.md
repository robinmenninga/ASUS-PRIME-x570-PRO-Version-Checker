# ASUS PRIME x570 PRO Version Checker - Python edition

A script that checks if you have the latest PRIME x570-PRO bios, audio driver, network driver and chipset, made in python.

# Pip dependencies
- packaging
- requests
- beautifulsoup4
- tomli-w

# Linux dependencies
- dmidecode

# Installation
After cloning the repo, start by installing all the dependencies. You can do this by executing the command `pip install [package]`.

# Usage
On Windows, simply execute the provided bat file. You can also open command prompt and execute the command `python check_version.py` (which is what the bat file does).

On Linux, run the command `python check_version_linux.py` or `./check_version_linux.py`.

# Configuration
After running the script at least once, a configuration file will be made (config.toml).

- The checks section allows you to enable and disable version checking.
- The prefs section allows you to set different preferences. Currently you can enable and disable beta version checking and choose whether to use the site of AMD or ASUS to check for chipset updates.
- The ignore_version section allows you to ignore versions. Make sure to put the version in quotes or it won't work!
