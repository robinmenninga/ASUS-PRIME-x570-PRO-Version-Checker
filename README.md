# ASUS PRIME x570 PRO Version Checker - Python edition

A script that checks if you have the latest PRIME x570-PRO bios, audio driver, network driver and chipset, made in python.

# Pip dependencies
- packaging
- requests

# Linux dependencies
- dmidecode

# Installation
After cloning the repo, start by installing all the dependencies. You can do this by executing the command `pip install [package]`.

# Usage
On Windows, simply execute the provided bat file. You can also open command prompt and execute the command `python check_version.py` (which is what the bat file does).

On Linux, run the command `python check_version_linux.py` or `./check_version_linux.py`.

# Configuration
After running the script at least once, a configuration file will be made (config.json). You can choose what you want to be checked by the script by editing the variables in this json file. It is also possible to ignore beta versions. By default, the script will check everything and will also notice you of any beta versions.

On Linux it's only possible to ignore ignore beta versions.
