#!/usr/bin/python3

import subprocess

def get_category(app_id):
    # Befehl als Variable definieren
    cmd = "appstreamcli dump "+app_id+" | grep '<category>.*</category>'"

    try:
        # Ausführen des Befehls
        process = subprocess.run(
            cmd,                       # Verwenden der cmd-Variable
            shell=True,                # Shell verwenden, da Pipe verwendet wird
            check=True,                # Fehler werfen, falls der Befehl fehlschlägt
            stdout=subprocess.PIPE,    # Standardausgabe erfassen
            stderr=subprocess.PIPE,    # Fehlerausgabe erfassen
            text=True                  # Ausgabe als String zurückgeben
        )

        # Ausgabe extrahieren
        output = process.stdout
        cat_raw = output[0]
        cat= cat_raw[cat_raw.find(">"):cat_raw.find("</")]            
        return cat

    except subprocess.CalledProcessError as e:
        # Fehler behandeln und ausgeben
        print(f"Ein Fehler ist aufgetreten: {e.stderr}")

def get_list():
    # Befehl als Variable definieren
    cmd = "flatpak remote-ls --app| awk -F'\t' '{print $2}'"

    try:
        # Ausführen des Befehls
        process = subprocess.run(
            cmd,                       # Verwenden der cmd-Variable
            shell=True,                # Shell verwenden, da Pipe verwendet wird
            check=True,                # Fehler werfen, falls der Befehl fehlschlägt
            stdout=subprocess.PIPE,    # Standardausgabe erfassen
            stderr=subprocess.PIPE,    # Fehlerausgabe erfassen
            text=True                  # Ausgabe als String zurückgeben
        )

        # Ausgabe extrahieren
        output = process.stdout.splitlines()
        return output

    except subprocess.CalledProcessError as e:
        # Fehler behandeln und ausgeben
        print(f"Ein Fehler ist aufgetreten: {e.stderr}")

list = get_list()
for line in list:
    cat = get_category(line)
    if cat:    
        print(f"app: {line}\tcategory: {cat}")




