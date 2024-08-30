import sys 
import os
import subprocess
import re
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QPushButton, QSlider, 
                             QVBoxLayout, QWidget, QMessageBox)

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):


        faktor = app.desktop().height()/720
        self.faktor = app.desktop().height()/720
        breite = int(250 * faktor)
        hoehe = int(60 * faktor)
        bts=int(16 * faktor)
        sts=int(16 * faktor)
        pos_x = int((app.desktop().width()-breite)/2)
        pos_y = int((app.desktop().height()-hoehe)/2)
        self.background_color()
      
        #  StyleSheet 
        
        self.ssbtn1=str("""
            QWidget {
            background-color: #130343;
            }
            QLabel {
            font-size: """ + str(sts) + """px; 
            text-align: right;      
            border-radius: 10px;
            background-color: """ + self.color_background  + """;
            border: 2px solid """ + self.color_background  + """;
            padding-top: 2px;
            padding-left: 5px;
            padding-right: 5px;
            padding-bottom: 2px;
            color: """ + self.color_font + """;
            }
            """)
            

        # Erstelle ein Layout für das Hauptfenster
        layout = QVBoxLayout()
        self.label = QLabel("bitte warten\nDaten werden aktuallisiert ...", self)
        self.label.setStyleSheet(self.ssbtn1)
        layout.addWidget(self.label)

        # Setze das Layout für das Hauptfenster
        self.setLayout(layout)

        self.setGeometry(pos_x, pos_y,breite,hoehe)
        self.setWindowIcon(QIcon.fromTheme('settings'))  # Setze das systemweite Theme-Icon als Fenstericon
        self.setWindowTitle("X-Mint Einstellungstool")
        #self.setMinimumSize(breite, hoehe)  # Festlegen der Größe auf 600x400 Pixel
        #self.setFixedWidth(breite)
        self.setStyleSheet("background: rgba(80,80, 80, 00);")  # Hintergrundfarbe festlegen

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)  # Entfernt die Fensterdekoration
        self.adjustSze()
        self.show()

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
                self.color_background = self.extract_color_from_css(css_file_path, ' background-color')
                self.color_font = self.extract_color_from_css(css_file_path, ' color')
                
                #self.setStyleSheet(f"background: {bcolor};color: {color}")
            else:
                print(f"CSS file not found: {css_file_path}")
        else:
            print("Unable to determine the current theme.")
            
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    sys.exit(app.exec_())
