#!/usr/bin/python3

import subprocess, os, re

def get_current_theme():
    try:
        # Versuche, das Theme mit xfconf-query abzurufen
        result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'], capture_output=True, text=True)
        theme_name = result.stdout.strip()
        if theme_name:
            return theme_name
    except FileNotFoundError:
        pass
        #print("xfconf-query nicht gefunden. Versuche gsettings.")
    except Exception as e:
        #print(f"Error getting theme with xfconf-query: {e}")
        pass

    try:
        # Fallback auf gsettings, falls xfconf-query nicht vorhanden ist
        result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
        theme_name = result.stdout.strip().strip("'")
        if theme_name:
            return theme_name
    except Exception as e:
        #print(f"Error getting theme with gsettings: {e}")
        pass

    return None

def extract_color_from_css(css_file_path, color_name):
    try:
        with open(css_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            #print(content)
            # Muster zum Finden der Farbe
            pattern = r'{}[\s:]+([#\w]+)'.format(re.escape(color_name))
            match = re.search(pattern, content)
            if match:
                return match.group(1)
            return None
    except IOError as e:
        #print(f"Error reading file: {e}")
        return None
                 
def theme_color():
    theme_name = get_current_theme()
    #print(f"Current theme: {theme_name}")
    if theme_name:
        #print(f"Current theme: {theme_name}")

        # Pfad zur GTK-CSS-Datei des aktuellen Themes
        css_file_path = f'/usr/share/themes/{theme_name}/gtk-3.0/gtk.css'
        if os.path.exists(css_file_path):
            bcolor = extract_color_from_css(css_file_path, ' background-color')
            color = extract_color_from_css(css_file_path, ' color')
            return bcolor, color
        else:
            return None, None                 
            #print(f"CSS file not found: {css_file_path}")
    else:
        #print("Unable to determine the current theme.")
        return None, None 
        

if __name__ == "__main__":
    bcolor,color = theme_color()
    print(bcolor,color)
