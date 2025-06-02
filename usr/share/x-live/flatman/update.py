import sys 
import os
import subprocess
import re
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QPushButton, QSlider, 
                             QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, QProcess

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        config_dir = os.path.expanduser("~/.config/x-live/flatman/")
        data_file = config_dir+"program_data.json"
        bak_file = "/usr/share/x-live/flatman/program_data.json"
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        if not os.path.exists(data_file):
            cmd = f"cp {bak_file} {data_file}"
            os.system(cmd)
        


        self.initUI()

    def initUI(self):

        self.process=None

        faktor = app.desktop().height()/720
        self.faktor = app.desktop().height()/720
        breite = int(650 * faktor)
        hoehe = int(60 * faktor)
        bts=int(16 * faktor)
        sts=int(16 * faktor)
        pos_x = int((app.desktop().width()-breite)/2)
        pos_y = int((app.desktop().height()-hoehe)/2)
        self.background_color()
        #print(breite," ",hoehe," ",pos_x," ",pos_y)
      
        #  StyleSheet 
        
        self.ssbtn1=str("""
            QWidget {
            background-color: #130343;
            }
            QPushButton {
            font-size: """ + str(sts) + """px; 
            text-align: center;      
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
        self.label = QPushButton("BITTE WARTEN !!\nDaten werden aktuallisiert ...", self)
        self.label.setStyleSheet(self.ssbtn1)
        layout.addWidget(self.label)

        # Setze das Layout für das Hauptfenster
        self.setLayout(layout)

        self.setGeometry(pos_x, pos_y,breite,hoehe)
        self.setWindowIcon(QIcon.fromTheme('settings'))  # Setze das systemweite Theme-Icon als Fenstericon
        self.setWindowTitle("collect Flatpak-data")
        self.setMinimumSize(breite, hoehe)  # Festlegen der Größe auf 600x400 Pixel
        self.setMaximumWidth(int(self.faktor*720/3*2))
        self.setStyleSheet("background: rgba(80,80, 80, 00);")  # Hintergrundfarbe festlegen

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)  # Entfernt die Fensterdekoration
        self.adjustSize()
        self.show()
        self.start_data_refresh()





    def start_data_refresh(self):
        if not self.process:
            self.label.setText("bitte warten\nDaten werden aktuallisiert ...")
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.process_finished)
            
            # Prepare the command
            command = f'python3 /usr/share/x-live/flatman/update_data.py'
            self.process.start('sh', ['-c', command])
            #self.process.start(command)


    def read_output(self):
        if self.process:
            #output = self.process.readAllStandardOutput().data()
            output = str(self.process.readAll().data().decode())
            output = str(output).replace('\n', '')
            self.label.setText(f"BITTE WARTEN !!\n{output}")

    def process_finished(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.label.setText("\nInstallation completed successfully.")
            #QMessageBox.information(self, "Success", "Package installed successfully!")
            sys.exit()
        else:
            self.label.setText("\nInstallation failed.")
            #QMessageBox.critical(self, "Error", "Failed to install package.")
            sys.exit()
      







    # farbprofil ermitteln
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
                self.color_background="gray"
                self.color_font = "white"
        else:
            print("Unable to determine the current theme.")
            self.color_background="gray"
            self.color_font = "white"
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    sys.exit(app.exec_())
