#!/usr/bin/python3

import os
import json
import requests
import subprocess
import flatperm
import themecolor
import about
import x_app_updates
from datetime import datetime
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel, QTextEdit, QScrollArea, QMessageBox, QComboBox, QLineEdit, QAction, QMenu, QMenuBar, QListView, QProgressBar, QCheckBox
from PyQt5.QtGui import QPixmap, QIcon, QPixmap
from PyQt5.QtCore import Qt, QProcess, QSize, QTimer, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import tempfile
from PIL import Image

class FlatpakApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.reload = False
        self.wait_for_main()
        self.manager = QNetworkAccessManager()
        self.faktor = app.desktop().height()/1000

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
        
        #self.categories_ordered = ["Favoriten","Spiele","Büro","Grafik","AudioVideo","Zubehör","Internet","Bildung","Wissenschaft","Entwicklung","System","Andere","Alle"]  # Geordnete Liste der Kategorien


        self.categories_ordered = ["Favoriten","Game", "Office", "Graphics", "AudioVideo", "Utility", "Network", "Education", "Science", "Development", "System","Other","Alle" ]
        self.categories_trans = {"Favoriten":"Favoriten","Spiele":"Game", "Büro":"Office", "Grafik":"Graphics", "AudioVideo":"AudioVideo", "Dienstprogramme":"Utility", "Internet":"Network", "Bildung":"Education", "Wissenschaft":"Science", "Entwicklung":"Development", "System":"System","Sonstiges":"Other","Alle":"Alle" }
        self.categories_de = ["Favoriten","Spiele", "Büro", "Grafik", "AudioVideo", "Dienstprogramme", "Internet", "Bildung", "Wissenschaft", "Entwicklung", "System","Sonstiges","Alle"]


        self.categories_ordered
        QTimer.singleShot(3,self.initUI)

    def wait_for_main(self):
        self.wait_win = QWidget()
        layout= QVBoxLayout()
        self.wait_win.setWindowIcon(QIcon("/usr/share/pixmaps/x-live-flatman.png"))
        self.wait_win.setWindowTitle("X-Live FlatMan")
        wait_label = QLabel("Daten werden vorbereitet")
        layout.addWidget(wait_label)
        self.wait_win.setLayout(layout)
        self.wait_win.show()
        #x = app.desktop().width()
        bcolor,color  = themecolor.theme_color()
        if not bcolor and color:
            print("default color")
            bcolor = "#0d0d0d"
            color = "#eeeeec"
        self.wait_win.setStyleSheet(f"background: {bcolor};color: {color}")

    def initUI(self):
        self.faktor = app.desktop().height()/1000
        #self.faktor = 1.0
        screen = QApplication.screenAt(self.pos())
        print(screen)
        self.setWindowTitle("X-Live FlatMan")
        x = int(app.desktop().width()/2-int(750*(self.faktor+0.3)/2))
        y = int(app.desktop().height()/2-int(650*(self.faktor+0.3)/2))
        print(x,y, app.desktop().width(), app.desktop().height())
        #self.setGeometry(x, y, int(750*(self.faktor+0.3)), int(650*self.faktor))
        self.setMinimumSize(int(750*(self.faktor+0.3)), int(650*self.faktor))
        self.setWindowIcon(QIcon("/usr/share/pixmaps/x-live-flatman.png"))
        lwidth = int(232*self.faktor)
        self.lwidth = lwidth
        desheight = int(200*self.faktor)
        catheight = int(100*self.faktor)
        sshotheight = int(320*self.faktor)
        statuswidth= int(620*self.faktor)
        statusheight= int(22*self.faktor)
        buttonheight= int(35*self.faktor)
        
        self.last_item = None
        self.process = None
        self.programList = None
        self.main_menu = "store"
        self.flatpak_updates = []
        self.flatpak_version = {}
        self.flatpak_id = {}
        self.check_flatpak_updates()  
        self.update_layouts = [] 
        
        self.style_main_menu = "QPushButton {font-size: " + str(int(14*self.faktor)) + "px;background: #" + self.bcolor +";color: #" + self.color + ";} QPushButton:hover {background: #a0" + self.color + ";color: #" + self.bcolor + ";}"
        self.style_main_menu_aktiv = "QPushButton {font-size: " + str(int(14*self.faktor)) + "px;background: #004000;color: #ffffff;} QPushButton:hover {background: #a0" + self.color + ";color: #004000;}"        
        self.checkbox_style ="""
            QCheckBox::indicator {
                    width: """+str(int(36*self.faktor))+"""px;
                    height: """+str(int(36*self.faktor))+"""px;
                }
                QCheckBox::indicator:unchecked {
                    image: url(/usr/share/x-live/flatman/icons/off1.png);
                }
                QCheckBox::indicator:checked {
                    image: url(/usr/share/x-live/flatman/icons/on1.png);
                }
            """
        # Menübar erstellen
        menubar = QMenuBar()
        #menubar.setStyleSheet(f"font-size: {str(int(22*self.faktor))}px")
        menubar.setMaximumWidth(int(30*self.faktor))
        # Menü hinzufügen
        menu_menu = menubar.addMenu("⋮")
        menu_menu.setStyleSheet(f"font-size: {str(int(14*self.faktor))}px;background: #20{self.color};")
        #menu_menu.setIcon(QIcon("/usr/share/x-live/flatman/icons/menu.png"))
        #menu_menu.setStyleSheet(f"background: #80{self.bcolor};color: #80{self.color};")
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
        
        self.mainLayout=QVBoxLayout()
        self.layout = QHBoxLayout()
        self.titleLayout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()
        self.updateLayout = QVBoxLayout()
        self.dataLayout = QVBoxLayout()
        self.permlayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.updatebuttonLayout = QHBoxLayout()
        self.rightLayout = QVBoxLayout()

        self.mainLayout.addLayout(self.titleLayout)
        self.mainLayout.addLayout(self.layout)
        self.rightLayout.addLayout(self.buttonLayout)

        #main menu Buttons
        self.titleLayout.addWidget(menubar)
        self.storeButton = QPushButton("Stöbern")
        self.storeButton.clicked.connect(self.main_menu_store)
        self.storeButton.setStyleSheet(self.style_main_menu_aktiv)
        self.titleLayout.addWidget(self.storeButton)

        self.recommendationButton = QPushButton("Empfehlungen")
        self.recommendationButton.setStyleSheet(self.style_main_menu)
        #self.titleLayout.addWidget(self.recommendationButton)

        self.installedButton = QPushButton("Installiert")
        self.installedButton.clicked.connect(self.main_menu_installed)
        self.installedButton.setStyleSheet(self.style_main_menu)
        self.titleLayout.addWidget(self.installedButton)

        self.updatesButton = QPushButton("Aktuallisierungen")
        self.updatesButton.clicked.connect(self.main_menu_updates)
        self.updatesButton.setStyleSheet(self.style_main_menu)
        self.titleLayout.addWidget(self.updatesButton)

        # Suchleiste
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Apps filtern...")
        self.search_input.setStyleSheet(f"font-size: {str(int(14*self.faktor))}px;")
        self.search_input.textChanged.connect(self.start_filter)
        self.search_input.setFixedSize(lwidth,buttonheight)
        self.leftLayout.addWidget(self.search_input)
        
        # Kategorie auswahl box
        self.categoryList = QComboBox()
        self.categoryList.setFixedSize(lwidth,buttonheight)
        self.categoryList.setStyleSheet("QComboBox {font-size: " + str(int(14*self.faktor)) + "px;} QComboBox QAbstractItemView {selection-background-color: #" + self.color + ";selection-color: #" + self.bcolor + ";} ")
        self.categoryList.setFocusPolicy(Qt.NoFocus)
        self.categoryList.currentIndexChanged.connect(self.loadPrograms)
        self.leftLayout.addWidget(self.categoryList)

        # Programmliste
        self.programList = QListWidget()
        self.programList.currentItemChanged.connect(self.onProgramClicked)
        self.programList.setFixedWidth(lwidth)
        self.programList.setFocusPolicy(Qt.NoFocus)
        self.leftLayout.addWidget(self.programList)
        self.programList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.programList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # title leiste
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

        # Statuslabel für alle informationen von aktionen
        self.statusLabel = QLabel("")
        self.rightLayout.addWidget(self.statusLabel)
        self.rightLayout.addLayout(self.updatebuttonLayout)
        self.statusLabel.setFixedHeight(statusheight)
        self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;")
     
        # buttons für bereich updates 
        self.updatebuttonLayout.addStretch(2)
        
        self.checkAllUpdatesBtn = QCheckBox("  Alle auswählen")
        self.updatebuttonLayout.addWidget(self.checkAllUpdatesBtn)
        self.checkAllUpdatesBtn.setStyleSheet(self.checkbox_style)
        self.checkAllUpdatesBtn.setFixedWidth(int(582*self.faktor))
        self.checkAllUpdatesBtn.toggled.connect(self.update_toggle_all)
        self.checkAllUpdatesBtn.hide()
        self.updatebuttonLayout.addStretch(1)

        self.installUpdatesBtn = QPushButton("Ausgewählte Updates installieren")
        self.installUpdatesBtn.setFixedWidth(int(280*self.faktor))
        self.updatebuttonLayout.addWidget(self.installUpdatesBtn)
        self.installUpdatesBtn.clicked.connect(self.update_start)
        self.installUpdatesBtn.hide()

        self.updatebuttonLayout.addStretch(2)

        # knopf layout für menu stöbern und installiert
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
        self.favButton.setFixedWidth(int(30*self.faktor))
        self.favButton.clicked.connect(self.fav_btn_clicked)
        self.favButton.setStyleSheet(""" QPushButton {background: grey;color: white;font-size: """+str(int(24*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
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

        self.updatescroll = QScrollArea()
        self.updatescroll.setWidgetResizable(True)
        self.updatescrollWidget = QWidget()
        self.updatescrollWidget.setLayout(self.updateLayout)
        self.updatescroll.setWidget(self.updatescrollWidget)

        self.infoLayout.addLayout(self.permlayout)
        self.infoLayout.addWidget(self.scroll)
        self.infoLayout.addWidget(self.updatescroll)

        self.rightLayout.addLayout(self.infoLayout)

        self.layout.addLayout(self.rightLayout)

        self.central_widget= QWidget(self)
        
        self.central_widget.setLayout(self.mainLayout)
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
        #print("fehler 3")
        os.system("appstreamcli refresh-cache")
        os.system("python3 /usr/share/x-live/flatman/update.py") 
        #self.show()
        self.wait_for_main()
        QTimer.singleShot(3,self.loadSavedData)


    def displayCategories(self):
        
        self.prepare_programmlist()
        self.check_installed()
        self.wait_win.close()
        self.show()
        self.categoryList.clear()
        for category in self.categories_de:
            self.categoryList.addItem(category)

        self.categoryList.setCurrentIndex(0)
        self.loadPrograms()

    def main_menu_updates(self):
        self.main_menu = "updates"
        self.categoryList.hide()
        self.updatescroll.setVisible(True)
        self.scroll.setVisible(False)
        self.search_input.hide()
        self.programList.hide()
        self.descriptionText.hide()
        self.descriptionLabel.hide()
        self.screenshotlabel.hide()    
        self.storeButton.setStyleSheet(self.style_main_menu)
        self.recommendationButton.setStyleSheet(self.style_main_menu)
        self.installedButton.setStyleSheet(self.style_main_menu)
        self.updatesButton.setStyleSheet(self.style_main_menu_aktiv)
        self.clearLayout(self.permlayout) 
        #self.clearLayout(self.updateLayout) 
        self.hideLayout(self.buttonLayout)
        self.showLayout(self.updatebuttonLayout)
        self.update_layouts_clear()
        self.flatpakUpdater()

    def main_menu_installed(self):
        self.main_menu = "installed"
        self.categoryList.hide()
        self.updatescroll.setVisible(False)
        self.scroll.setVisible(True)
        self.search_input.hide()
        self.programList.show()
        self.storeButton.setStyleSheet(self.style_main_menu)
        self.recommendationButton.setStyleSheet(self.style_main_menu)
        self.installedButton.setStyleSheet(self.style_main_menu_aktiv)
        self.updatesButton.setStyleSheet(self.style_main_menu)
        self.showLayout(self.buttonLayout)
        self.hideLayout(self.updatebuttonLayout)
        self.onProgramClicked(self.last_item)
        #self.clearLayout(self.updateLayout)
        self.loadPrograms()

    def main_menu_store(self):
        self.main_menu = "store"
        self.hideLayout(self.updatebuttonLayout)
        self.categoryList.show()
        self.updatescroll.setVisible(False)
        self.clearLayout(self.updateLayout)
        self.scroll.setVisible(True)
        self.search_input.show()
        self.programList.show()
        self.storeButton.setStyleSheet(self.style_main_menu_aktiv)
        self.recommendationButton.setStyleSheet(self.style_main_menu)
        self.installedButton.setStyleSheet(self.style_main_menu)
        self.updatesButton.setStyleSheet(self.style_main_menu)
        self.showLayout(self.buttonLayout)
        self.onProgramClicked(self.last_item)
        self.loadPrograms()


    def loadPrograms(self):
        category = self.categories_trans[self.categoryList.currentText()]
        self.search_input.clear()
        self.updatescroll.setVisible(False)

        # Programme alphabetisch sortieren
        if self.main_menu == "installed":
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

    def flatpakUpdater(self):
        self.update_layouts_clear()
        self.sorted_updates = self.check_flatpak_updates()
        self.check_btns = {}
        self.update_app_list = []
        self.update_layouts = []
        #print(sorted_programs)
        for app in self.sorted_updates:
            tempLayout = QHBoxLayout()
            temp2Layout = QVBoxLayout()
            app_id = self.flatpak_id[app]
            #print(app_id)
            desc = self.program_data.get(app, {}).get("short-desc")
            update_version = self.flatpak_version[app]
            version = self.program_data.get(app, {}).get("version")
            if desc: 
                if len(desc) > 50: 
                    desc = desc[:47]+"..."
            icon_path=f"{self.icons_dir}{app_id}.png"
            if not os.path.exists(icon_path):
                icon_path="/usr/share/x-live/flatman/icons/no_screenshot.png"

            pixmap = QPixmap(icon_path).scaled(int(36*self.faktor), int(36*self.faktor), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            check = QCheckBox()
            check.setStyleSheet(self.checkbox_style)
            check.setProperty("user_data", app)
            check.stateChanged.connect(self.update_toggle)

            temp_icon_label = QLabel()
            temp_icon_label.setPixmap(pixmap)
            temp_icon_label.setFixedSize(int(36*self.faktor), int(36*self.faktor))
            temp_name_label = QLabel(f"{app}")
            temp_name_label.setFixedWidth(int(430*self.faktor))
            temp_name_label.setStyleSheet(f"font-size: {int(22*self.faktor)}px;")
            temp_desc_label = QLabel(f"{desc}")
            temp_desc_label.setFixedWidth(int(430*self.faktor))
            temp_desc_label.setStyleSheet(f"font-size: {int(12*self.faktor)}px;")
            self.check_btns[app] = check


            temp_vold_label = QLabel(f"{version}")
            temp_vold_label.setFixedWidth(int(180*self.faktor))
            temp_vold_label.setStyleSheet(f"font-size: {int(18*self.faktor)}px;")


            temp_vnew_label = QLabel(f"{update_version}")
            temp_vnew_label.setFixedWidth(int(180*self.faktor))
            temp_vnew_label.setStyleSheet(f"font-size: {int(18*self.faktor)}px;")


            tempLayout.addStretch(5)
            tempLayout.addWidget(check)
            tempLayout.addWidget(temp_icon_label)
            tempLayout.addStretch(0)
            temp2Layout.addWidget(temp_name_label)
            temp2Layout.addWidget(temp_desc_label)
            tempLayout.addLayout(temp2Layout)
            tempLayout.addWidget(temp_vold_label)
            tempLayout.addWidget(temp_vnew_label)
            tempLayout.addStretch(5)
            self.updateLayout.addLayout(tempLayout)
            self.update_layouts.append(temp2Layout)
            self.update_layouts.append(tempLayout)
        self.updateLayout.addStretch(0)
        
    def update_toggle(self, checked):
        
        userrole = self.sender().property("user_data")
        app_id = self.flatpak_id[userrole]
        if self.sender().isChecked():
            if app_id not in self.update_app_list:
                self.update_app_list.append(app_id)
        else:
            self.update_app_list.remove(app_id)
        print(self.update_app_list)

    def update_toggle_all(self, checked):
        for app in self.sorted_updates:
            self.check_btns[app].setChecked(self.sender().isChecked())
        

    def update_layouts_clear(self):
        #print(len(self.update_layouts))
        if self.update_layouts:
            for x,layout in enumerate(self.update_layouts):
                self.clearLayout(layout)
        self.update_layouts = []
        self.clearLayout(self.updateLayout)

    def prepare_programmlist(self):

        self.programList.clear()
        # Programme alphabetisch sortieren
        sorted_programs = sorted(self.all_apps)
        for app_name in sorted_programs:
            beschreibung = self.program_data.get(app_name, {}).get("short-desc", "")
            #if beschreibung != "":
            #    beschreibung = self.translate_text(beschreibung)
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
            #icon_label.setStyleSheet("background: transparent;")

            # Text-Label
            text_label = QLabel()
            text_label.setText(html)
            text_label.setTextFormat(Qt.RichText)
            text_label.setWordWrap(True)
            text_label.setToolTip(tooltip)
            #text_label.setStyleSheet("background: transparent;")

            layout.addWidget(icon_label)
            layout.addWidget(text_label)
            widget.setLayout(layout)
            widget.setFixedWidth(self.lwidth-5)

            item = QListWidgetItem()
            
            widget.setStyleSheet("QWidget {padding: 0px;background: transparent;} QWidget:hover {background: #45" + self.color + "; border-radius: " + str(int(5*self.faktor)) + "px; padding: 0px;} QLabel:hover {background: transparent; } QLabel {background: transparent; }")

            self.programList.addItem(item)
            self.programList.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, app_name)
        self.programList.setStyleSheet("QListWidget::item:selected {border-radius: " + str(int(5*self.faktor)) + "px; background-color: #65" + self.color + ";color: #" + self.color + ";}") 

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
            self.scroll.setVisible(False)
            #self.infoLayout.addWidget(self.scroll)
            self.permlayout.addWidget(self.perm_widget)
        else:
            self.scroll.setVisible(True)
            self.clearLayout(self.permlayout) 
        

    def onProgramClicked(self, item):
        self.scroll.verticalScrollBar().setValue(0)  # Scrollt ganz nach oben

        self.scroll.setVisible(True)
        self.clearLayout(self.permlayout) 
        self.descriptionText.show()
        self.descriptionLabel.show()
        self.screenshotlabel.show()     
        if not self.reload:
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;")
        self.reload = False
        
        if item:
            try:
                app_name = item.data(Qt.UserRole)
                app_id = self.program_data.get(app_name, {}).get("id")
                self.last_item = item
                #self.highlightSelectedItem(item)  # 👈 HIER wird das Styling aktualisiert

                if app_id:
                    self.displayProgramDetails(app_id, app_name)
            except Exception as e:
                print("Fehler beim Klicken:", e)

    def highlightSelectedItem(self, current_item):
        self.programList.setStyleSheet("QListWidget::item:selected {border-radius: " + str(int(5*self.faktor)) + "px; background-color: #65" + self.color + ";color: #" + self.color + ";}") 
        #print(self.color)
        for index in range(self.programList.count()):
            item = self.programList.item(index)
            app_name = item.data(Qt.UserRole)
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
            self.favButton.setStyleSheet(""" QPushButton {background: green;color: white;font-size: """+str(int(24*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("aus Favoriten entfernen")
        else:         
            self.favButton.setStyleSheet(""" QPushButton {background: gray;color: white;font-size: """+str(int(24*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("zu Favoriten hinzufügen")

        thumbnail, description, info_version, info_installed = self.get_flatpak_info(app_name)
        QTimer.singleShot(100, lambda: self.get_thumbnail(thumbnail))

        self.descriptionLabel.setText(f" App-ID: {app_id}\n Version: {info_version}\n Speicherbedarf: {info_installed}\n\nBeschreibung:")
        if app_name in self.flatpak_updates:
            self.descriptionLabel.setText(f" App-ID: {app_id}\n installierte Version: {info_version} Aktuallisierug auf {self.flatpak_version[app_name]} verfügbar\n Speicherbedarf: {info_installed}\n\nBeschreibung:")
        self.descriptionLabel.setStyleSheet("""font-size: """+str(int(18*self.faktor))+"""px;""")



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

        try:
            self.uninstallButton.setEnabled(True)
            self.installButton.setEnabled(True)
            #description1 = self.translate_text(description)
            self.descriptionText.setText(description)
            self.descriptionText.setStyleSheet("""font-size: """+str(int(15*self.faktor))+"""px;""")
            self.nameLabel.setText(f"{app_name}")
                   
        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen der Programmdetails-hier: {e}")
            self.descriptionText.setText("")
        self.screenshotlabel.hide()
        
        #QTimer.singleShot(100,self.get_thumbnail)


    def get_thumbnail(self, thumbnail):
        app_id = self.app_id
        #thumbnail = self.thumbnail
        picture_save_path=f"{self.thumbnails_dir}{app_id}.jpg"
        if os.path.exists(picture_save_path):
            pixmap = QPixmap(picture_save_path)  # Lade das konvertierte Bild
            self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.screenshotlabel.show()
        else:
            pixmap = QPixmap("/usr/share/x-live/flatman/icons/no_screenshot.png")
            self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

            filepath = f"/tmp/{app_id}.webp"
            self.start_download(thumbnail, filepath, app_id)
            
    def place_thumbnail(self,filepath,app_id):
        if self.main_menu == "updates": return
        picture_save_path=f"{self.thumbnails_dir}{app_id}.jpg"
        if not os.path.exists(self.thumbnails_dir):
            os.makedirs(self.thumbnails_dir)
        self.convert_image_format(filepath, picture_save_path)  # Konvertiere in JPG
        if self.app_id != app_id:
            return        
        if self.main_menu == "updates": return                 
        pixmap = QPixmap(picture_save_path)  # Lade das konvertierte Bild
        if pixmap.isNull():
            self.screenshotlabel.setText("Fehler beim Laden des WebP-Bildes.")
        else:
            self.screenshotlabel.setPixmap(pixmap.scaled(int(600*self.faktor), int(300*self.faktor), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.screenshotlabel.show()

    def start_download(self, url, filepath,app_id):
        request = QNetworkRequest(QUrl(url))
        self.reply = self.manager.get(request)

        #self.reply.downloadProgress.connect(self.update_progress)
        self.reply.finished.connect(lambda: self.download_finished(filepath,app_id))

    def update_progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            percent = int((bytes_received / bytes_total) * 100)
            print(percent)

    def download_finished(self,filepath,app_id):
        data = self.reply.readAll()
        with open(filepath, "wb") as f:
            f.write(data)
        self.reply.deleteLater()
        self.place_thumbnail(filepath,app_id)

    def check_installed(self): 
        try:
            cmd = "flatpak list --app".split(" ")
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.splitlines()
            self.installed = []
            for line in lines:
                self.installed.append(line.split("\t")[1])   
        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen von installierten Apps: {e}")
            
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

    def hideLayout(self, layout):
        if layout is not None:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() is not None:
                    item.widget().hide()

    def showLayout(self, layout):
        if layout is not None:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() is not None:
                    item.widget().show()

    def start_filter(self):
        self.filter_cancelled = True  # Vorherigen Durchlauf abbrechen
        QTimer.singleShot(30, self.filter_list)

            


    def filter_list(self):
        """ Die Liste der Programme basierend auf der Benutzereingabe filtern """
        self.filter_cancelled = False
        filter_text = self.search_input.text().lower()
        if filter_text == "": 
            self.loadPrograms()
            return

        for row in range(self.programList.count()):
            if self.filter_cancelled:
                return
            item = self.programList.item(row)
            widget = self.programList.itemWidget(item)
            if widget:
                # Angenommen, das Widget ist ein QLabel
                app_name = item.data(Qt.UserRole)
                beschreibung = self.program_data.get(app_name, {}).get("short-desc", "")
                description = self.program_data.get(app_name, {}).get("description")
                text = app_name.lower() + " " + beschreibung.lower() + " " + description.lower()
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
            self.favButton.setStyleSheet(""" QPushButton {background: gray;color: white;font-size: """+str(int(24*self.faktor))+"""px;}QPushButton:disabled {background: gray;color: light_gray;}""")
            self.favButton.setToolTip("zu Favoriten hinzufügen")

        else:
            self.favorites.append(app_name)
            self.favButton.setStyleSheet(""" QPushButton {background: green;color: white;font-size: """+str(int(24*self.faktor))+"""px;} QPushButton:disabled {background: gray;color: light_gray;}""")
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

    def update_start(self):
        #print("[debug] update Start")
        if self.update_app_list:       
            self.update_package(self.update_app_list)

    def update_finished(self):
        self.process = None
        #print("update abgeschlossen !!")
        self.main_menu_updates()

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

    def check_for_updates(self):
        updates = self.check_flatpak_updates()
        #print(updates)

    def check_flatpak_updates(self):
        try:
            # Überprüfen, ob Flatpak installiert ist
            
            self.flatpak_updates = []
            self.flatpak_version = {}
            self.flatpak_id = {}
            if subprocess.run(['which', 'flatpak'], stdout=subprocess.PIPE).returncode != 0:
                print("Flatpak is not installed.")
                return []

            # Führe den Befehl aus, um nach Flatpak-Updates zu suchen
            result = subprocess.run(['flatpak', 'remote-ls', '--updates'], stdout=subprocess.PIPE, text=True)
            updates = result.stdout.strip().split('\n')
            #print(f"Flatpak Updates:\n{updates}")
            
            # Berechne die Anzahl der Flatpak-Updates (leerzeilen ignorieren)
            self.flatpak_updates = [line.split("\t")[0] for line in updates if line]
            self.flatpak_version = {line.split("\t")[0]: line.split("\t")[2] for line in updates if line}
            self.flatpak_id = {line.split("\t")[0]: line.split("\t")[1] for line in updates if line}

            return sorted(self.flatpak_updates, key=str.lower)

        except Exception as e:
            print(f"Error checking Flatpak updates: {e}")
            return []

    def install_package(self,app_id):
        if not self.process:
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;")
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
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished_remove)
            
            # Prepare the command
            command = f'flatpak uninstall -y {app_id}'
            self.process.start('sh', ['-c', command])

    def update_package(self, app_id):
        if not self.process:
            #print("[debug] update Start 1")
            self.statusLabel.show()
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished_update)

            # Liste in String umwandeln, wenn nötig
            if isinstance(app_id, list):
                apps = " ".join(app_id)
            else:
                apps = app_id

            command = f'flatpak update -y {apps}'
            self.process.start('sh', ['-c', command])




    def update_package_old(self,app_id):
        if not self.process:
            self.statusLabel.setText("")
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished_update)
            
            # Prepare the command
            command = f'flatpak update -y {app_id}'
            self.process.start('sh', ['-c', command])





    def read_output(self):
        if self.process:
            output = self.process.readAll().data().decode()
            output = str(output).replace('\r\n', '\n').replace('\r', '\n')
            self.statusLabel.setText(output)

    def process_finished(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.statusLabel.setText(" "+self.translate_text("Installation completed successfully."))
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;background-color: green;color: white;")
            #QMessageBox.information(self, "Success", "Package installed successfully!")
        else:
            self.statusLabel.setText(" "+self.translate_text("Installation failed."))
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;background-color: red;color: white;")
            #QMessageBox.critical(self, "Error", "Failed to install package.")

        self.check_installed()            
        self.un_install_finished()
        
            
    def process_finished_remove(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.statusLabel.setText(" "+self.translate_text("Uninstallation completed successfully."))
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;background-color: green;color: white;")
            #QMessageBox.information(self, "Success", "Package uninstalled successfully!")
        else:
            self.statusLabel.setText(" "+self.translate_text("Uninstallation failed."))
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;background-color: red;color: white;")
            #QMessageBox.critical(self, "Error", "Failed to uninstall package.")
        
        self.check_installed()
        self.un_install_finished()

    def process_finished_update(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.statusLabel.setText(" "+self.translate_text("update completed successfully."))
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;background-color: green;color: white;")
            #QMessageBox.information(self, "Success", "Package uninstalled successfully!")
        else:
            self.statusLabel.setText(" "+self.translate_text("update failed."))
            self.statusLabel.setStyleSheet(f"font-size: {str(int(18*self.faktor))}px;background-color: red;color: white;")
            #QMessageBox.critical(self, "Error", "Failed to uninstall package.")
        
        self.check_installed()
        self.update_finished()

        
if __name__ == '__main__':
    app = QApplication([])
    ex = FlatpakApp()
    app.exec_()
