#!/usr/bin/python3

import os
import json
import requests
import subprocess
import re
from bs4 import BeautifulSoup


def loadSavedData():
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            program_data = json.load(f)
        return program_data
    elif os.path.exists(bak_file):
        with open(bak_file, "r") as f:
            program_data = json.load(f)
        return program_data
    else:
        return {}

def check_category(app_categories):
    categories = [
    "Game",
    "Office",
    "Graphics",
    "AudioVideo",
    "Utility",
    "Network",
    "Education",
    "Science",
    "Development",
    "System"]
    for wort1 in categories:
        for wort2 in app_categories:
            if wort1 == wort2:  # Exakter Vergleich
                return wort1
    return "Other"

def get_flatpak_info(app_id):
    url = f"https://flathub.org/api/v2/appstream/{app_id}"
    
    try:
        # HTTP GET request
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        #print(f"[debug] {data}")

        # Extract description and screenshots
        description = data.get("description", [])
        screenshots = data.get("screenshots", [])
        app_categories = data.get("categories", [])
        icon_url = data.get("icon", [])[0]
        if icon_url:
            download_icon(app_id, icon_url, icons_path)

        screenshot_url = ""
        if screenshots:
            screenshot = screenshots[0]
            size = screenshot.get("sizes", [])[0]
            screenshot_url = size.get("src")
        return  screenshot_url, description,app_categories
    
    except requests.exceptions.RequestException as e:
        if e.response.status_code == 404:
            #print(f"404 - App nicht gefunden: {app_id}")
            return "", "" , ["none"]
        else: 
            #print(f"An error occurred: {e}")
            return "", "" , ["none"]


def only_icon(app_id):
    url = f"https://flathub.org/api/v2/appstream/{app_id}"
    
    try:
        # HTTP GET request
        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        #print(f"[debug] {data}")

        # Extract description and screenshots
        icon_url = data.get("icon", [])
        print(icon_url)
        if icon_url:
            download_icon(app_id, icon_url, icons_path)

    except requests.exceptions.RequestException as e:
        if e.response.status_code == 404:
            #print(f"404 - App nicht gefunden: {app_id}")
            return "", "" , ["none"]
        else: 
            #print(f"An error occurred: {e}")
            return "", "" , ["none"]


def download_icon(app_id, url, folder="/tmp/"):
    os.makedirs(folder, exist_ok=True)
    icon_path = os.path.join(folder, f"{app_id}.png")
    if not os.path.exists(icon_path):
        r = requests.get(url)
        if r.status_code == 200:
            with open(icon_path, "wb") as f:
                f.write(r.content)
            print(f"Icon für {app_id} gespeichert.")
    return icon_path


def translate_text(text, source="en", target="de"):
    if os.path.exists(trans_file):
        result = subprocess.run(
            [trans_file, f"-b", f":{target}", str(text)],
            stdout=subprocess.PIPE,
            text=True
        )
        #print("[debug]",str(result.stdout.strip()))
        return str(result.stdout.strip())
    else:
        cmd=f"cd {config_dir} && wget git.io/trans && chmod +x ./trans"
        os.system(cmd)
        result = subprocess.run(
            [trans_file, f"-b", f":{target}", str(text)],
            stdout=subprocess.PIPE,
            text=True
        )
        #print("[debug]",str(result.stdout.strip()))
        return str(result.stdout.strip())


def get_all_apps():
    try:
        result = subprocess.run(
            ["flatpak", "remote-ls", "--app", "--columns=name,application,version,installed-size,description"],
            capture_output=True,
            text=True,  # Dekodiert die Ausgabe als String
            check=True  # Wirft eine CalledProcessError, wenn der Befehl fehlschlägt
        )
        output = result.stdout

        # Verarbeitung mit awk in Python (effizienter als externer awk-Aufruf)
        app_names = []
        app_ids = []
        app_versions = []
        app_sizes = []
        app_desc_shorts = []
        for line in output.splitlines():
            parts = line.split('\t')
            #print(parts,len(parts))
            if len(parts) > 1:
                app_names.append(parts[0])
                app_ids.append(parts[1])
                app_versions.append(parts[2])
                app_sizes.append(parts[3])
            if len(parts) > 4:
                app_desc_shorts.append(parts[4])
            else: 
                app_desc_shorts.append(" ")

        return app_ids, app_names, app_versions, app_sizes, app_desc_shorts

    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen von flatpak: {e}")
        print(f"Stderr: {e.stderr}") # Gibt Fehlermeldungen aus
        return None
    except FileNotFoundError:
        print("Fehler: flatpak ist nicht installiert.")
        return None

## Hauptprogramm
icons_path = os.path.expanduser("~/.config/x-live/flatman/icons/")
raw_path = "~/.config/x-live/flatman/program_data.json"
data_file = os.path.expanduser(raw_path)
bak_file = "/usr/share/x-live/flatman/program_data.json"
config_dir = os.path.expanduser("~/.config/x-live/flatman/")
trans_file = config_dir + "trans"
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

program_data = loadSavedData()  # Speichert die Kategorie, URL und Details der Programme

os.system("appstreamcli refresh-cache 1>>/dev/null")

names = {
    "Game":"Spiele",
    "Office":"Büro",
    "Graphics":"Grafik",
    "AudioVideo":"AudioVideo",
    "Utility":"Zubehör",
    "Network":"Internet",
    "Education":"Bildung",
    "Science":"Wissenschaft",
    "Development":"Entwicklung",
    "System":"System",
    "Other":"Andere"
}

#program_data = {}
zaehler = 0
app_ids, app_names, app_versions, app_sizes, app_desc_shorts = get_all_apps()
count_cmd = f"echo Daten zu 0% aktuallisiert 0 Apps erfasst !!"
os.system(count_cmd)
for x,app in enumerate(app_ids):
    pro = int(x/len(app_ids)*100)
    app_name = app_names[x].strip()
    app_id = app
    app_version = app_versions[x].strip()
    app_size = app_sizes[x].strip()
    app_short_desc = app_desc_shorts[x].strip()
    icon_path = os.path.join(icons_path, f"{app_id}.png")


    if program_data.get(app_name, {}).get("id") == None:
        
        thumbnail, description_en, app_categories = get_flatpak_info(app_id)
        checked_cat = check_category(app_categories)
        category_name = names[checked_cat]
        if app_categories != ["none"]:
            zaehler = zaehler + 1
            program_data[app_name] = {
                "category": category_name,
                "id": app_id,
                "description": translate_text(description_en),
                "thumbnail": thumbnail,
                "version": app_version,
                "size": app_size,
                "short-desc": translate_text(app_short_desc)
            }
            #cmd_name = f"echo !!! {app_name} datenbank hinzugefügt !!!"
            #os.system(cmd_name)
    elif not os.path.exists(icon_path):
        only_icon(app_id)

    count_cmd = f"echo Daten zu {pro}% aktuallisiert {x+1}/{len(app_ids)+1} Apps erfasst !! {zaehler} Apps hinzugefügt "
    os.system(count_cmd)

output_dir = os.path.dirname(data_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    #print(f"[DEBUG] Verzeichnis erstellt: {output_dir}")

with open(data_file, "w") as f:
    json.dump(program_data, f)
#print(f"[DEBUG] Daten gespeichert in: {data_file}")
