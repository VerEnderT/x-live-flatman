import requests
import subprocess
import sys
import urllib.request

def get_update_info(username, repo):
    """
    Holt die neuesten Versionsnummern der Releases und die Download-URLs eines GitHub-Repositories.
    
    :param username: GitHub-Nutzername
    :param repo: GitHub-Repository-Name
    :return: Ein Dictionary mit der neuesten Versionsnummer und der Download-URL des neuesten Releases
    """

    try:
        url = f"https://api.github.com/repos/{username}/{repo}/releases/latest"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise Exception(f"Fehler beim Abrufen der Daten: {response.status_code}")
            print(f"Repo nicht erreichhbar: {repo}")
        data = response.json()
        release_info = {
            "version": str(data["tag_name"]).replace("v", "").strip(),
            "download_url": data["assets"][0]["browser_download_url"] if data["assets"] else "Keine Assets vorhanden"
        }
        
        return release_info
    
    except Exception as e:
        fehler = str(e).split(":")[-1]
        print(f"Fehler: {fehler}")
        
        release_info = {
            "version": "x",
            "download_url": "x"
        }
        
        return "x"


def get_version(package_name):
    try:
        result = subprocess.run(['dpkg', '-s', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            return "x"
        
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
        
        return "x"
    
    except Exception as e:
        fehler = str(e).split(":")[-1]
        print(f"Fehler: {fehler}")
        return "x"

def parse_version(v):
    return tuple(map(int, (v.replace(" ", "").split("."))))

def compare_versions(installed_version, latest_version):
    if installed_version == "x":
        return "x"
    
    installed = parse_version(installed_version)
    latest = parse_version(latest_version)
    
    if installed < latest:
        return "u" # update available
    else:
        return "a" # up to date

def update_info(username,repo):
    installed_version = get_version(repo).replace(" ", "")
    #print(f'installedVersion: >{installed_version}<')
    if installed_version == "x":
        return {'version':"x",'installed':"x","update":"x","url":"x"}
    else:
        repo_info = get_update_info(username,repo)
        latest_version = str(repo_info["version"]).replace(" ", "")
        need_update = compare_versions(installed_version, latest_version)
        url = str(repo_info["download_url"]).replace(" ", "")
        #print(f'version:{latest_version},  installed: {installed_version}, update: {need_update}, url: {url}')
        return {'version':latest_version,'installed':installed_version,"update":need_update,"url":url}