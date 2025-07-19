#!/usr/bin/python3

import sys
import os
import themecolor
import subprocess
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Ermittlung der Benutzersprache
def get_user_language():
    return os.environ.get('LANG', 'en_US')

def show_about_dialog(app_id, app_name):
    # Extrahiere die Version aus der Versionsermittlungsfunktion
    version = get_version_info(app_id)
    language = get_user_language()

    # Setze den Text je nach Sprache
    if language.startswith("de"):
        title = f"Über {app_name}"
        text = (f"{app_name}<br><br>"
                f"Autor: F. Maczollek aka VerEnderT <br>"
                f"Webseite: <a href='https://github.com/VerEnderT/{app_id}'>https://github.com/VerEnderT/{app_id}</a><br>"
                f"Version: {version}<br><br>"
                f"Copyright © 2024 - 2025 VerEnderT<br>"
                f"Dies ist freie Software; Sie können es unter den Bedingungen der GNU General Public License Version 3 oder einer späteren Version weitergeben und/oder modifizieren.<br>"
                f"Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich ist, aber OHNE JEDE GARANTIE; sogar ohne die implizite Garantie der MARKTGÄNGIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.<br><br>"
                f"Sie sollten eine Kopie der GNU General Public License zusammen mit diesem Programm erhalten haben. Wenn nicht, siehe <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.")
    else:
        title = "About {app_name}"
        text = (f"{app_name}<br><br>"
                f"Author: F. Maczollek aka VerEnderT<br>"
                f"Website: <a href='https://github.com/VerEnderT/{app_id}'>https://github.com/VerEnderT/{app_id}</a><br>"
                f"Version: {version}<br><br>"
                f"Copyright © 2024 - 2025 VerEnderT<br>"
                f"This is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License Version 3 or any later version.<br>"
                f"This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.<br><br>"
                f"You should have received a copy of the GNU General Public License along with this program. If not, see <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.")
    
    # Über Fenster anzeigen
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setTextFormat(Qt.RichText)  # Setze den Textformatierungsmodus auf RichText (HTML)
    msg_box.setText(text)
    msg_box.setWindowIcon(QIcon("about.png"))
    bcolor,color  = themecolor.theme_color()
    if not bcolor and color:
        print("default color")
        bcolor = "#0d0d0d"
        color = "#eeeeec"
    msg_box.setStyleSheet(f"background: {bcolor};color: {color}")
    msg_box.exec_()

def get_version_info(app_id):
    try:
        result = subprocess.run(['apt', 'show', app_id], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
    except Exception as e:
        print(f"Fehler beim Abrufen der Version: {e}")
    return "Unbekannt"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = show_about_dialog("x-live-wetter","X-live Wetter")
    sys.exit(app.exec_())


