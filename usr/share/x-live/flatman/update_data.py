#!/usr/bin/python3


import os
import json
import requests
import subprocess
import re
from bs4 import BeautifulSoup

data_file = "/tmp/x-live/flatpak/program_data.json"
program_data = {}  # Speichert die Kategorie, URL und Details der Programme

os.system("appstreamcli refresh-cache 1>>/dev/null")
#cmd = ["python3", "/usr/share/x-live/flatman/warten.py"]  # Beispielprogramm; passe dies an das Programm an, das du starten möchtest

# Starten des Prozesses ohne Einfluss auf das Hauptprogramm
#process = subprocess.Popen(
#    cmd,
#    start_new_session=True,  # Startet den Prozess in einer neuen Sitzung
#    stdout=subprocess.DEVNULL,  # Verhindert Ausgabe des gestarteten Prozesses in der Konsole
#    stderr=subprocess.DEVNULL,  # Verhindert Fehlerausgabe in der Konsole
##)

base_urls = [
    "https://flathub.org/apps/collection/popular/",
    "https://flathub.org/de/apps/collection/trending/",
    "https://flathub.org/de/apps/collection/recently-added/",
    "https://flathub.org/de/apps/category/Game/",
    "https://flathub.org/de/apps/category/Office/",
    "https://flathub.org/de/apps/category/Graphics/",
    "https://flathub.org/de/apps/category/AudioVideo/",
    "https://flathub.org/de/apps/category/Utility/",
    "https://flathub.org/de/apps/category/Network/",
    "https://flathub.org/de/apps/category/Education/",
    "https://flathub.org/de/apps/category/Science/",
    "https://flathub.org/de/apps/category/Development/",
    "https://flathub.org/de/apps/category/System/"
]

names = {
    "popular":"Beliebt",
    "trending":"Im Trend",
    "recently-added":"Neu hinzugefügt",
    "Game":"Spiele",
    "Office":"Büro",
    "Graphics":"Grafik",
    "AudioVideo":"AudioVideo",
    "Utility":"Zubehör",
    "Network":"Internet",
    "Education":"Bildung",
    "Science":"Wissenschaft",
    "Development":"Entwicklung",
    "System":"System"
}

categories_ordered = ["Beliebt","Im Trend","Neu hinzugefügt","Spiele","Büro","Grafik","AudioVideo","Zubehör","Internet","Bildung","Wissenschaft","Entwicklung","System"]  # Geordnete Liste der Kategorien
categories_ordered = []  # Zurücksetzen der geordneten Liste
program_data = {}
counter=0

for base_url in base_urls:
    category_base = base_url.split('/')[-2]
    category_name = names[category_base]
    counter = counter + 1
    pro = int(counter/len(base_urls)*100)
    count_cmd = f"echo Daten zu {pro}% aktuallisiert"
    os.system(count_cmd)
    categories_ordered.append(category_name)  # Kategorien in der gewünschten Reihenfolge speichern
    page_number = 1
    while True:
        url = f"{base_url}{page_number}"
        #print(f"[DEBUG] Sende Anfrage an: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            break

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            app_links = soup.find_all("a", class_="bg-flathub-white")
            if not app_links:
                break

            for link in app_links:
                app_name_tag = link.find("span", class_="truncate")
                if app_name_tag:
                    app_name = app_name_tag.text.strip()
                    app_url = "https://flathub.org" + link.get("href")
                    #print(app_url)
                    program_data[app_name] = {
                        "category": category_name,
                        "url": app_url
                    }

            page_number += 1

        except Exception as e:
            #print(f"[ERROR] Fehler beim Verarbeiten der Seite: {e}")
            break

#command = ['pkill', '-f', 'python3 /usr/share/x-live/flatman/warten.py']        
#result = subprocess.run(command, text=True)

output_dir = os.path.dirname(data_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    #print(f"[DEBUG] Verzeichnis erstellt: {output_dir}")

with open(data_file, "w") as f:
    json.dump(program_data, f)
#print(f"[DEBUG] Daten gespeichert in: {data_file}")
