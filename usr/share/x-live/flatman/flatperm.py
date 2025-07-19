
"""
flatperm.py - GUI-Werkzeug zur Verwaltung von Flatpak-Berechtigungen

Dieses Programm zeigt die Berechtigungen einer Flatpak-App an und erlaubt das Bearbeiten 
von Overrides über eine grafische Oberfläche (PyQt5). Es verwendet das Modul `flatdata.py`, 
um die Metadaten und benutzerdefinierten Einstellungen einer App zu lesen.

Autor: F.Maczollek aka VerEnderT
Lizenz: GNU General Public License Version 3
Abhängigkeiten: PyQt5, flatpak CLI, flatdata.py, themecolor.py
Stand: Juni 2025
"""

import time
import subprocess
import sys
import flatdata
import themecolor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCheckBox, QLabel, QLineEdit,
    QScrollArea, QHBoxLayout, QToolButton, QPushButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt

#
# FlatPerm: PyQt5 GUI zur Anzeige und Bearbeitung von Flatpak-Berechtigungen
#
class FlatPerm(QWidget):
    def __init__(self, app_id, faktor = 1):
        super().__init__()
        self.init_ui(app_id,faktor)

    def init_ui(self, app_id, faktor):
        self.app_id = app_id
        self.faktor = faktor
        self.darkmode = False
        #print(app_id)
        self.app_name = flatdata.get_name(app_id)
        #print(self.app_name)
        bcolor, color = themecolor.theme_color()
        #print(bcolor,color)

        if bcolor == None or color == None:
            bcolor = "0d0d0d"
            color = "eeeeec"
        else:
            bcolor = bcolor.replace("#","")
            color = color.replace("#","")

        # === STYLES: Standard, Buttons, Dark Mode ===
        self.standartStyle= """ QWidget {
                                    
                                    border: none;
                                    background-color: #""" + bcolor + """;
                                    color: #""" + color + """;
                                }
                                QLineEdit {
                                
                                    border: 1px #""" +  color + """;
                                    border-radius: 3px;
                                    background-color: #20afafaf;
                                    font-size: """+str(int(13*faktor))+"""px;
                                    color: #""" + color + """;
                                
                                }
                                QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    text-align: left;
                                    font-size: """+str(int(13*faktor))+"""px;
                                    padding: 0px;
                                    padding-left: 4px;
                                    /*color: inherit;   Optional: Textfarbe */
                                    font: inherit; /* Optional: Schrift vom Eltern-Widget übernehmen */
                                }
                                QPushButton:hover {
                                    background-color: transparent;
                                }
                                QPushButton:pressed {
                                    background-color: transparent;
                                }
                            """
        self.btnStyle =  """    QPushButton {
                                    border: 3px solid #08""" + color + """;
                                    border-radius: 7px;
                                    background-color: #04""" + color + """;
                                    text-align: center;
                                    padding-right: 3px;
                                    padding-left: 3px;
                                    /*color: inherit;   Optional: Textfarbe */
                                    font: inherit; /* Optional: Schrift vom Eltern-Widget übernehmen */
                                }
                                QPushButton:hover {
                                    background-color: #40""" + color + """;
                                }
                                QPushButton:pressed {
                                    background-color: #80""" + color + """;
                                }
                            """
        self.darkStyle=     """ QWidget {
                                    
                                    border: none;
                                    background-color: black;
                                    color: white;
                                }
                                QLineEdit {
                                
                                    border: 1px white;
                                    border-radius: 3px;
                                    background-color: #20afafaf;
                                    color: white;
                                }
                                QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    text-align: left;
                                    padding: 0px;
                                    /*color: inherit;   Optional: Textfarbe */
                                    font: inherit; /* Optional: Schrift vom Eltern-Widget übernehmen */
                                }
                                QPushButton:hover {
                                    background-color: transparent;
                                }
                                QPushButton:pressed {
                                    background-color: transparent;
                                }
                            """
        self.titleStyle =   """    QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    text-align: left;
                                    font-size: """+str(int(24*faktor))+"""px;
                                    padding: 0px;
                                    /*color: inherit;   Optional: Textfarbe */
                                    font: inherit; /* Optional: Schrift vom Eltern-Widget übernehmen */
                                }
                                QPushButton:hover {
                                    background-color: transparent;
                                }
                                QPushButton:pressed {
                                    background-color: transparent;
                                }
                            """
        self.bigTitleStyle= """ QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    text-align: center;
                                    font-size: """+str(int(32*faktor))+"""px;
                                    padding: 0px;
                                    /*color: inherit;   Optional: Textfarbe */
                                    font: inherit; /* Optional: Schrift vom Eltern-Widget übernehmen */
                                }
                                QPushButton:hover {
                                    background-color: transparent;
                                }
                                QPushButton:pressed {
                                    background-color: transparent;
                                }
                            """
        self.descStyle =    """    QPushButton {
                                    border: none;
                                    background-color: transparent;
                                    text-align: left;
                                    font-size: """+str(int(10*faktor))+"""px;
                                    padding: 0px;
                                    color: grey;  
                                    font: inherit; /* Optional: Schrift vom Eltern-Widget übernehmen */
                                }
                                QPushButton:hover {
                                    background-color: transparent;
                                }
                                QPushButton:pressed {
                                    background-color: transparent;
                                }
                            """
        self.setStyleSheet(self.standartStyle)

        # === HAUPTLAYOUT & SCROLLBEREICH ===
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Big Title part
        big_title_Label = QPushButton(f"Berechtigungen für \n{self.app_name}\n")
        big_title_Label.setStyleSheet(self.bigTitleStyle)
        #layout.addWidget(big_title_Label)
        
        

        # === SHARED (z. B. Netzwerkfreigaben) ===
        # shared part
        self.con_shared_Label = QPushButton("Komunikation im Netzwerk")
        self.con_shared_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.con_shared_Label)
        
        self.con_shared_desc_Label = QPushButton("(Shared) Liste der mit dem Hostsystem gemeinsam genutzten Subsysteme")
        self.con_shared_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.con_shared_desc_Label)


        self.con_shared = [
        "network: Zugriff auf das Netzwerk",
        "ipc: Interprozesskommunikation (IPC) mit Host"
        ]
        
        self.con_shared_buttons = []
        self.con_shared_warnings = []
        for btn in self.con_shared:
            temp_layout = QHBoxLayout()
            con_btn = QPushButton(btn)
            con_btn.setCheckable(True)
            con_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/off.png"))
            con_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            con_btn.toggled.connect(self.handle_toggle)
            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            temp_layout.addWidget(con_btn)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            
            content_layout.addLayout(temp_layout)
            self.con_shared_buttons.append(con_btn)
            self.con_shared_warnings.append(warn_btn)
        
        # === SOCKETS (z. B. X11, PulseAudio, Wayland) ===
        # Sockets part
        self.con_sockets_Label = QPushButton("\nSchnittstellen")
        self.con_sockets_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.con_sockets_Label)
        
        self.con_sockets_desc_Label = QPushButton("(Sockets) Liste der in Sandbox verfügbaren Sockets")
        self.con_sockets_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.con_sockets_desc_Label)

        self.con_sockets= [
        "x11: Zugriff auf das X11-Fenstersystem",
        "wayland: Zugriff auf das Wayland-Fenstersystem",
        "fallback-x11: Eingeschränkter Zugriff auf X11 (Fallback)",
        "pulseaudio: Audio-Ausgabe über PulseAudio",
        "session-bus: Zugriff auf den DBus der Benutzersitzung",
        "system-bus: Zugriff auf den System-DBus",
        "ssh-auth: SSH-Agent für Authentifizierung verwenden",
        "pcsc: Zugriff auf Smartcards (z. B. Ausweis)",
        "cups: Zugriff auf Druckdienste (CUPS)",
        "gpg-agent: Zugriff auf GnuPG-Agent (z. B. zum Signieren)"
        ]
        
        self.con_sockets_buttons = []
        self.con_sockets_warnings = []
        for btn in self.con_sockets:
            temp_layout = QHBoxLayout()
            con_btn = QPushButton(btn)
            con_btn.setCheckable(True)
            con_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/off.png"))
            con_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            con_btn.toggled.connect(self.handle_toggle)
            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            temp_layout.addWidget(con_btn)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            
            content_layout.addLayout(temp_layout)
            self.con_sockets_buttons.append(con_btn)
            self.con_sockets_warnings.append(warn_btn)

        # === GERÄTE (z. B. DRI, KVM, shm) ===
        # devices part
        self.con_devices_Label = QPushButton("\nGeräte")
        self.con_devices_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.con_devices_Label)
        
        self.con_devices_desc_Label = QPushButton("(Devices) Liste der in der Sandbox verfügbaren Geräte")
        self.con_devices_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.con_devices_desc_Label)
        
        self.con_devices = [
        "dri: Zugriff auf Grafikbeschleunigung (DRI)",
        "kvm: Zugriff auf KVM-Virtualisierung",
        "shm: Zugriff auf Shared Memory (/dev/shm)",
        "all: Zugriff auf alle Geräte (unsicher!)"
        ]
        
        self.con_devices_buttons = []
        self.con_devices_warnings = []
        for btn in self.con_devices:
            temp_layout = QHBoxLayout()
            con_btn = QPushButton(btn)
            con_btn.setCheckable(True)
            con_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/off.png"))
            con_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            con_btn.toggled.connect(self.handle_toggle)
            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            temp_layout.addWidget(con_btn)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            
            content_layout.addLayout(temp_layout)
            self.con_devices_buttons.append(con_btn)
            self.con_devices_warnings.append(warn_btn)

        # === FEATURES (z. B. Debug, Multiarch) ===
        # features part
        self.con_features_Label = QPushButton("\nFunktionen ")
        self.con_features_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.con_features_Label)
        
        self.con_features_desc_Label = QPushButton("(Features) Liste der Funktionen, die der Anwendung zur Verfügung stehen")
        self.con_features_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.con_features_desc_Label)
        
        self.con_features = [
        "devel: Entwicklungsmodus (z. B. Debug-Zugriff)",
        "multiarch: Zugriff auf mehrere CPU-Architekturen",
        "bluetooth: Zugriff auf Bluetooth-Geräte",
        "canbus: Zugriff auf CAN-Bus (Fahrzeugdaten)",
        "per-app-dev-shm: Separater Shared-Memory-Bereich"
        ]
        
        self.con_features_buttons = []
        self.con_features_warnings = []
        for btn in self.con_features:
            temp_layout = QHBoxLayout()
            con_btn = QPushButton(btn)
            con_btn.setCheckable(True)
            con_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/off.png"))
            con_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            con_btn.toggled.connect(self.handle_toggle)
            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            temp_layout.addWidget(con_btn)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            
            content_layout.addLayout(temp_layout)
            self.con_features_buttons.append(con_btn)
            self.con_features_warnings.append(warn_btn)
        
        # === DATEISYSTEM-ZUGRIFFE (z. B. /home, host-etc) ===
        # filesystems part
        self.con_filesystems_Label = QPushButton("\nDateisysteme")
        self.con_filesystems_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.con_filesystems_Label)
        
        self.con_features_desc_Label = QPushButton("(Filesystems) Liste der Funktionen, die der Anwendung zur Verfügung stehen")
        self.con_features_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.con_features_desc_Label)
        
        self.con_filesystems = [
        "host: Alle Systemdateien",
        "host-os: Alle Systembibliotheken,\nausführbare Dateien sowie statische Daten",
        "host-etc: Alle Systemkonfigurationen",
        "home: Alle Benutzerdateien",
        ]
        
        self.con_filesystems_buttons = []
        self.con_filesystems_box = []
        self.con_filesystems_editLines = []
        self.con_filesystems_warnings = []
        self.con_filesystems_ewarnings = []
        self.con_filesystems_rem_btn_list = []
        for btn in self.con_filesystems:
            temp_layout = QHBoxLayout()
            con_btn = QPushButton(btn)
            con_btn.setCheckable(True)
            con_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/off.png"))
            con_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            con_btn.toggled.connect(self.handle_toggle)
            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            temp_layout.addWidget(con_btn)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            
            content_layout.addLayout(temp_layout)
            self.con_filesystems_buttons.append(con_btn)
            self.con_filesystems_warnings.append(warn_btn)
        temp_layout = QHBoxLayout()
        con_files_other = QPushButton("andere Dateien")
        temp_layout.addWidget(con_files_other)
        temp_layout.addStretch()
        con_files_add = QPushButton()
        con_files_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add_file.png"))
        con_files_add.setStyleSheet(self.btnStyle)
        con_files_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        con_files_add.clicked.connect(lambda: self.add_entry(0))
        temp_layout.addWidget(con_files_add)
        content_layout.addLayout(temp_layout)
        self.con_files_layout = QVBoxLayout()
        content_layout.addLayout(self.con_files_layout)
        
        # === PERSISTENTE VERZEICHNISSE ===
        # persistent part
        self.con_persistent_Label = QPushButton("\nPersistent")
        self.con_persistent_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.con_persistent_Label)
        
        self.con_persistent_desc_Label = QPushButton("(persistent) Liste der Sandbox erstellten homedir-relative Pfade")
        self.con_persistent_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.con_persistent_desc_Label)
        
        self.con_persistent_box = []
        self.con_persistent_editLines = []
        self.con_persistent_ewarnings = []
        self.con_persistent_rem_btn_list = []
        temp_layout = QHBoxLayout()
        con_persistent_other = QPushButton("Dateien")
        temp_layout.addWidget(con_persistent_other)
        temp_layout.addStretch()
        con_persistent_add = QPushButton()
        con_persistent_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add_file.png"))
        con_persistent_add.setStyleSheet(self.btnStyle)
        con_persistent_add.clicked.connect(lambda: self.add_entry(1))
        con_persistent_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        temp_layout.addWidget(con_persistent_add)
        content_layout.addLayout(temp_layout)
        self.con_persistent_layout = QVBoxLayout()
        content_layout.addLayout(self.con_persistent_layout)
        
        
        # === UMGEBUNGSVARIABLEN ===
        # environment part
        self.environment_Label = QPushButton("\nUmgebungsvariablen")
        self.environment_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.environment_Label)
        
        self.environment_desc_Label = QPushButton("(Environment) Liste der Sandbox erstellten homedir-relative Pfade")
        self.environment_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.environment_desc_Label)
        
        
        
        self.environment_box = []
        self.environment_editLines = []
        self.environment_ewarnings = []
        self.environment_rem_btn_list = []
        temp_layout = QHBoxLayout()
        environment_other = QPushButton("Variablen")
        temp_layout.addWidget(environment_other)
        temp_layout.addStretch()
        environment_add = QPushButton()
        environment_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add.png"))
        environment_add.setStyleSheet(self.btnStyle)
        environment_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        environment_add.clicked.connect(lambda: self.add_entry(2))
        temp_layout.addWidget(environment_add)
        content_layout.addLayout(temp_layout)
        self.environment_layout = QVBoxLayout()
        content_layout.addLayout(self.environment_layout)
        
        # === SYSTEM BUS POLICIES ===
        # System Bus part
        self.system_bus_Label = QPushButton("\nSystem Bus")
        self.system_bus_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.system_bus_Label)
        
        self.system_bus_desc_Label = QPushButton("(System Bus Policy) Liste bekannter Namen auf dem Systembus")
        self.system_bus_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.system_bus_desc_Label)
        
        self.system_talk_box = []
        self.system_talk_editLines = []
        self.system_talk_ewarnings = []
        self.system_talk_rem_btn_list = []
        temp_layout = QHBoxLayout()
        system_talk_other = QPushButton("Redet mit ")
        temp_layout.addWidget(system_talk_other)
        temp_layout.addStretch()
        system_talk_add = QPushButton()
        system_talk_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add.png"))
        system_talk_add.setStyleSheet(self.btnStyle)
        system_talk_add.clicked.connect(lambda: self.add_entry(3))
        system_talk_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        temp_layout.addWidget(system_talk_add)
        content_layout.addLayout(temp_layout)
        self.system_talk_layout = QVBoxLayout()
        content_layout.addLayout(self.system_talk_layout)
        
        self.system_own_box = []
        self.system_own_editLines = []
        self.system_own_ewarnings = []
        self.system_own_rem_btn_list = []
        temp_layout = QHBoxLayout()
        system_own_other = QPushButton("\nBesitzt: ")
        temp_layout.addWidget(system_own_other)
        temp_layout.addStretch()
        system_own_add = QPushButton()
        system_own_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add.png"))
        system_own_add.setStyleSheet(self.btnStyle)
        system_own_add.clicked.connect(lambda: self.add_entry(4))
        system_own_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        temp_layout.addWidget(system_own_add)
        content_layout.addLayout(temp_layout)
        self.system_own_layout = QVBoxLayout()
        content_layout.addLayout(self.system_own_layout)

        # === SESSION BUS POLICIES ===
        # Session Bus part
        self.session_bus_Label = QPushButton("\nSession Bus")
        self.session_bus_Label.setStyleSheet(self.titleStyle)
        content_layout.addWidget(self.session_bus_Label)
        
        self.session_desc_Label = QPushButton("(Session Bus Policy) Liste bekannter Namen im Sitzungsbus")
        self.session_desc_Label.setStyleSheet(self.descStyle)
        content_layout.addWidget(self.session_desc_Label)
        
        self.session_talk_box = []
        self.session_talk_editLines = []
        self.session_talk_ewarnings = []
        self.session_talk_rem_btn_list = []
        temp_layout = QHBoxLayout()
        session_talk_other = QPushButton("Redet mit ")
        temp_layout.addWidget(session_talk_other)
        temp_layout.addStretch()
        session_talk_add = QPushButton()
        session_talk_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add.png"))
        session_talk_add.setStyleSheet(self.btnStyle)
        session_talk_add.clicked.connect(lambda: self.add_entry(5))
        session_talk_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        temp_layout.addWidget(session_talk_add)
        content_layout.addLayout(temp_layout)
        self.session_talk_layout = QVBoxLayout()
        content_layout.addLayout(self.session_talk_layout)
        
        self.session_own_box = []
        self.session_own_editLines = []
        self.session_own_ewarnings = []
        self.session_own_rem_btn_list = []
        temp_layout = QHBoxLayout()
        session_own_other = QPushButton("\nBesitzt: ")
        temp_layout.addWidget(session_own_other)
        temp_layout.addStretch()
        session_own_add = QPushButton()
        session_own_add.setIcon(QIcon("/usr/share/x-live/flatman/icons/add.png"))
        session_own_add.setStyleSheet(self.btnStyle)
        session_own_add.clicked.connect(lambda: self.add_entry(6))
        session_own_add.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
        temp_layout.addWidget(session_own_add)
        content_layout.addLayout(temp_layout)
        self.session_own_layout = QVBoxLayout()
        content_layout.addLayout(self.session_own_layout)
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        footer_layout = QHBoxLayout()
        
        #close_btn = QPushButton("schließen")
        #close_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/close.png"))
        #close_btn.setStyleSheet(self.btnStyle)
        #close_btn.clicked.connect(self.close)

        apply_btn = QPushButton("übernehmen")
        apply_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/enter.png"))
        apply_btn.setStyleSheet(self.btnStyle)
        apply_btn.clicked.connect(self.prepare_new_permissions)
        
        reload_btn = QPushButton("neuladen")
        reload_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/reload.png"))
        reload_btn.setStyleSheet(self.btnStyle)
        reload_btn.clicked.connect(self.reload_permissions)

        reset_btn = QPushButton("zurücksetzen")
        reset_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/reset.png"))
        reset_btn.setStyleSheet(self.btnStyle)
        reset_btn.clicked.connect(self.reset_permissions)

        footer_layout.addStretch(3)
        #footer_layout.addWidget(close_btn)
        #footer_layout.addStretch(1)
        footer_layout.addWidget(apply_btn)
        footer_layout.addStretch(1)
        footer_layout.addWidget(reload_btn)
        footer_layout.addStretch(1)
        footer_layout.addWidget(reset_btn)
        footer_layout.addStretch(3)
        layout.addLayout(footer_layout)
        
        self.setLayout(layout)
        self.setWindowTitle(f"Berechtigungen für {self.app_name}")
        #self.resize(320, 500)
        self.refresh_perm()
        
    def check_all_buttons(self):
        self.check_perm_buttons("sockets", self.con_sockets_buttons, self.con_sockets, self.con_sockets_warnings)
        self.check_perm_buttons("shared", self.con_shared_buttons, self.con_shared, self.con_shared_warnings)
        self.check_perm_buttons("devices", self.con_devices_buttons, self.con_devices, self.con_devices_warnings)
        self.check_perm_buttons("features", self.con_features_buttons, self.con_features, self.con_features_warnings)
        self.check_perm_buttons("filesystems", self.con_filesystems_buttons, self.con_filesystems, self.con_filesystems_warnings)
        
        self.btn_rem_list = []
        
        # editline_list, warnings, rem_btn_list
        
        self.con_filesystems_editLines, self.con_filesystems_ewarnings, self.con_filesystems_rem_btn_list, self.con_filesystems_box = self.check_perm_lineEdits("filesystems", self.con_files_layout, self.con_filesystems_editLines, self.con_filesystems_ewarnings, self.con_filesystems_rem_btn_list)
        
        self.con_persistent_editLines, self.con_persistent_ewarnings, self.con_persistent_rem_btn_list, self.con_persistent_box = self.check_perm_lineEdits("persistent", self.con_persistent_layout, self.con_persistent_editLines, self.con_persistent_ewarnings, self.con_persistent_rem_btn_list)
        
        self.environment_editLines, self.environment_ewarnings, self.environment_rem_btn_list, self.environment_box = self.check_perm_lineEdits("Environment", self.environment_layout, self.environment_editLines, self.environment_ewarnings, self.environment_rem_btn_list)
        
        # editline_list, warnings, rem_btn_list, extra_editline_list, extra_warnings, extra_rem_btn_list
        
        self.system_talk_editLines, self.system_talk_ewarnings, self.system_talk_rem_btn_list, self.system_own_editLines, self.system_own_ewarnings, self.system_own_rem_btn_list, self.system_talk_box, self.system_own_box = self.check_perm_lineEdits("System Bus Policy", self.system_talk_layout, self.system_talk_editLines, self.system_talk_ewarnings, self.system_talk_rem_btn_list, self.system_own_layout, self.system_own_editLines, self.system_own_ewarnings, self.system_own_rem_btn_list)
        
        self.session_talk_editLines, self.session_talk_ewarnings, self.session_talk_rem_btn_list, self.session_own_editLines, self.session_own_ewarnings, self.session_own_rem_btn_list, self.session_talk_box, self.session_own_box = self.check_perm_lineEdits("Session Bus Policy", self.session_talk_layout, self.session_talk_editLines, self.session_talk_ewarnings, self.btn_rem_list, self.session_own_layout, self.session_own_editLines, self.session_own_ewarnings, self.session_own_rem_btn_list)

    # Aktualisiert Berechtigungen aus Flatpak-Metadaten und Overrides
    def refresh_perm(self):
        self.app_permissions,self.app_override = flatdata.get_permissions(self.app_id)
        self.check_all_buttons()
    
    # Setzt Icons und Warnungen je nach Zustand eines Buttons
    def handle_toggle(self, checked):
        button = self.sender()
        text = button.text()
        key = text.split(":")[0]
        #print(text)
        if button in self.con_sockets_buttons:
            for i, btn in enumerate(self.con_sockets_buttons):
                if btn.text() == text:
                    btn_number = i
                    if checked and self.app_permissions["sockets"][key] != True:
                        self.con_sockets_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_sockets_warnings[i].setToolTip("durch benutzer geändert")
                    elif checked and self.app_permissions["sockets"][key] == True:
                        self.con_sockets_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_sockets_warnings[i].setToolTip("")
                    elif self.app_permissions["sockets"][key] == True:
                        self.con_sockets_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_sockets_warnings[i].setToolTip("durch benutzer geändert")
                    elif self.app_permissions["sockets"][key] != True:
                        self.con_sockets_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_sockets_warnings[i].setToolTip("")
                        
        if button in self.con_shared_buttons:
            for i, btn in enumerate(self.con_shared_buttons):
                if btn.text() == text:
                    btn_number = i
                    if checked and self.app_permissions["shared"][key] != True:
                        self.con_shared_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_shared_warnings[i].setToolTip("durch benutzer geändert")
                    elif checked and self.app_permissions["shared"][key] == True:
                        self.con_shared_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_shared_warnings[i].setToolTip("")
                    elif self.app_permissions["shared"][key] == True:
                        self.con_shared_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_shared_warnings[i].setToolTip("durch benutzer geändert")
                    elif self.app_permissions["shared"][key] != True:
                        self.con_shared_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_shared_warnings[i].setToolTip("")
                        
        if button in self.con_devices_buttons:
            for i, btn in enumerate(self.con_devices_buttons):
                if btn.text() == text:
                    btn_number = i
                    if checked and self.app_permissions["devices"][key] != True:
                        self.con_devices_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_devices_warnings[i].setToolTip("durch benutzer geändert")
                    elif checked and self.app_permissions["devices"][key] == True:
                        self.con_devices_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_devices_warnings[i].setToolTip("")
                    elif self.app_permissions["devices"][key] == True:
                        self.con_devices_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_devices_warnings[i].setToolTip("durch benutzer geändert")
                    elif self.app_permissions["devices"][key] != True:
                        self.con_devices_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_devices_warnings[i].setToolTip("")
                        
        if button in self.con_features_buttons:
            for i, btn in enumerate(self.con_features_buttons):
                if btn.text() == text:
                    btn_number = i
                    if checked and self.app_permissions["features"][key] != True:
                        self.con_features_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_features_warnings[i].setToolTip("durch benutzer geändert")
                    elif checked and self.app_permissions["features"][key] == True:
                        self.con_features_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_features_warnings[i].setToolTip("")
                    elif self.app_permissions["features"][key] == True:
                        self.con_features_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_features_warnings[i].setToolTip("durch benutzer geändert")
                    elif self.app_permissions["features"][key] != True:
                        self.con_features_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_features_warnings[i].setToolTip("")
                        
        if button in self.con_filesystems_buttons:
            for i, btn in enumerate(self.con_filesystems_buttons):
                if btn.text() == text:
                    btn_number = i
                    if checked and self.app_permissions["filesystems"][key] != True:
                        self.con_filesystems_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_filesystems_warnings[i].setToolTip("durch benutzer geändert")
                    elif checked and self.app_permissions["filesystems"][key] == True:
                        self.con_filesystems_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_filesystems_warnings[i].setToolTip("")
                    elif self.app_permissions["filesystems"][key] == True:
                        self.con_filesystems_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        self.con_filesystems_warnings[i].setToolTip("durch benutzer geändert")
                    elif self.app_permissions["filesystems"][key] != True:
                        self.con_filesystems_warnings[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        self.con_filesystems_warnings[i].setToolTip("")
                        
        if checked:
            button.setIcon(QIcon("/usr/share/x-live/flatman/icons/on.png"))
                
        else:
            button.setIcon(QIcon("/usr/share/x-live/flatman/icons/off.png"))

    # Setzt Checkboxen (Buttons) anhand aktueller Berechtigungen + Overrides
    def check_perm_buttons(self, kat, buttons, names, warn):
        for i, btn in enumerate(buttons):
            name = names[i].split(":")[0]
            #print(name)
            
            value = self.app_permissions.get(kat, {}).get(name)
            if value is not None:
                #print("Existiert:", value)
                btn.setChecked(value)
            else:
                btn.setChecked(False)
            
            value = self.app_override.get(kat, {}).get(name)
            if value is not None:
                #print("Existiert:", value)
                btn.setChecked(value)
                warn[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            else:
                warn[i].setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))

    # Erstellt Zeilen für benutzerdefinierte Einträge (Pfad/Name/Wert) je nach Kategorie
    def check_perm_lineEdits(self, kat, layout, warnings, editline_list, rem_btn_list, extra_layout = None, extra_editline_list = None, extra_warnings = None, extra_rem_btn_list = None):
        
        box_list = []
        extra_box_list = []
        perms = self.app_permissions[kat]
        override = self.app_override[kat]
        #print("\n\nkat:",kat)
        #print("\n\nperms:",perms)
        #print("\n\noverride:",override)
        if kat in ["filesystems", "persistent"]:
            for key, value in perms.items():
                if key not in ["host", "host-os", "host-etc", "home"]:
                    if key not in self.app_override[kat]:
                        temp_layout = QHBoxLayout()
                        editline = QLineEdit(key)
                        editline.setFixedWidth(300)
                        editline.textChanged.connect(self.on_text_changed)
                        warn_btn = QPushButton()
                        warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        warn_btn.setToolTip("")
                        warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                        rem_btn = QPushButton()
                        rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                        rem_btn.setStyleSheet(self.btnStyle)
                        rem_btn.setToolTip("Eintrag entfernen")
                        rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                        rem_btn.clicked.connect(self.remove_entry)
                        
                        temp_layout.addWidget(editline)
                        temp_layout.addStretch()
                        temp_layout.addWidget(warn_btn)
                        temp_layout.addWidget(rem_btn)
                        layout.addLayout(temp_layout)
                        box_list.append(temp_layout)
                        rem_btn_list.append(rem_btn)
                        warnings.append(warn_btn)
                        editline_list.append(editline)
            for key, value in self.app_override[kat].items():
                if key not in ["host", "host-os", "host-etc", "home"]:
                    if key not in perms:
                        temp_layout = QHBoxLayout()
                        editline = QLineEdit(key)
                        editline.setFixedWidth(300)
                        editline.textChanged.connect(self.on_text_changed)
                        rem_btn = QPushButton()
                        rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                        rem_btn.setStyleSheet(self.btnStyle)
                        rem_btn.setToolTip("Eintrag entfernen")
                        rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                        rem_btn.clicked.connect(self.remove_entry)
                        warn_btn = QPushButton()
                        warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        warn_btn.setToolTip("durch benutzer geändert")
                        warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                        temp_layout.addWidget(editline)
                        temp_layout.addStretch()
                        temp_layout.addWidget(warn_btn)
                        temp_layout.addWidget(rem_btn)
                        layout.addLayout(temp_layout)
                        box_list.append(temp_layout)
                        warnings.append(warn_btn)
                        rem_btn_list.append(rem_btn)
                        editline_list.append(editline)
            return editline_list, warnings, rem_btn_list, box_list
            
        if kat in ["Environment"]:
            for key, value in perms.items():
                if key not in self.app_override[kat]:
                    temp_layout = QHBoxLayout()
                    editline = QLineEdit(key+"="+value)
                    editline.setFixedWidth(300)
                    editline.textChanged.connect(self.on_text_changed)
                    warn_btn = QPushButton()
                    warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                    warn_btn.setToolTip("durch benutzer geändert")
                    warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                    rem_btn = QPushButton()
                    rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                    rem_btn.setStyleSheet(self.btnStyle)
                    rem_btn.setToolTip("Eintrag entfernen")
                    rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                    rem_btn.clicked.connect(self.remove_entry)
                    temp_layout.addWidget(editline)
                    temp_layout.addStretch()
                    temp_layout.addWidget(warn_btn)
                    temp_layout.addWidget(rem_btn)
                    layout.addLayout(temp_layout)
                    box_list.append(temp_layout)
                    rem_btn_list.append(rem_btn)
                    warnings.append(warn_btn)
                    editline_list.append(editline)
            for key, value in self.app_override[kat].items():
                if key not in perms:
                    temp_layout = QHBoxLayout()
                    editline = QLineEdit(key+"="+value)
                    editline.setFixedWidth(300)
                    editline.textChanged.connect(self.on_text_changed)
                    warn_btn = QPushButton()
                    warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                    warn_btn.setToolTip("durch benutzer geändert")
                    warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                    rem_btn = QPushButton()
                    rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                    rem_btn.setStyleSheet(self.btnStyle)
                    rem_btn.setToolTip("Eintrag entfernen")
                    rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                    rem_btn.clicked.connect(self.remove_entry)
                    temp_layout.addWidget(editline)
                    temp_layout.addStretch()
                    temp_layout.addWidget(warn_btn)
                    temp_layout.addWidget(rem_btn)
                    layout.addLayout(temp_layout)
                    box_list.append(temp_layout)
                    rem_btn_list.append(rem_btn)
                    warnings.append(warn_btn)
                    editline_list.append(editline)
            return editline_list, warnings, rem_btn_list, box_list
                        
        if kat in ["System Bus Policy","Session Bus Policy"]:
            for key, value in perms.items():
                if key not in self.app_override[kat]:
                    if value == "talk":
                        temp_layout = QHBoxLayout()
                        
                        editline = QLineEdit(key)
                        editline.setFixedWidth(300)
                        editline.textChanged.connect(self.on_text_changed)
                        warn_btn = QPushButton()
                        warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        warn_btn.setToolTip("")
                        warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                        rem_btn = QPushButton()
                        rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                        rem_btn.setStyleSheet(self.btnStyle)
                        rem_btn.setToolTip("Eintrag entfernen")
                        rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                        rem_btn.clicked.connect(self.remove_entry)
                        temp_layout.addWidget(editline)
                        temp_layout.addStretch()
                        temp_layout.addWidget(warn_btn)
                        temp_layout.addWidget(rem_btn)
                        layout.addLayout(temp_layout)
                        box_list.append(temp_layout)
                        rem_btn_list.append(rem_btn)
                        warnings.append(warn_btn)
                        editline_list.append(editline)
                        
                    elif value == "own":
                        temp_layout = QHBoxLayout()
                        
                        editline = QLineEdit(key)
                        editline.setFixedWidth(300)
                        editline.textChanged.connect(self.on_text_changed)
                        warn_btn = QPushButton()
                        warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/nowarn.png"))
                        warn_btn.setToolTip("")
                        warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                        rem_btn = QPushButton()
                        rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                        rem_btn.setStyleSheet(self.btnStyle)
                        rem_btn.setToolTip("Eintrag entfernen")
                        rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                        rem_btn.clicked.connect(self.remove_entry)
                        temp_layout.addWidget(editline)
                        temp_layout.addStretch()
                        temp_layout.addWidget(warn_btn)
                        temp_layout.addWidget(rem_btn)
                        
                        
                        extra_layout.addLayout(temp_layout)
                        
                        extra_box_list.append(temp_layout)
                        extra_warnings.append(warn_btn)
                        extra_editline_list.append(editline)
                        extra_rem_btn_list.append(rem_btn)
                        
            for key, value in self.app_override[kat].items():
                if key not in perms or value != "none":
                    if value == "talk":
                        temp_layout = QHBoxLayout()
                        
                        editline = QLineEdit(key)
                        editline.setFixedWidth(300)
                        editline.textChanged.connect(self.on_text_changed)
                        warn_btn = QPushButton()
                        warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        warn_btn.setToolTip("durch benutzer geändert")
                        warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                        rem_btn = QPushButton()
                        rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                        rem_btn.setStyleSheet(self.btnStyle)
                        rem_btn.setToolTip("Eintrag entfernen")
                        rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                        rem_btn.clicked.connect(self.remove_entry)
                        temp_layout.addWidget(editline)
                        temp_layout.addStretch()
                        temp_layout.addWidget(warn_btn)
                        temp_layout.addWidget(rem_btn)
                        layout.addLayout(temp_layout)
                        box_list.append(temp_layout)
                        rem_btn_list.append(rem_btn)
                        warnings.append(warn_btn)
                        editline_list.append(editline)
                        
                    elif value == "own":
                        temp_layout = QHBoxLayout()
                        
                        editline = QLineEdit(key)
                        editline.setFixedWidth(300)
                        editline.textChanged.connect(self.on_text_changed)
                        warn_btn = QPushButton()
                        warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
                        warn_btn.setToolTip("durch benutzer geändert")
                        warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
                        rem_btn = QPushButton()
                        rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
                        rem_btn.setStyleSheet(self.btnStyle)
                        rem_btn.setToolTip("Eintrag entfernen")
                        rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
                        rem_btn.clicked.connect(self.remove_entry)
                        temp_layout.addWidget(editline)
                        temp_layout.addStretch()
                        
                        temp_layout.addWidget(warn_btn)
                        temp_layout.addWidget(rem_btn)
                        
                        extra_layout.addLayout(temp_layout)
                        extra_box_list.append(temp_layout)
                        extra_warnings.append(warn_btn)
                        extra_editline_list.append(editline)
                        extra_rem_btn_list.append(rem_btn)
                        
            return editline_list, warnings, rem_btn_list, extra_editline_list, extra_warnings, extra_rem_btn_list, box_list, extra_box_list

    
    
    # Entfernt einen manuell hinzugefügten Eintrag (Pfad/Bus-Name/etc.)
    def remove_entry(self):
        btn = self.sender()
        
        rem_btn_list = [self.con_filesystems_rem_btn_list,self.con_persistent_rem_btn_list,self.environment_rem_btn_list,self.system_talk_rem_btn_list,self.system_own_rem_btn_list,self.session_talk_rem_btn_list,self.session_own_rem_btn_list]
        le_list = [self.con_filesystems_editLines,self.con_persistent_editLines,self.environment_editLines,self.system_talk_editLines,self.system_own_editLines,self.session_talk_editLines,self.session_own_editLines]
        b1_list = [
self.con_filesystems_rem_btn_list,self.con_persistent_rem_btn_list,self.environment_rem_btn_list,self.system_talk_rem_btn_list,self.system_own_rem_btn_list,self.session_talk_rem_btn_list,self.session_own_rem_btn_list]
        b2_list = [ self.con_filesystems_ewarnings,self.con_persistent_ewarnings,self.environment_ewarnings,self.system_talk_ewarnings,self.system_own_ewarnings,self.session_talk_ewarnings,self.session_own_ewarnings]
        hbox_list = [ self.con_filesystems_box,self.con_persistent_box,self.environment_box,self.system_talk_box,self.system_own_box,self.session_talk_box,self.session_own_box]
        
        for kat,btn_list in enumerate(rem_btn_list):
            if btn in btn_list:
                index = btn_list.index(btn)
                #print(f"button gefunden: Filesystem - {index}")
                
                le = le_list[kat].pop(index)
                b1 = b1_list[kat].pop(index)
                b2 = b2_list[kat].pop(index)
                hbox = hbox_list[kat].pop(index)
                
                for widget in (le, b1, b2):
                    hbox.removeWidget(widget)
                    widget.deleteLater()
                    
                self.con_files_layout.removeItem(hbox)
                return
            
        print("button nicht gefunden")
    
    
    
    
    
    
    
    
    
    
    # Fügt einen neuen leeren Eintrag für die jeweilige Kategorie hinzu
    def add_entry(self, btn):
        if btn == 0:
            #print(f"button gefunden: Filesystem")

            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.con_files_layout.addLayout(temp_layout)
            self.con_filesystems_box.append(temp_layout)
            self.con_filesystems_rem_btn_list.append(rem_btn)
            self.con_filesystems_ewarnings.append(warn_btn)
            self.con_filesystems_editLines.append(editline)
            
            return
            
        if btn == 1:
            #print(f"button gefunden: Persistent")
            
            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.con_persistent_layout.addLayout(temp_layout)
            self.con_persistent_box.append(temp_layout)
            self.con_persistent_rem_btn_list.append(rem_btn)
            self.con_persistent_ewarnings.append(warn_btn)
            self.con_persistent_editLines.append(editline)
            
            return
            
        if btn == 2:
            #print(f"button gefunden: environment")
            
            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.environment_layout.addLayout(temp_layout)
            self.environment_box.append(temp_layout)
            self.environment_rem_btn_list.append(rem_btn)
            self.environment_ewarnings.append(warn_btn)
            self.environment_editLines.append(editline)
            
            return
        if btn == 3:
            #print(f"button gefunden: system_talk")
            
            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.system_talk_layout.addLayout(temp_layout)
            self.system_talk_box.append(temp_layout)
            self.system_talk_rem_btn_list.append(rem_btn)
            self.system_talk_ewarnings.append(warn_btn)
            self.system_talk_editLines.append(editline)
            
            return
        if btn == 4:
            #print(f"button gefunden: system_own")
            
            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.system_own_layout.addLayout(temp_layout)
            self.system_own_box.append(temp_layout)
            self.system_own_rem_btn_list.append(rem_btn)
            self.system_own_ewarnings.append(warn_btn)
            self.system_own_editLines.append(editline)
            return
        if btn == 5:
            #print(f"button gefunden: session_talk")
            
            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.session_talk_layout.addLayout(temp_layout)
            self.session_talk_box.append(temp_layout)
            self.session_talk_rem_btn_list.append(rem_btn)
            self.session_talk_ewarnings.append(warn_btn)
            self.session_talk_editLines.append(editline)
            return
        if btn == 6:
            #print(f"button gefunden: session_own")
            
            temp_layout = QHBoxLayout()
            editline = QLineEdit()
            editline.setFixedWidth(300)
            editline.textChanged.connect(self.on_text_changed)

            warn_btn = QPushButton()
            warn_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/warn.png"))
            warn_btn.setToolTip("durch benutzer geändert")
            warn_btn.setIconSize(QSize(int(32*self.faktor),int(32*self.faktor)))
            rem_btn = QPushButton()
            rem_btn.setIcon(QIcon("/usr/share/x-live/flatman/icons/rem.png"))
            rem_btn.setStyleSheet(self.btnStyle)
            rem_btn.setToolTip("Eintrag entfernen")
            rem_btn.setIconSize(QSize(int(24*self.faktor),int(24*self.faktor)))
            rem_btn.clicked.connect(self.remove_entry)
            temp_layout.addWidget(editline)
            temp_layout.addStretch()
            temp_layout.addWidget(warn_btn)
            temp_layout.addWidget(rem_btn)
            
            self.session_own_layout.addLayout(temp_layout)
            self.session_own_box.append(temp_layout)
            self.session_own_rem_btn_list.append(rem_btn)
            self.session_own_ewarnings.append(warn_btn)
            self.session_own_editLines.append(editline)
            return
            
        print("button nicht gefunden")
            
            
            
             
            
            
            
           
            

    # Reaktion auf Textänderungen in den Eingabefeldern (z. B. Warnsymbol setzen)
    def on_text_changed(self, new_text):
        
        btn = self.sender()
        
        if btn in self.con_filesystems_editLines:
            index = self.con_filesystems_editLines.index(btn)
            #print(f"button gefunden: Filesystem - {index}")
            
        if btn in self.con_persistent_editLines:
            index = self.con_persistent_editLines.index(btn)
            #print(f"button gefunden: Persistent - {index}")
            
            
            
            
        if btn in self.environment_editLines:
            index = self.environment_editLines.index(btn)
            #print(f"button gefunden: environment - {index}")
            
            
            
        if btn in self.system_talk_editLines:
            index = self.system_talk_editLines.index(btn)
            #print(f"button gefunden: system_talk - {index}")
            
        if btn in self.system_own_editLines:
            index = self.system_own_editLines.index(btn)
            #print(f"button gefunden: system_own - {index}")
            
            
            
        if btn in self.session_talk_editLines:
            index = self.session_talk_editLines.index(btn)
            #print(f"button gefunden: session_talk - {index}")
            
            
            
        if btn in self.session_own_editLines:
            index = self.session_own_editLines.index(btn)
            #print(f"button gefunden: session_own - {index}")
        
        print("Neuer Text:", new_text)
        
    def prepare_new_permissions(self):
        self.new_permission = flatdata.get_clean_permissions()
        self.new_override = flatdata.get_clean_override()
        
        btns = {"shared":self.con_shared_buttons,"sockets":self.con_sockets_buttons,"devices":self.con_devices_buttons,"features":self.con_features_buttons,"filesystems":self.con_filesystems_buttons}
        for kat in btns:
            for btn in btns[kat]:
                flag = btn.text().split(":")[0]
                self.new_permission[kat][flag] = btn.isChecked()
                if self.new_permission[kat][flag] != self.app_permissions[kat][flag]:
                    self.new_override[kat][flag] = self.new_permission[kat][flag]
        files = {"filesystems" : self.con_filesystems_editLines,"persistent" : self.con_persistent_editLines  }  
        
        for kat in files:
            for le in files[kat]:
                flag = le.text()
                self.new_permission[kat][flag] = True
                if flag not in self.app_permissions[kat]:
                    self.new_override[kat][flag] = True
                    
        for kat in files:
            for flag in self.app_permissions[kat]:
                if flag not in self.new_permission[kat]:
                    self.new_override[kat][flag] = False
                    
                    
        
        for le in self.environment_editLines:
            key = le.text().split("=")[0]
            flag = le.text().split("=")[1]
            self.new_permission["Environment"][key] = flag
            if key not in self.app_permissions["Environment"]:
                self.new_override["Environment"][key] = flag
                
        
        kat = "Environment"
        for flag in self.app_permissions[kat]:
            if flag not in self.new_permission[kat]:
                self.new_override[kat][flag] = ""
                
                
        
        
        buses = {"System Bus Policy:talk" : self.system_talk_editLines, "System Bus Policy:own" : self.system_own_editLines,"Session Bus Policy:talk" : self.session_talk_editLines, "Session Bus Policy:own" : self.session_own_editLines}
        
        for kat in buses:
            for le in buses[kat]:
                key = kat.split(":")[0]
                flag = le.text()
                value = kat.split(":")[1]
                self.new_permission[key][flag] = value
                if flag not in self.app_permissions[key]:
                    self.new_override[key][flag] = value
                elif self.app_permissions[key][flag] != self.new_permission[key][flag]:
                    self.new_override[key][flag] = value
                    
            
        for kat in ["System Bus Policy","Session Bus Policy"]:
            for flag in self.app_permissions[kat]:
                if flag not in self.new_permission[kat]:
                    self.new_override[kat][flag] = "none"

        
        
        
        #print(f"\n\nAlte Berechtigungen:\n {self.app_permissions}\n")
        #print(f"\n\nNeue Berechtigungen:\n {self.new_permission}\n")
        #print(f"\n\nAlte override:\n {self.app_override}\n")
        #print(f"\n\nNeue override:\n {self.new_override}\n")
        
        gemeinsam = 0
        nicht_vorhanden = 0
        old_gemeinsam = 0
        old_nicht_vorhanden = 0
        for kat in self.app_override:
            
            for flag in self.app_override[kat]:
                if flag not in self.new_override[kat]:
                    nicht_vorhanden += 1
                elif self.new_override[kat][flag] != self.app_override[kat][flag]:
                    nicht_vorhanden += 1
                else:
                    gemeinsam += 1
            #print("[",kat,"]","gleich:",gemeinsam-old_gemeinsam," - anders:",nicht_vorhanden-old_nicht_vorhanden) 
            old_gemeinsam = gemeinsam
            old_nicht_vorhanden = nicht_vorhanden
        for kat in self.new_override:
            
            for flag in self.new_override[kat]:
                if flag not in self.app_override[kat]:
                    nicht_vorhanden += 1
                elif self.new_override[kat][flag] != self.app_override[kat][flag]:
                    nicht_vorhanden += 1
                else:
                    gemeinsam += 1
            #print("[",kat,"]","gleich:",gemeinsam-old_gemeinsam," - anders:",nicht_vorhanden-old_nicht_vorhanden) 
            old_gemeinsam = gemeinsam
            old_nicht_vorhanden = nicht_vorhanden
        #print("[gesamt]","gleich:",gemeinsam," - anders:",nicht_vorhanden) 
        
        
        override_commands = self.generate_flatpak_override_args(self.new_override)
        #print(override_commands)
        
        
        failed_cmds = self.apply_flatpak_overrides(self.app_id, override_commands)
        print ("overrides erfolgreich: ",failed_cmds)
        
        
        self.test_permissions,self.test_override = flatdata.get_permissions(self.app_id)
        
        
        
        gemeinsam = 0
        nicht_vorhanden = 0
        old_gemeinsam = 0
        old_nicht_vorhanden = 0
        
        for kat in self.test_override:
            
            for flag in self.test_override[kat]:
                if flag not in self.new_override[kat]:
                    nicht_vorhanden += 1
                elif self.new_override[kat][flag] != self.test_override[kat][flag]:
                    nicht_vorhanden += 1
                else:
                    gemeinsam += 1
            #print("[",kat,"]","gleich:",gemeinsam-old_gemeinsam," - anders:",nicht_vorhanden-old_nicht_vorhanden) 
            old_gemeinsam = gemeinsam
            old_nicht_vorhanden = nicht_vorhanden
        for kat in self.new_override:
            
            for flag in self.new_override[kat]:
                if flag not in self.test_override[kat]:
                    nicht_vorhanden += 1
                elif self.new_override[kat][flag] != self.test_override[kat][flag]:
                    nicht_vorhanden += 1
                else:
                    gemeinsam += 1
            #print("[",kat,"]","gleich:",gemeinsam-old_gemeinsam," - anders:",nicht_vorhanden-old_nicht_vorhanden) 
            old_gemeinsam = gemeinsam
            old_nicht_vorhanden = nicht_vorhanden
        print("[gesamt]","gleich:",gemeinsam," - anders:",nicht_vorhanden) 
        
        
        
        
    def generate_flatpak_override_args(self,override):
        flag_map = {
            "sockets": ("--socket", "--nosocket"),
            "shared": ("--share", "--unshare"),
            "devices": ("--device", "--nodevice"),
            "features": ("--allow", "--disallow"),
            "filesystems": ("--filesystem", "--nofilesystem"),
            "persistent": ("--persist", None),
            "Environment": ("--env", "--unset-env"),
            "Session Bus Policy": {
                "own": "--own-name",
                "talk": "--talk-name",
                "none": "--no-talk-name"
            },
            "System Bus Policy": {
                "own": "--system-own-name",
                "talk": "--system-talk-name",
                "none": "--system-no-talk-name"
            },
        }

        args = []

        for category, items in override.items():
            if category in ("sockets", "shared", "devices", "features", "filesystems", "persistent"):
                add_opt, remove_opt = flag_map[category]
                for key, value in items.items():
                    if value:
                        args.append(f"{add_opt}={key}")
                    else:
                        if remove_opt:
                            args.append(f"{remove_opt}={key}")

            elif category == "Environment":
                add_opt, remove_opt = flag_map[category]
                for key, value in items.items():
                    if value != "":
                        args.append(f"{add_opt}={key}={value}")
                    else:
                        args.append(f"{remove_opt}={key}")

            elif category in ("Session Bus Policy", "System Bus Policy"):
                submap = flag_map[category]
                for key, value in items.items():
                    opt = submap.get(value)
                    if opt:
                        args.append(f"{opt}={key}")

        return args

    def apply_flatpak_overrides(self,app_id, args, user=True):
        base_cmd = ["flatpak", "override"]
        if user:
            base_cmd.append("--user")

        # Reset zuerst
        try:
            subprocess.run(base_cmd + ["--reset", app_id], check=True)
            print(f"Override-Reset für {app_id} erfolgreich.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Reset für {app_id}: {e}")
            return False

        success = []
        failed = []

        for arg in args:
            try:
                subprocess.run(base_cmd + [arg, app_id], check=True)
                success.append(arg)
            except subprocess.CalledProcessError as e:
                print(f"Fehler bei Override {arg}: {e}")
                failed.append(arg)

        print(f"✔ Erfolgreich angewendet: {success}")
        print(f"✖ Fehlerhafte Overrides: {failed}")

        return len(failed) == 0


    def reset_permissions(self, user=True):
        app_id = self.app_id
        base_cmd = ["flatpak", "override"]
        
        try:
            subprocess.run(base_cmd + ["--reset","--user", app_id], check=True)
            print(f"Override-Reset für {app_id} erfolgreich.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Reset für {app_id}: {e}")
            return False
            
        self.reload_permissions()

    def reload_permissions(self):
        btn_list =[self.con_filesystems_rem_btn_list,self.con_persistent_rem_btn_list,self.environment_rem_btn_list,self.system_talk_rem_btn_list,self.system_own_rem_btn_list,self.session_talk_rem_btn_list,self.session_own_rem_btn_list]
        for kat in btn_list:
            while len(kat) >= 1:
                kat[0].click()
        
        self.refresh_perm()
        print("Reload durchgeführt !!")

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) != 2:
        print("⚠️  Nutzung: python p5.py <App-ID>")
    else:
        window = FlatPerm(sys.argv[1])
        window.show()
        sys.exit(app.exec_())
    
    