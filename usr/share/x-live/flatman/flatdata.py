#!/usr/bin/python3

import subprocess
import sys, os

sections=["[Context]","[Session Bus Policy]","[System Bus Policy]","[Environment]"]

# Aktuelle Umgebungsvariablen kopieren
env = os.environ.copy()
env["LC_ALL"] = "C"

def get_overridedata(app_id, user=True):
    scope = "--user" if user else "--system"
    try:
        result = subprocess.run(
            ["flatpak", "override", "--show", scope, app_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
            env=env
        )
        #print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""

def get_data(app_id):
    try:
        raw_info = subprocess.run(
            ["flatpak", "info", "--show-metadata", app_id],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
            env=env
        ).stdout
        #print(raw_info)
        return raw_info
    except subprocess.CalledProcessError:
        print("❌ App nicht gefunden oder Flatpak nicht installiert.")
        return

def get_name(app_id):
    try:
        result = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application,name"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
            env=env
        ).stdout
        apps = result.splitlines()
        for app in apps:
            name = app.split("\t")[1]
            search_id = app.split("\t")[0]
            if app_id == search_id:
                return name
        return 
    except subprocess.CalledProcessError:
        print("❌ App nicht gefunden oder Flatpak nicht installiert.")
        return
        
def get_more_info(app_id):    
    pass


def parse_data(raw_data,permissions_context):
    active_section = None
    raw_sec = []
    
    data = raw_data.splitlines()
    for line in data:
        if line in sections:
            raw_sec.append(line)
            active_section = line.replace("[","").replace("]","")
            next
        if line.startswith("[") and line not in sections:
            active_section = None
            next
        elif active_section == "Context":
            permissions_context = parse_context(line,permissions_context)
        elif active_section == "Session Bus Policy":
            permissions_context = parse_session(line,permissions_context)
        elif active_section == "System Bus Policy":
            permissions_context = parse_system(line,permissions_context)
        elif active_section == "Environment":
            permissions_environment = parse_environment(line,permissions_context)

    return raw_sec, permissions_context

def parse_context(data,permissions_context):
    if "=" in data:
        key = data.split("=")[0]
        flags = data.split("=")[1].rstrip(";").split(";")
        if key in ["shared","sockets","devices","features","filesystems","persistent"]:
            for flag in flags:
                if flag.startswith("!"):
                    flag=flag[1:]
                    permissions_context[key][flag] = False
                else:
                    permissions_context[key][flag] = True
    return permissions_context

def parse_session(data,permissions_context):
    if "=" in data:
        key = data.split("=")[1]
        flag = data.split("=")[0]
        permissions_context["Session Bus Policy"][flag] = key
    return permissions_context
    
def parse_environment(data,permissions_context):
    if "=" in data:
        key = data.split("=")[1]
        flag = data.split("=")[0]
        permissions_context["Environment"][flag] = key
    return permissions_context
    
def parse_system(data,permissions_context):
    if "=" in data:
        key = data.split("=")[1]
        flag = data.split("=")[0]
        permissions_context["System Bus Policy"][flag] = key
    return permissions_context

def get_clean_permissions(): 
    permissions = {
        "sockets": {
            "x11": False,
            "wayland": False,
            "fallback-x11": False,
            "pulseaudio": False,
            "session-bus": False,
            "system-bus": False,
            "ssh-auth": False,
            "pcsc": False,
            "cups": False,
            "gpg-agent": False
        },
        "shared": {
            "network": False,
            "ipc": False
        },
        "devices": {
            "dri": False,
            "kvm": False,
            "shm": False,
            "all": False
        },
        "features": {
            "devel": False,
            "multiarch": False,
            "bluetooth": False,
            "canbus": False,
            "per-app-dev-shm": False
        },
        "filesystems": {
            "host": False,
            "host-os": False,
            "host-etc": False,
            "home": False,
        },
        "persistent": {
        },
        "Session Bus Policy": {
        },
        "System Bus Policy": {
        },
        "Environment": {
        }
    }
    return permissions

def get_clean_override(): 
    override_permissions = {
        "sockets": {
        },
        "shared": {
        },
        "devices": {
        },
        "features": {
        },
        "filesystems": {
        },
        "persistent": {
        },
        "Session Bus Policy": {
        },
        "System Bus Policy": {
        },
        "Environment": {
        }
    }
    return override_permissions

def get_permissions(app_id):    
    permissions = get_clean_permissions()
    override_permissions = get_clean_override()
    
    #==== Hole Override-Daten ====
    override_info = get_overridedata(app_id)
    
    #==== Hole Original-Metadaten ====
    raw_info = get_data(app_id)
    data, permissions_meta = parse_data(raw_info,permissions)
    data_overide, permissions_override = parse_data(override_info,override_permissions)
    
    return permissions_meta, permissions_override
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("⚠️  Nutzung: python p5.py <App-ID>")
    else:
        get_permissions(sys.argv[1])
