#!/usr/bin/python3

import os
import json
import requests
import subprocess
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QTextEdit, QScrollArea, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QProcess

class FlatpakApp(QWidget):
    def __init__(self):
        super().__init__()
        self.data_file = "/tmp/x-live/flatpak/program_data.json"
        self.program_data = {}  # Speichert die Kategorie, URL und Details der Programme
        self.categories_ordered = ["trending","Game","Office","Graphics","AudioVideo","Utility","Network","Education","Science","Development","System"]  # Geordnete Liste der Kategorien
        self.initUI()

    def initUI(self):
        self.setWindowTitle("X-Live FlatMan")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("/usr/share/pixmaps/x-live-flatman.png"))
        lwidth = 200
        desheight = 150
        catheight = 100
        sshotheight = 350
        statuswidth= 500
        statusheight= 15
        self.process = None
        layout = QHBoxLayout()

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.rightLayout.addLayout(self.buttonLayout)

        self.categoryLabel = QLabel("Kategorien:")
        self.categoryLabel.setFixedWidth(lwidth)
        self.leftLayout.addWidget(self.categoryLabel)

        self.categoryList = QListWidget()
        self.categoryList.setFixedSize(lwidth, catheight)
        self.leftLayout.addWidget(self.categoryList)

        self.programLabel = QLabel("Programme:")
        self.programLabel.setFixedWidth(lwidth)
        self.leftLayout.addWidget(self.programLabel)

        self.programList = QListWidget()
        self.programList.currentItemChanged.connect(self.onProgramClicked)
        self.programList.setFixedWidth(lwidth)
        self.leftLayout.addWidget(self.programList)

        self.loadButton = QPushButton("Daten aktualisieren")
        self.loadButton.setFixedWidth(lwidth)
        self.loadButton.clicked.connect(self.loadCategories)
        self.leftLayout.addWidget(self.loadButton)

        self.rightPanel = QWidget()
        self.rightLayout.addWidget(self.rightPanel)

        self.nameLabel = QLabel("Name:")
        self.buttonLayout.addWidget(self.nameLabel)
        self.buttonLayout.addStretch()
        self.nameLabel.setStyleSheet("font-size: 24px;")
        
        self.statusLabel = QLabel("")
        self.rightLayout.addWidget(self.statusLabel)
        self.statusLabel.setFixedSize(statuswidth,statusheight)
        
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


        self.descriptionLabel = QLabel("Beschreibung:")
        self.rightLayout.addWidget(self.descriptionLabel)

        self.descriptionText = QTextEdit()
        self.descriptionText.setReadOnly(True)
        self.descriptionText.setFixedHeight(desheight)
        self.rightLayout.addWidget(self.descriptionText)

        self.screenshotLabel = QLabel("Screenshots:")
        self.rightLayout.addWidget(self.screenshotLabel)

        self.screenshotArea = QScrollArea()
        self.screenshotContainer = QWidget()
        self.screenshotArea.setFixedHeight(sshotheight)
        self.screenshotLayout = QHBoxLayout()
        self.screenshotContainer.setLayout(self.screenshotLayout)
        self.screenshotArea.setWidget(self.screenshotContainer)
        self.screenshotArea.setWidgetResizable(True)
        self.rightLayout.addWidget(self.screenshotArea)
        self.screenshotlabel = QLabel()
        self.screenshotLayout.addWidget(self.screenshotlabel)


        layout.addLayout(self.leftLayout)
        layout.addLayout(self.rightLayout)

        self.setLayout(layout)
        self.background_color()
        #self.show()

        self.loadSavedData()

    def loadSavedData(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.program_data = json.load(f)
            print("lädt daten")
            print(f"data: {self.categories_ordered}")
            self.displayCategories()
        else:
            self.loadCategories()

    def loadCategories(self):
        self.hide()
        os.system("appstreamcli refresh-cache")
        cmd = ["python3", "/usr/share/x-live/flatman/warten.py"]  # Beispielprogramm; passe dies an das Programm an, das du starten möchtest
    
        # Starten des Prozesses ohne Einfluss auf das Hauptprogramm
        process = subprocess.Popen(
            cmd,
            start_new_session=True,  # Startet den Prozess in einer neuen Sitzung
            stdout=subprocess.DEVNULL,  # Verhindert Ausgabe des gestarteten Prozesses in der Konsole
            stderr=subprocess.DEVNULL,  # Verhindert Fehlerausgabe in der Konsole
        )

        base_urls = [
            "https://flathub.org/de/apps/collection/trending/",
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

        self.categories_ordered = []  # Zurücksetzen der geordneten Liste
        self.program_data = {}

        for base_url in base_urls:
            category_name = base_url.split('/')[-2]
            self.categories_ordered.append(category_name)  # Kategorien in der gewünschten Reihenfolge speichern
            page_number = 1
            while True:
                url = f"{base_url}{page_number}"
                print(f"[DEBUG] Sende Anfrage an: {url}")
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
                            self.program_data[app_name] = {
                                "category": category_name,
                                "url": app_url
                            }

                    page_number += 1

                except Exception as e:
                    print(f"[ERROR] Fehler beim Verarbeiten der Seite: {e}")
                    break
        
        command = ['pkill', '-f', 'python3 /usr/share/x-live/flatman/warten.py']        
        result = subprocess.run(command, text=True)
        
        self.show()
        self.saveData()
        self.displayCategories()

    def saveData(self):
        output_dir = os.path.dirname(self.data_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"[DEBUG] Verzeichnis erstellt: {output_dir}")

        with open(self.data_file, "w") as f:
            json.dump(self.program_data, f)
        print(f"[DEBUG] Daten gespeichert in: {self.data_file}")

    def displayCategories(self):
        self.show()
        self.categoryList.clear()
        for category in self.categories_ordered:
            self.categoryList.addItem(category)
        self.categoryList.currentItemChanged.connect(self.loadPrograms)        
        self.categoryList.setCurrentRow(0)

    def loadPrograms(self, item):
        category = item.text()
        self.programList.clear()
        # Programme alphabetisch sortieren, bevor sie hinzugefügt werden
        sorted_programs = sorted([app_name for app_name, data in self.program_data.items() if data["category"] == category])
        for app_name in sorted_programs:
            self.programList.addItem(app_name)        
        self.programList.setCurrentRow(0)

    def onProgramClicked(self, item):
        app_name = item.text()
        print(item.text)
        app_url = self.program_data.get(app_name, {}).get("url")
        self.last_item = item
        if app_url:
            self.displayProgramDetails(app_url, app_name)

    def get_data_from_appstream(self, app_id):
        try:
            cmd = f"appstreamcli dump {app_id}".split(" ")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"[ERROR] Fehler beim Abrufen von AppStream-Daten: {result.stderr}")
                return []

            lines = result.stdout.strip().lstrip().replace("\t", "").splitlines()
            screenshots = []
            description = ""
            thumbnails = []
            for line in lines:
                testline = line[line.find("<"):]
                if testline.startswith('<image type="source"'):
                    url = testline[testline.find(">")+1:]
                    url = url[:url.find("<")]
                    screenshots.append(url)
                if testline.startswith('<image type="thumbnail"'):
                    url = testline[testline.find(">")+1:]
                    url = url[:url.find("<")]
                    thumbnails.append(url)
                if testline.startswith('<p>'):
                    description = (description+testline[testline.find("<p>"):]).replace("</p>", "").replace("<p>", "")
            return screenshots, thumbnails, description

        except Exception as e:
            print(f"[ERROR] Fehler beim Verarbeiten von AppStream-Daten: {e}")
            return []

    def displayProgramDetails(self, app_url, app_name):
        print(f"[DEBUG] Lade Details für Programm: {app_url}")
        self.app_id = app_url.split('/')[-1]
        try:
            app_id = app_url.split('/')[-1]
            screenshots, thumbnails, description = self.get_data_from_appstream(app_id)
            if thumbnails:
                screenshot_url = thumbnails[-1]
            else:
                if screenshots:
                    screenshot_url = screenshots[0]
            if screenshot_url:
                response = requests.get(screenshot_url)
                response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.screenshotlabel.setPixmap(pixmap.scaled(400, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen des Thumbnails: {e}")

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

            self.nameLabel.setText(f"Name: {app_name}")
            self.descriptionText.setText(description)
            #self.clearLayout(self.screenshotLayout)

                   
            #app_id = app_url.split('/')[-1]
            #screenshots, thumbnails, description = self.get_data_from_appstream(app_id)
            #for screenshot_url in screenshots:
            #    response = requests.get(screenshot_url)
            #    response.raise_for_status()
            #    pixmap = QPixmap()
            #    pixmap.loadFromData(response.content)

            #    label = QLabel()
            #    label.setPixmap(pixmap.scaled(400, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                #label.setFixedSize(400, 280)
            #    self.screenshotLayout.addWidget(label)

        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen der Programmdetails: {e}")
            try:
                response = requests.get(app_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                description_div = soup.find('div', class_='prose dark:prose-invert xl:max-w-[75%]')
                if description_div:
                    description = description_div.get_text(strip=True)
                else:
                    description = 'Beschreibung nicht gefunden'
                self.nameLabel.setText(f"Name: {app_name}")
                self.descriptionText.setText(description)

            
            except Exception as e:
                print(f"[ERROR] Fehler beim Abrufen der Programmdetails: {e}")
            

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

    # Farbprofil abrufen und anwenden

    def get_current_theme(self):
        try:
            # Versuche, das Theme mit xfconf-query abzurufen
            result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'], capture_output=True, text=True)
            theme_name = result.stdout.strip()
            if theme_name:
                return theme_name
        except FileNotFoundError:
            print("xfconf-query nicht gefunden. Versuche gsettings.")
        except Exception as e:
            print(f"Error getting theme with xfconf-query: {e}")

        try:
            # Fallback auf gsettings, falls xfconf-query nicht vorhanden ist
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
            theme_name = result.stdout.strip().strip("'")
            if theme_name:
                return theme_name
        except Exception as e:
            print(f"Error getting theme with gsettings: {e}")

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
            print(f"Error reading file: {e}")
            return None
            
            
    def background_color(self):
        theme_name = self.get_current_theme()
        if theme_name:
            print(f"Current theme: {theme_name}")

            # Pfad zur GTK-CSS-Datei des aktuellen Themes
            css_file_path = f'/usr/share/themes/{theme_name}/gtk-3.0/gtk.css'
            if os.path.exists(css_file_path):
                bcolor = self.extract_color_from_css(css_file_path, ' background-color')
                color = self.extract_color_from_css(css_file_path, ' color')
                self.setStyleSheet(f"background: {bcolor};color: {color}")
            else:
                print(f"CSS file not found: {css_file_path}")
        else:
            print("Unable to determine the current theme.")
            
    
    def app_start(self):
        cmd = (f"flatpak run {self.app_id}").split(" ")
        subprocess.Popen(cmd)
                
    def install_start(self):
        self.programList.setEnabled(False)
        self.categoryList.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.installButton.setEnabled(False)
        self.install_package(self.app_id)

            
    def uninstall_start(self):
        self.programList.setEnabled(False)
        self.categoryList.setEnabled(False)
        self.loadButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.installButton.setEnabled(False)
        self.uninstall_package(self.app_id)

    def un_install_finished(self):
        self.programList.setEnabled(True)
        self.categoryList.setEnabled(True)
        self.loadButton.setEnabled(True)
        self.statusLabel.setText("")        
        self.process = None  
        self.onProgramClicked(self.last_item)
        


    def install_package(self,app_id):
        if not self.process:
            self.statusLabel.setText("Starting package update and installation...\n")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished)
            
            # Prepare the command
            command = f'flatpak install -y {app_id}'
            self.process.start('sh', ['-c', command])
            
    def uninstall_package(self,app_id):
        if not self.process:
            self.statusLabel.setText("Starting package uninstallation...\n")
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
            self.statusLabel.setText("\nInstallation completed successfully.")
            QMessageBox.information(self, "Success", "Package installed successfully!")
        else:
            self.statusLabel.setText("\nInstallation failed.")
            QMessageBox.critical(self, "Error", "Failed to install package.")
            
        self.un_install_finished()
        
            
    def process_finished_remove(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.statusLabel.setText("\nUninstallation completed successfully.")
            QMessageBox.information(self, "Success", "Package uninstalled successfully!")
        else:
            self.statusLabel.setText("\nUninstallation failed.")
            QMessageBox.critical(self, "Error", "Failed to uninstall package.")
        
        self.un_install_finished()
        
if __name__ == '__main__':
    app = QApplication([])
    ex = FlatpakApp()
    app.exec_()
