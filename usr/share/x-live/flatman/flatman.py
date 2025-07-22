#!/usr/bin/python3

import os
import json
import requests
import subprocess
import flatperm
import themecolor
import about
import x_app_updates
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, QTextEdit, QScrollArea, QMessageBox, QComboBox, QLineEdit, QAction, QMenu, QMenuBar, QListView
from PyQt5.QtGui import QPixmap, QIcon, QPixmap
from PyQt5.QtCore import Qt, QProcess, QSize
import tempfile
from PIL import Image


# Pfad zum Arbeitsverzeichnis festlegen
#arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/flatman/')
#os.chdir(arbeitsverzeichnis)


class FlatpakApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.reload = False

        # Erstelle eine Kopie der aktuellen Umgebung
        self.env = dict(subprocess.os.environ)
        # Setze LC_ALL auf C
        self.env["LC_ALL"] = "C"

        self.bcolor, self.color = themecolor.theme_color()
        #print(self.bcolor, self.color)

        if self.bcolor == None or self.color == None:
            self.bcolor = "eeeeec"
            self.color = "0d0d0d"
        else:
            self.bcolor = self.bcolor.replace("#","")
            self.color = self.color.replace("#","")


        self.config_dir = os.path.expanduser("~/.config/x-live/flatman/")
        self.icons_dir = os.path.expanduser("~/.config/x-live/flatman/icons/")
        self.thumbnails_dir = os.path.expanduser("~/.config/x-live/flatman/thumbnails/")
        self.data_file = self.config_dir + "program_data.json"
        self.fav_file = self.config_dir + "favorites.json"
        self.trans_file = self.config_dir + "trans"
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.program_data = {}  # Speichert die Kategorie, URL und Details der Programme
        
        self.categories_ordered = ["Favoriten","Spiele","Büro","Grafik","AudioVideo","Zubehör","Internet","Bildung","Wissenschaft","Entwicklung","System","Andere","Alle","Installiert"]  # Geordnete Liste der Kategorien
        self.initUI()

    def initUI(self):
        self.faktor = app.desktop().height()/1000
        self.faktor = 1.0
        self.setWindowTitle("X-Live FlatMan")
        self.setGeometry(200, 20, int(950*(self.faktor+0.3)), int(600*self.faktor))
        self.setMinimumSize(int(750*(self.faktor+0.3)), int(600*self.faktor))
        self.setWindowIcon(QIcon("/usr/share/pixmaps/x-live-flatman.png"))
        lwidth = int(232*self.faktor)
        self.lwidth = lwidth
        desheight = int(200*self.faktor)
        catheight = int(100*self.faktor)
        sshotheight = int(320*self.faktor)
        statuswidth= int(620*self.faktor)
        statusheight= int(25*self.faktor)
        buttonheight= int(35*self.faktor)
        
        self.last_item = None
        self.process = None
        
        
        
        # Menübar erstellen
        menubar = QMenuBar()
        menubar.setStyleSheet(f"font-size: {str(int(14*self.faktor))}px;")
        menubar.setFixedSize(buttonheight,buttonheight)

        # Menü hinzufügen
        menu_menu = menubar.addMenu("")
        menu_menu.setIcon(QIcon("/usr/share/x-live/flatman/icons/menu.png"))

        # Aktionen für das Menü - Berechtigungen
        permissions_action = QAction("Berechtigungen", self)
        permissions_action.setIcon(QIcon("/usr/share/x-live/flatman/icons/perm_icon.png"))
        permissions_action.triggered.connect(self.loadPermissions)
        #permissions_action.setStyleSheet(f"font-size: {str(int(24*self.faktor))}px;")
        

        # Aktionen für das Menü - Daten aktuallisieren
        refresh_action = QAction("APP-Datenbank auffrischen", self)
        refresh_action.setIcon(QIcon("/usr/share/x-live/flatman/icons/update.png"))
        refresh_action.triggered.connect(self.loadCategories)
        

        # Aktionen für das Menü - über 
        about_action = QAction("über", self)
        about_action.setIcon(QIcon("/usr/share/x-live/flatman/icons/about.png"))
        about_action.triggered.connect(lambda: about.show_about_dialog("x-live-flatman","X-Live Flatman"))
        
        # Aktionen für das Menü - Flatman Update 
        update_action = QAction("Flatman Aktuallisieren", self)
        update_action.setIcon(QIcon("/usr/share/x-live/flatman/icons/update.png"))
        update_action.triggered.connect(lambda: about.show_about_dialog("x-live-flatman","X-Live Flatman"))
        
        # Aktionen zu den Menüs hinzufügen
        
        try:
            update_check = x_app_updates.update_info("verendert","x-live-flatman")
            #print(update_check)
        
        except Exception as e:
            print(f"Fehler bei updatecheck: {str(e)}")
            update_check  = {}
            update_check["update"] = "x"


        if update_check["update"] == "u":
            update_action.setText(f"Flatman auf {update_check['version']} aktuallisieren")
        if update_check["update"] == "a":
            update_action.setText(f"Flatman ist aktuell version {update_check['version']}")
        if update_check["update"] == "x":
            update_action.setText(f"Flatman konnte nicht auf update prüfen !!")
        menu_menu.addAction(refresh_action)
        menu_menu.addAction(update_action)
        menu_menu.addAction(about_action)
        
        
        self.layout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()
        self.dataLayout = QVBoxLayout()
        self.permlayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.rightLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(menubar)

        # Suchleiste
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Apps filtern...")
        self.search_input.setStyleSheet(f"font-size: {str(int(14*self.faktor))}px;")
        self.search_input.textChanged.connect(self.filter_list)
        self.search_input.setFixedSize(lwidth,buttonheight)
        self.leftLayout.addWidget(self.search_input)
        

        self.categoryList = QComboBox()
        self.categoryList.setFixedSize(lwidth,buttonheight)
        

        self.categoryList.setStyleSheet("QComboBox {font-size: " + str(int(14*self.faktor)) + "px;} QComboBox QAbstractItemView {selection-background-color: #" + self.color + ";selection-color: #" + self.bcolor + ";} ")



        self.categoryList.setFocusPolicy(Qt.NoFocus)
        self.categoryList.currentIndexChanged.connect(self.loadPrograms)
        self.leftLayout.addWidget(self.categoryList)

        self.programList = QListWidget()
        self.programList.currentItemChanged.connect(self.onProgramClicked)
        self.programList.setFixedWidth(lwidth)
        self.programList.setFocusPolicy(Qt.NoFocus)
        self.leftLayout.addWidget(self.programList)
        self.programList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.programList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.rightPanel = QWidget()
        self.dataLayout.addWidget(self.rightPanel)
        icon_path="/usr/share/x-live/flatman/icons/no_screenshot.png"

        self.icon_label = QLabel()
        
        pixmap = QPixmap(icon_path).scaled(int(64*self.faktor), int(64*self.faktor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(int(64*self.faktor), int(64*self.faktor))

        self.buttonLayout.addWidget(self.icon_label)

        self.nameLabel = QLabel("Name:")
        self.buttonLayout.addWidget(self.nameLabel)
        self.buttonLayout.addStretch()
        self.nameLabel.setStyleSheet(f"font-size: {str(int(24*self.faktor))}px;")
        
        self.statusLabel = QLabel("")
        self.dataLayout.addWidget(self.statusLabel)
        self.statusLabel.setFixedSize(statuswidth,statusheight)
        
        self.installButton = QPushButton("Installieren")
        self.buttonLayout.addWidget(self.installButton)
        self.installButton.setFixedHeight(buttonheight)
        self.installButton.clicked.connect(self.install_start)
        self.installButton.setStyleSheet(""" QPushButton {background: green;color: white;} QPushButton:disabled {background: gray;color: light_gray;}""")

        self.permButton = QPushButton("Berechtigungen")
        self.permButton.setFixedHeight(buttonheight)
        self.buttonLayout.addWidget(self.permButton)
        self.permButton.clicked.connect(self.loadPermissions)
        self.permButton.setIcon(QIcon("/usr/share/x-live/flatman/perm_icon.png"))
        
        self.permButton.setStyleSheet(""" QPushButton {background: grey;color: white;}""")
        
        self.startButton = QPushButton("Starten")
        self.buttonLayout.addWidget(self.startButton)
        self.startButton.setFixedHeight(buttonheight)
        self.startButton.hide()
        self.startButton.clicked.connect(self.app_start)
        self.startButton.setStyleSheet(""" QPushButton {background: yellow;color: black;} QPushButton:disabled {background: gray;color: light_gray;}""")
        
        self.uninstallButton = QPushButton("Deinstallieren")
        self.uninstallButton.setFixedHeight(buttonheight)
        self.buttonLayout.addWidget(self.uninstallButton)
        self.uninstallButton.hide()
        self.uninstallButton.clicked.connect(self.uninstall_start)
        self.uninstallButton.setStyleSheet(""" QPushButton {background: red;color: black;} QPushButton:disabled {background: gray;color: light_gray;}""")

        self.favButton = QPushButton(" ❤ ")
        self.buttonLayout.addWidget(self.favButton)
        self.favButton.setFixedSize(int(24*self.faktor),int(24*self.faktor))
        self.favButton.clicked.connect(self.fav_btn_clicked)
        self.favButton.setStyleSheet(""" QPushButton {background: grey;color: white;font-size: """+str(int(26*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
        self.favButton.setToolTip("zu Favoriten hinzufügen")

        self.screenshotLayout = QHBoxLayout()
        self.screenshotlabel = QLabel()
        self.screenshotLayout.addStretch(0)
        self.screenshotLayout.addWidget(self.screenshotlabel)
        self.screenshotLayout.addStretch(0)
        self.screenshotlabel.setFixedHeight(sshotheight)

        self.dataLayout.addLayout(self.screenshotLayout)
        self.dataLayout.addStretch(1)

        self.descriptionLabel = QLabel("Beschreibung:")
        self.dataLayout.addWidget(self.descriptionLabel)

        self.descriptionText = QLabel()
        self.descriptionText.setWordWrap(True)           # ⚡️ Textumbruch
        self.dataLayout.addWidget(self.descriptionText)
        self.dataLayout.addStretch(2)

        self.layout.addLayout(self.leftLayout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.dataLayout)
        self.scroll.setWidget(self.scrollWidget)

        self.infoLayout.addLayout(self.permlayout)
        self.infoLayout.addWidget(self.scroll)
        self.rightLayout.addLayout(self.infoLayout)

        self.layout.addLayout(self.rightLayout)

        self.central_widget= QWidget(self)
        
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.background_color()
        self.loadSavedFavorites()
        self.loadSavedData()
        
        

    def loadSavedData(self):
        #print(self.data_file)
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.program_data = json.load(f)
                    #print("lädt daten")
                    #print(f"data: {self.categories_ordered}")
                    self.all_apps = sorted([app_name for app_name, data in self.program_data.items()])
                    self.displayCategories()

            except Exception as e:
                print(f"fehler 1 {e}")
                self.loadCategories()
        else:
            print("fehler 2")
            self.loadCategories()

    def loadSavedFavorites(self):
        if os.path.exists(self.fav_file):
            with open(self.fav_file, "r") as f:
                self.favorites = json.load(f)
        else:
            self.favorites=["VLC","0 A.D.","ONLYOFFICE Desktop Editors","Hedgewars","Brave","SuperTuxKart","OBS Studio","Heroic","Steam","RetroDECK"]

    def loadCategories(self):
        self.hide()
        print("fehler 3")
        os.system("appstreamcli refresh-cache")
        os.system("python3 /usr/share/x-live/flatman/update.py") 
        #self.show()
        self.loadSavedData()


    def displayCategories(self):
        self.prepare_programmlist()
        self.show()
        self.categoryList.clear()
        for category in self.categories_ordered:
            self.categoryList.addItem(category)

        self.categoryList.setCurrentIndex(0)
        self.loadPrograms()


    def loadPrograms(self):
        category = self.categoryList.currentText()
        self.search_input.clear()

        # Programme alphabetisch sortieren
        if category == "Installiert":
            sorted_programs = self.loadInstalled()
        elif category == "Alle":
            sorted_programs = self.all_apps
        elif category == "Favoriten":
            sorted_programs = sorted(self.favorites)
        else:
            sorted_programs = sorted([
                app_name for app_name, data in self.program_data.items()
                if data["category"] == category
            ])
        self.filter_categorie(sorted_programs)

        return


    def prepare_programmlist(self):

        # Programme alphabetisch sortieren
        sorted_programs = sorted(self.all_apps)

        for app_name in sorted_programs:
            beschreibung = self.program_data.get(app_name, {}).get("short-desc", "")
            app_id = self.program_data.get(app_name, {}).get("id")
            tooltip = beschreibung
            if beschreibung and len(beschreibung) > 55:
                beschreibung = beschreibung[:50].rstrip() + " …"


            # HTML-Text definieren
            html = f"""
            <div>
                <span style="font-size:"""+str(int(12*self.faktor))+f"""pt; font-weight:bold;">{app_name}</span><br>
                <span style="font-size:"""+str(int(9*self.faktor))+f"""pt;">{beschreibung}</span>
            </div>
            """


            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(0)
            icon_path=f"{self.icons_dir}{app_id}.png"
            # Icon-Label

            if not os.path.exists(icon_path):
                icon_path="/usr/share/x-live/flatman/icons/no_screenshot.png"

            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(int(32*self.faktor), int(32*self.faktor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            #icon_label.setIcon(QIcon(icon_path))   
            #icon_label.setIconSize(QSize(int(32*self.faktor), int(32*self.faktor)))      
            icon_label.setFixedWidth(int(42*self.faktor))

            # Text-Label
            text_label = QLabel()
            text_label.setText(html)
            text_label.setTextFormat(Qt.RichText)
            text_label.setWordWrap(True)
            text_label.setToolTip(tooltip)

            layout.addWidget(icon_label)
            layout.addWidget(text_label)
            widget.setLayout(layout)
            widget.setFixedWidth(self.lwidth-5)

            item = QListWidgetItem()
            self.programList.addItem(item)
            self.programList.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, app_name)

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

    def loadAll(self):
        try:
            result = subprocess.run(
                ["flatpak", "remote-ls", "--app", "--columns=name"],
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
            
    def loadPermissions(self):
        if self.scroll.isVisible():

            self.perm_widget = None
            self.clearLayout(self.permlayout)
            app_name = self.last_item.data(Qt.UserRole)
            app_id = self.program_data.get(app_name, {}).get("id")
            self.perm_widget=flatperm.FlatPerm(app_id,self.faktor*1.2)
            #self.descriptionText.hide()
            #self.descriptionLabel.hide()
            #self.screenshotArea.hide()
            self.scroll.hide()
            #self.infoLayout.addWidget(self.scroll)
            self.permlayout.addWidget(self.perm_widget)
        else:
            self.scroll.show()
            self.clearLayout(self.permlayout) 
        

    def onProgramClicked(self, item):
        self.scroll.verticalScrollBar().setValue(0)  # Scrollt ganz nach oben

        self.scroll.show()
        self.clearLayout(self.permlayout) 
        self.descriptionText.show()
        self.descriptionLabel.show()
        self.screenshotlabel.show()     
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
        self.programList.setStyleSheet("QListWidget::item:selected {border-radius: " + str(int(5*self.faktor)) + "px; background-color: #65" + self.color + ";color: #" + self.color + ";}") 
        print(self.color)
        for index in range(self.programList.count()):
            item = self.programList.item(index)
            widget = self.programList.itemWidget(item)
            if widget:
                if item == current_item:
                    widget.setStyleSheet("QWidget:hover {padding: 0px;} QWidget {background: transparent;padding: 0px;} QLabel:hover {background: transparent; } QLabel {background: transparent; }")
                else:
                    widget.setStyleSheet("QWidget {padding: 0px;} QWidget:hover {background: #45" + self.color + "; border-radius: " + str(int(5*self.faktor)) + "px; padding: 0px;} QLabel:hover {background: transparent; } QLabel {background: transparent; }")

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

        icon_path=f"{self.icons_dir}{app_id}.png"
            # Icon-Label
        if not os.path.exists(icon_path):
            icon_path="/usr/share/x-live/flatman/icons/no_screenshot.png"

        pixmap = QPixmap(icon_path).scaled(int(64*self.faktor), int(64*self.faktor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(int(64*self.faktor), int(64*self.faktor))

        if app_name in self.favorites:
            self.favButton.setStyleSheet(""" QPushButton {background: green;color: white;font-size: """+str(int(26*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("aus Favoriten entfernen")
        else:         
            self.favButton.setStyleSheet(""" QPushButton {background: gray;color: white;font-size: """+str(int(26*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("zu Favoriten hinzufügen")

        thumbnail, description, info_version, info_installed = self.get_flatpak_info(app_name)

        self.descriptionLabel.setText(f" App-ID: {app_id}\n Version: {info_version}\n Speicherbedarf: {info_installed}\n\nBeschreibung:")
        self.descriptionLabel.setStyleSheet("""font-size: """+str(int(18*self.faktor))+"""px;""")



        pixmap = QPixmap("/usr/share/x-live/flatman/icons/no_screenshot.png")
        self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        #print("-"+thumbnail+"-")
        
        picture_save_path=f"{self.thumbnails_dir}{self.app_id}.jpg"
        if os.path.exists(picture_save_path):
            pixmap = QPixmap(picture_save_path)  # Lade das konvertierte Bild
            self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            pass
            try:
                # Bild von der URL herunterladen
                response = requests.get(thumbnail, timeout=2)     
                if response.status_code == 200:
                    # Temporäre Datei für das Bild erstellen
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.webp') as temp_file:
                        temp_file.write(response.content)
                        temp_file_path = temp_file.name
                    #print("downloaded_here")
                    picture_save_path=f"{self.thumbnails_dir}{self.app_id}.jpg"
                    self.convert_image_format(temp_file_path, 'downloaded_image.jpg')
                    if not os.path.exists(self.thumbnails_dir):
                        os.makedirs(self.thumbnails_dir)
                    self.convert_image_format(temp_file_path, picture_save_path)  # Konvertiere in JPG
                    pixmap = QPixmap('downloaded_image.jpg')  # Lade das konvertierte Bild

                    if pixmap.isNull():
                        self.screenshotlabel.setText("Fehler beim Laden des WebP-Bildes.")
                    else:
                        self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

                else:
                    self.screenshotlabel.setText("Fehler beim Herunterladen des Bildes.")

            except Exception as e:
                print(f"[ERROR] Fehler beim Abrufen des Thumbnails: {e}")
                pixmap = QPixmap("/usr/share/x-live/flatman/icons/no_screenshot.png")
                self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        try:
            cmd = "flatpak list --app".split(" ")
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.splitlines()
            self.installed = []
            for line in lines:
                self.installed.append(line.split("\t")[1])
            if app_id in self.installed:
                self.permButton.show()
                self.uninstallButton.show()
                self.startButton.show()
                self.installButton.hide()
                
            else:
                self.permButton.hide()
                self.uninstallButton.hide()
                self.startButton.hide()
                self.installButton.show()

            self.uninstallButton.setEnabled(True)
            self.installButton.setEnabled(True)
            #description1 = self.translate_text(description)
            self.descriptionText.setText(description)
            self.descriptionText.setStyleSheet("""font-size: """+str(int(15*self.faktor))+"""px;""")
            self.nameLabel.setText(f"{app_name}")
                   
        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen der Programmdetails-hier: {e}")
            self.descriptionText.setText("")
        
            
    def translate_text(self, text, source="en", target="de"):
        if os.path.exists(self.trans_file):
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
        if filter_text == "": 
            self.loadPrograms()
            return

        for row in range(self.programList.count()):
            item = self.programList.item(row)
            widget = self.programList.itemWidget(item)
            if widget:
                # Angenommen, das Widget ist ein QLabel
                app_name = item.data(Qt.UserRole)
                beschreibung = self.program_data.get(app_name, {}).get("short-desc", "")
                text = app_name.lower() + " " + beschreibung.lower()
                item.setHidden(filter_text not in text)

    def filter_categorie(self,filter_text):
        #print(filter_text)
        for row in range(self.programList.count()):
            item = self.programList.item(row)
            widget = self.programList.itemWidget(item)
            if widget:
                # Angenommen, das Widget ist ein QLabel
                app_name = item.data(Qt.UserRole)
                item.setHidden(app_name not in filter_text)

        if len(filter_text) == 0:
            pixmap = QPixmap("/usr/share/x-live/flatman/icons/no_screenshot.png")
            self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            self.uninstallButton.setEnabled(False)
            self.installButton.setEnabled(False)
            self.startButton.hide()
            self.favButton.setEnabled(False)
            self.descriptionLabel.setText("Es befinden sich in der Kategorie keine Apps !")
            #description1 = self.translate_text(description)
            self.descriptionText.setText("")
            self.nameLabel.setText(f"Keine Apps vorhanden")
        else:
            self.favButton.setEnabled(True)
            for i in range(self.programList.count()):
                item = self.programList.item(i)
                if not item.isHidden():
                    self.programList.setCurrentItem(item)
                    break

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

    # Farbprofil abrufen und anwenden
                     
    def background_color(self):
        bcolor,color  = themecolor.theme_color()
        if not bcolor and color:
            print("default color")
            bcolor = "#0d0d0d"
            color = "#eeeeec"
        self.setStyleSheet(f"background: {bcolor};color: {color}")
    
    def app_start(self):
        cmd = (f"flatpak run {self.app_id}").split(" ")
        subprocess.Popen(cmd)
                
    def install_start(self):
        self.programList.setEnabled(False)
        self.categoryList.setEnabled(False)
        #self.loadButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.installButton.setEnabled(False)
        self.install_package(self.app_id)

            
    def uninstall_start(self):
        self.programList.setEnabled(False)
        self.categoryList.setEnabled(False)
        #self.loadButton.setEnabled(False)
        self.uninstallButton.setEnabled(False)
        self.installButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.uninstall_package(self.app_id)

    def un_install_finished(self):
        self.programList.setEnabled(True)
        self.categoryList.setEnabled(True)
        #self.loadButton.setEnabled(True)  
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
