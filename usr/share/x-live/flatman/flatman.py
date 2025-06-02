#!/usr/bin/python3

import os
import json
import requests
import subprocess
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, QTextEdit, QScrollArea, QMessageBox, QComboBox, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QProcess, QSize
import tempfile
from PIL import Image



class FlatpakApp(QWidget):
    def __init__(self):
        super().__init__()
        self.reload = False

        # Erstelle eine Kopie der aktuellen Umgebung
        self.env = dict(subprocess.os.environ)
        # Setze LC_ALL auf C
        self.env["LC_ALL"] = "C"

        self.config_dir = os.path.expanduser("~/.config/x-live/flatman/")
        self.data_file = self.config_dir + "program_data.json"
        self.fav_file = self.config_dir + "favorites.json"
        self.trans_file = self.config_dir + "trans"
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.program_data = {}  # Speichert die Kategorie, URL und Details der Programme
        
        self.categories_ordered = ["Favoriten","Spiele","Büro","Grafik","AudioVideo","Zubehör","Internet","Bildung","Wissenschaft","Entwicklung","System","Andere","Installiert"]  # Geordnete Liste der Kategorien
        self.initUI()

    def initUI(self):
        self.setWindowTitle("X-Live FlatMan")
        self.setGeometry(200, 20, 840, 600)
        self.setWindowIcon(QIcon("/usr/share/pixmaps/x-live-flatman.png"))
        lwidth = 200
        self.lwidth = lwidth
        desheight = 200
        catheight = 100
        sshotheight = 320
        statuswidth= 620
        statusheight= 15
        
        self.last_item = None
        self.process = None
        layout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.rightLayout.addLayout(self.buttonLayout)

        self.categoryLabel = QLabel("Kategorien:")
        self.categoryLabel.setFixedWidth(lwidth)

        self.leftLayout.addWidget(self.categoryLabel)

        self.categoryList = QComboBox()
        self.categoryList.setFixedWidth(lwidth)
        self.categoryList.setFocusPolicy(Qt.NoFocus)
        self.categoryList.currentIndexChanged.connect(self.loadPrograms)
        self.leftLayout.addWidget(self.categoryList)

        self.programLabel = QLabel("Programme:")
        self.programLabel.setFixedWidth(lwidth)
        self.leftLayout.addWidget(self.programLabel)

        self.programList = QListWidget()
        self.programList.currentItemChanged.connect(self.onProgramClicked)
        self.programList.setFixedWidth(lwidth)
        self.programList.setFocusPolicy(Qt.NoFocus)
        self.leftLayout.addWidget(self.programList)
        self.programList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.programList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        self.loadButton = QPushButton("Daten aktualisieren")
        self.loadButton.setFixedWidth(lwidth-30)
        self.loadButton.clicked.connect(self.loadCategories)

        self.aboutButton = QPushButton("")
        self.aboutButton.setIcon(QIcon("/usr/share/x-live/flatman/about.png"))
        self.aboutButton.setFixedWidth(40)
        self.aboutButton.clicked.connect(self.show_about_dialog)

        self.update_about_layout = QHBoxLayout()
        self.update_about_layout.addWidget(self.aboutButton)
        self.update_about_layout.addWidget(self.loadButton)
        self.leftLayout.addLayout(self.update_about_layout)

        self.rightPanel = QWidget()
        self.rightLayout.addWidget(self.rightPanel)

        self.nameLabel = QLabel("Name:")
        self.buttonLayout.addWidget(self.nameLabel)
        self.buttonLayout.addStretch()
        self.nameLabel.setStyleSheet("font-size: 24px;")
        
        self.statusLabel = QLabel("")
        self.rightLayout.addWidget(self.statusLabel)
        self.statusLabel.setFixedSize(statuswidth,statusheight)

        # Suchleiste
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Apps filtern...")
        self.search_input.textChanged.connect(self.filter_list)
        self.buttonLayout.addWidget(self.search_input)
        
        
        self.installButton = QPushButton("Installieren")
        self.buttonLayout.addWidget(self.installButton)
        self.installButton.clicked.connect(self.install_start)
        self.installButton.setStyleSheet(""" QPushButton {background: green;color: white;} QPushButton:disabled {background: gray;color: light_gray;}""")
        
        self.startButton = QPushButton("Starten")
        self.buttonLayout.addWidget(self.startButton)
        self.startButton.hide()
        self.startButton.clicked.connect(self.app_start)
        self.startButton.setStyleSheet(""" QPushButton {background: yellow;color: black;} QPushButton:disabled {background: gray;color: light_gray;}""")
        
        self.uninstallButton = QPushButton("Deinstallieren")
        self.buttonLayout.addWidget(self.uninstallButton)
        self.uninstallButton.hide()
        self.uninstallButton.clicked.connect(self.uninstall_start)
        self.uninstallButton.setStyleSheet(""" QPushButton {background: red;color: black;} QPushButton:disabled {background: gray;color: light_gray;}""")

        self.favButton = QPushButton(" ❤ ")
        self.buttonLayout.addWidget(self.favButton)
        self.favButton.setFixedSize(24,24)
        self.favButton.clicked.connect(self.fav_btn_clicked)
        self.favButton.setStyleSheet(""" QPushButton {background: grey;color: white;font-size: 26px;} QPushButton:disabled {background: gray;color: light_gray;}""")
        self.favButton.setToolTip("zu Favoriten hinzufügen")

        self.screenshotArea = QScrollArea()
        self.screenshotContainer = QWidget()
        self.screenshotArea.setFixedHeight(sshotheight)
        self.screenshotLayout = QHBoxLayout()
        self.screenshotContainer.setLayout(self.screenshotLayout)
        self.screenshotArea.setWidget(self.screenshotContainer)
        self.screenshotArea.setWidgetResizable(True)
        self.rightLayout.addWidget(self.screenshotArea)
        self.screenshotlabel = QLabel()
        self.screenshotLayout.addStretch(0)
        self.screenshotLayout.addWidget(self.screenshotlabel)
        self.screenshotLayout.addStretch(0)

        self.descriptionLabel = QLabel("Beschreibung:")
        self.rightLayout.addWidget(self.descriptionLabel)

        self.descriptionText = QTextEdit()
        self.descriptionText.setReadOnly(True)
        self.descriptionText.setFixedHeight(desheight)
        self.rightLayout.addWidget(self.descriptionText)



        layout.addLayout(self.leftLayout)
        layout.addLayout(self.rightLayout)

        self.setLayout(layout)
        self.background_color()
        #self.show()
        self.loadSavedFavorites()
        self.loadSavedData()

    def loadSavedData(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.program_data = json.load(f)
            #print("lädt daten")
            #print(f"data: {self.categories_ordered}")
                self.displayCategories()

            except Exception as e:
                self.loadCategories()
        else:
            self.loadCategories()

    def loadSavedFavorites(self):
        if os.path.exists(self.fav_file):
            with open(self.fav_file, "r") as f:
                self.favorites = json.load(f)
        else:
            self.favorites=["VLC","0 A.D.","ONLYOFFICE Desktop Editors","Hedgewars","Brave"]

    def loadCategories(self):
        self.hide()
        os.system("appstreamcli refresh-cache")
        os.system("python3 /usr/share/x-live/flatman/update.py") 
        self.show()
        self.loadSavedData()

    def displayCategories(self):
        self.show()
        self.categoryList.clear()
        for category in self.categories_ordered:
            self.categoryList.addItem(category)

        self.categoryList.setCurrentIndex(0)
        self.loadPrograms()


    def loadPrograms(self):
        category = self.categoryList.currentText()
        self.search_input.clear()
        self.programList.clear()

        # Programme alphabetisch sortieren
        if category == "Installiert":
            sorted_programs = self.loadInstalled()
        elif category == "Favoriten":
            sorted_programs = sorted(self.favorites)
        else:
            sorted_programs = sorted([
                app_name for app_name, data in self.program_data.items()
                if data["category"] == category
            ])

        for app_name in sorted_programs:
            beschreibung = self.program_data.get(app_name, {}).get("short-desc", "")
            tooltip = beschreibung
            if beschreibung and len(beschreibung) > 50:
                beschreibung = beschreibung[:50].rstrip() + " …"


            # HTML-Text definieren
            html = f"""
            <div>
                <span style="font-size:14pt; font-weight:bold;">{app_name}</span><br>
                <span style="font-size:10pt; color:gray;">{beschreibung}</span>
            </div>
            """

            # Widget mit QLabel (HTML)
            widget = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(1, 1, 1, 1)


            label = QLabel()
            label.setText(html)
            label.setTextFormat(Qt.RichText)
            label.setWordWrap(True)
            label.setToolTip(tooltip)

            layout.addWidget(label)
            widget.setLayout(layout)

            item = QListWidgetItem()
            self.programList.addItem(item)
            self.programList.setItemWidget(item, widget)
            item.setSizeHint(QSize(int(self.lwidth*0.9),int(widget.sizeHint().height()*1.2)))

            item.setData(Qt.UserRole, app_name)  # Speichert Programmnamen "unsichtbar" im Item


        if self.programList.count() > 0:
            self.programList.setCurrentRow(0)


    def loadInstalled(self):
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app", "--columns=name"],
                capture_output=True,
                env = self.env,
                text=True,  # Dekodiert die Ausgabe als String
                check=True  # Wirft eine CalledProcessError, wenn der Befehl fehlschlägt
            )
            output = result.stdout.split("\n")
            #print(f"[Debug] {output}")

            installed_apps= []
            for line in output:
                if line.strip() != "":
                    #print(line)
                    installed_apps.append(line.strip())
            return sorted(installed_apps, key=str.lower)

        except Exception as e:
            return []
            
    def onProgramClicked(self, item):
        if not self.reload:
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet("")
        self.reload = False
        
        if item:
            try:
                app_name = item.data(Qt.UserRole)
                app_id = self.program_data.get(app_name, {}).get("id")
                self.last_item = item
                self.highlightSelectedItem(item)  # 👈 HIER wird das Styling aktualisiert

                if app_id:
                    self.displayProgramDetails(app_id, app_name)
            except Exception as e:
                print("Fehler beim Klicken:", e)

    def highlightSelectedItem(self, current_item):
        for index in range(self.programList.count()):
            item = self.programList.item(index)
            widget = self.programList.itemWidget(item)
            if widget:
                if item == current_item:
                    widget.setStyleSheet("border: 1px solid #0078d7; border-radius: 5px; padding: 2px;")
                else:
                    widget.setStyleSheet("border: none; padding: 2px;")

    def get_flatpak_info(self, app_name):
        description = self.program_data.get(app_name, {}).get("description")
        thumbnail = self.program_data.get(app_name, {}).get("thumbnail")
        info_version = self.program_data.get(app_name, {}).get("version")
        info_installed = self.program_data.get(app_name, {}).get("size")
        return thumbnail, description, info_version, info_installed

    def convert_image_format(self, input_file, output_file):
        with Image.open(input_file) as img:
            img.convert("RGB").save(output_file, "JPEG")  # Konvertiere in JPEG

    def displayProgramDetails(self, app_id, app_name):
        self.app_id = app_id
        if app_name in self.favorites:
            self.favButton.setStyleSheet(""" QPushButton {background: green;color: white;font-size: 26px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("aus Favoriten entfernen")
        else:         
            self.favButton.setStyleSheet(""" QPushButton {background: gray;color: white;font-size: 26px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("zu Favoriten hinzufügen")

        thumbnail, description, info_version, info_installed = self.get_flatpak_info(app_name)

        self.descriptionLabel.setText(f" App-ID: {app_id}\n Version: {info_version}\n Speicherbedarf: {info_installed}\n\nBeschreibung:")

        try:
            # Bild von der URL herunterladen
            response = requests.get(thumbnail)
            
            if response.status_code == 200:
                # Temporäre Datei für das Bild erstellen
                with tempfile.NamedTemporaryFile(delete=False, suffix='.webp') as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name

                self.convert_image_format(temp_file_path, 'downloaded_image.jpg')  # Konvertiere in JPG
                pixmap = QPixmap('downloaded_image.jpg')  # Lade das konvertierte Bild

                if pixmap.isNull():
                    self.screenshotlabel.setText("Fehler beim Laden des WebP-Bildes.")
                else:
                    self.screenshotlabel.setPixmap(pixmap.scaled(600, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            else:
                self.screenshotlabel.setText("Fehler beim Herunterladen des Bildes.")

        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen des Thumbnails: {e}")
            pixmap = QPixmap("/usr/share/x-live/flatman/no_screenshot.png")
            self.screenshotlabel.setPixmap(pixmap.scaled(600, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        try:
            cmd = "flatpak list --app".split(" ")
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.splitlines()
            self.installed = []
            for line in lines:
                self.installed.append(line.split("\t")[1])
            if app_id in self.installed:
                self.uninstallButton.show()
                self.startButton.show()
                self.installButton.hide()
            else:
                self.uninstallButton.hide()
                self.startButton.hide()
                self.installButton.show()

            self.uninstallButton.setEnabled(True)
            self.installButton.setEnabled(True)
            #description1 = self.translate_text(description)
            self.descriptionText.setText(description)
            self.nameLabel.setText(f"{app_name}")
                   
        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen der Programmdetails-hier: {e}")
            self.descriptionText.setText("")


    def translate_text_old(self, text, source="en", target="de"):
        result = subprocess.run(
            [self.trans_file, f"-b", f":{target}", text],
            stdout=subprocess.PIPE,
            text=True
        )
        #print("[debug]",str(result.stdout.strip()))
        return str(result.stdout.strip())

    def translate_text(self, text, source="en", target="de"):
        if os.path.exists(trans_file):
            result = subprocess.run(
                [self.trans_file, f"-b", f":{target}", str(text)],
                stdout=subprocess.PIPE,
                text=True
            )
            #print("[debug]",str(result.stdout.strip()))
            return str(result.stdout.strip())
        else:
            cmd=f"cd {self.config_dir} && wget git.io/trans && chmod +x ./trans"
            os.system(cmd)
    
            result = subprocess.run(
                [self.trans_file, f"-b", f":{target}", str(text)],
                stdout=subprocess.PIPE,
                text=True
            )
            #print("[debug]",str(result.stdout.strip()))
            return str(result.stdout.strip())


    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

    def filter_list(self):
        """ Die Liste der Programme basierend auf der Benutzereingabe filtern """
        filter_text = self.search_input.text().lower()
        for row in range(self.programList.count()):
            item = self.programList.item(row)
            widget = self.programList.itemWidget(item)
            if widget:
                # Angenommen, das Widget ist ein QLabel
                app_name = item.data(Qt.UserRole)
                beschreibung = self.program_data.get(app_name, {}).get("short-desc", "")
                text = app_name.lower() + " " + beschreibung.lower()
                item.setHidden(filter_text not in text)

    def fav_btn_clicked(self):
        app_name = self.last_item.data(Qt.UserRole)

        if app_name in self.favorites:
            self.favorites.remove(app_name) 
            self.favButton.setStyleSheet(""" QPushButton {background: gray;color: white;font-size: 26px;}QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("zu Favoriten hinzufügen")

        else:
            self.favorites.append(app_name)
            self.favButton.setStyleSheet(""" QPushButton {background: green;color: white;font-size: 26px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("aus Favoriten entfernen")
        self.fav_save()
            

    def fav_save(self):
        output_dir = os.path.dirname(self.config_dir)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            #print(f"[DEBUG] Verzeichnis erstellt: {output_dir}")

        with open(self.fav_file, "w") as f:
            json.dump(self.favorites, f)
        #print(f"[DEBUG] Daten gespeichert in: {data_file}")



    # Ermittlung der Benutzersprache
    def get_user_language(self):
        return os.environ.get('LANG', 'en_US')

    def show_about_dialog(self):
        # Extrahiere die Version aus der Versionsermittlungsfunktion
        version = self.get_version_info()
        language = self.get_user_language()

        # Setze den Text je nach Sprache
        if language.startswith("de"):
            title = "Über X-Live Flatman"
            text = (f"X-Live Flatman<br><br>"
                    f"Autor: F. Maczollek aka VerEnderT <br>"
                    f"Webseite: <a href='https://github.com/VerEnderT/x-live-flatman'>https://github.com/VerEnderT/x-live-flatman</a><br>"
                    f"Version: {version}<br><br>"
                    f"Copyright © 2024 - 2025 VerEnderT<br>"
                    f"Dies ist freie Software; Sie können es unter den Bedingungen der GNU General Public License Version 3 oder einer späteren Version weitergeben und/oder modifizieren.<br>"
                    f"Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich ist, aber OHNE JEDE GARANTIE; sogar ohne die implizite Garantie der MARKTGÄNGIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.<br><br>"
                    f"Sie sollten eine Kopie der GNU General Public License zusammen mit diesem Programm erhalten haben. Wenn nicht, siehe <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.")
        else:
            title = "About X-Live Flatman"
            text = (f"X-Live Flatman<br><br>"
                    f"Author: F. Maczollek aka VerEnderT<br>"
                    f"Website: <a href='https://github.com/VerEnderT/x-live-flatman'>https://github.com/VerEnderT/x-live-flatman</a><br>"
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
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()

    def get_version_info(self):
        try:
            result = subprocess.run(['apt', 'show', 'x-live-flatman'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        except Exception as e:
            print(f"Fehler beim Abrufen der Version: {e}")
        return "Unbekannt"





    # Farbprofil abrufen und anwenden

    def get_current_theme(self):
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

    def extract_color_from_css(self,css_file_path, color_name):
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
                     
    def background_color(self):
        theme_name = self.get_current_theme()
        if theme_name:
            #print(f"Current theme: {theme_name}")

            # Pfad zur GTK-CSS-Datei des aktuellen Themes
            css_file_path = f'/usr/share/themes/{theme_name}/gtk-3.0/gtk.css'
            if os.path.exists(css_file_path):
                bcolor = self.extract_color_from_css(css_file_path, ' background-color')
                color = self.extract_color_from_css(css_file_path, ' color')
                self.setStyleSheet(f"background: {bcolor};color: {color}")
            else:
                pass                
                #print(f"CSS file not found: {css_file_path}")
        else:
            #print("Unable to determine the current theme.")
            pass
    
    def app_start(self):
        cmd = (f"flatpak run {self.app_id}").split(" ")
        subprocess.Popen(cmd)
                
    def install_start(self):
        self.programList.setEnabled(False)
        self.categoryList.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.installButton.setEnabled(False)
        self.install_package(self.app_id)

            
    def uninstall_start(self):
        self.programList.setEnabled(False)
        self.categoryList.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.installButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.uninstall_package(self.app_id)

    def un_install_finished(self):
        self.programList.setEnabled(True)
        self.categoryList.setEnabled(True)
        self.loadButton.setEnabled(True)  
        self.startButton.setEnabled(True)  
        self.process = None  
        self.reload = True
        self.onProgramClicked(self.last_item)
        


    def install_package(self,app_id):
        if not self.process:
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet("")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished)
            
            # Prepare the command
            command = f'flatpak install -y {app_id}'
            self.process.start('sh', ['-c', command])
            
    def uninstall_package(self,app_id):
        if not self.process:
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet("")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished_remove)
            
            # Prepare the command
            command = f'flatpak uninstall -y {app_id}'
            self.process.start('sh', ['-c', command])


    def read_output(self):
        if self.process:
            output = self.process.readAll().data().decode()
            output = str(output).replace('\r\n', '\n').replace('\r', '\n')
            self.statusLabel.setText(output)

    def process_finished(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.statusLabel.setText(" "+self.translate_text("Installation completed successfully."))
            self.statusLabel.setStyleSheet("background-color: green;color: white;")
            #QMessageBox.information(self, "Success", "Package installed successfully!")
        else:
            self.statusLabel.setText(" "+self.translate_text("Installation failed."))
            self.statusLabel.setStyleSheet("background-color: red;color: white;")
            #QMessageBox.critical(self, "Error", "Failed to install package.")
            
        self.un_install_finished()
        
            
    def process_finished_remove(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.statusLabel.setText(" "+self.translate_text("Uninstallation completed successfully."))
            self.statusLabel.setStyleSheet("background-color: green;color: white;")
            #QMessageBox.information(self, "Success", "Package uninstalled successfully!")
        else:
            self.statusLabel.setText(" "+self.translate_text("Uninstallation failed."))
            self.statusLabel.setStyleSheet("background-color: red;color: white;")
            #QMessageBox.critical(self, "Error", "Failed to uninstall package.")
        
        self.un_install_finished()
        
if __name__ == '__main__':
    app = QApplication([])
    ex = FlatpakApp()
    app.exec_()
