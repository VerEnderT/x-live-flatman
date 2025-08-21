#!/usr/bin/python3
import os
import json
import subprocess
import themecolor
from datetime import datetime
from PyQt5.QtCore import QEventLoop, QUrl, QTimer, Qt
from PyQt5.QtGui import QPixmap, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class FlatpakInfoFetcher(QWidget):
    def __init__(self, config_dir=None, icons_path=None, timeout_ms=10000, show_progress=False):
        super().__init__()

        bcolor,color  = themecolor.theme_color()
        if not bcolor and color:
            print("default color")
            bcolor = "#0d0d0d"
            color = "#eeeeec"
        self.setStyleSheet(f"background: {bcolor};color: {color}")
        self.setWindowIcon(QIcon("/usr/share/x-live/flatman/icons/reload.png"))

        # Netzwerkmanager
        self.manager = QNetworkAccessManager()
        self.timeout_ms = timeout_ms

        # Pfade
        self.config_dir = os.path.expanduser(config_dir or "~/.config/x-live/flatman/")
        self.icons_path = os.path.expanduser(icons_path or "~/.config/x-live/flatman/icons/")
        self.data_file = os.path.join(self.config_dir, "program_data.json")
        self.bak_file = "/usr/share/x-live/flatman/program_data.json"
        self.trans_file = os.path.join(self.config_dir, "trans")

        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.icons_path, exist_ok=True)

        # Optionales Fortschritts-Widget
        self.show_progress = show_progress
        if self.show_progress:
            self.setWindowTitle("Flatpak-Daten werden geladen...")
            self.resize(400, 100)
            layout = QVBoxLayout()
            self.label = QLabel("Starte...", self)
            self.close_btn = QPushButton("beenden",self)
            self.close_btn.hide()
            self.close_btn.clicked.connect(self.close)
            self.progress = QProgressBar(self)
            self.progress.setRange(0, 100)
            layout.addWidget(self.label)
            layout.addWidget(self.progress)
            layout.addWidget(self.close_btn)
            self.setLayout(layout)

    # ---------- Netzwerk-Helfer ----------
    def _get_json_from_url(self, url):
        loop = QEventLoop()
        reply = self.manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(loop.quit)
        QTimer.singleShot(self.timeout_ms, loop.quit)
        loop.exec_()

        if reply.error():
            print(f"[Fehler] {url}: {reply.errorString()}")
            reply.deleteLater()
            return None

        try:
            data = json.loads(reply.readAll().data().decode("utf-8"))
        except json.JSONDecodeError:
            reply.deleteLater()
            return None

        reply.deleteLater()
        return data

    def _download_file(self, url, save_path):
        loop = QEventLoop()
        reply = self.manager.get(QNetworkRequest(QUrl(url)))
        reply.finished.connect(loop.quit)
        QTimer.singleShot(self.timeout_ms, loop.quit)
        loop.exec_()

        if reply.error():
            print(f"[Fehler] Download {url}: {reply.errorString()}")
            reply.deleteLater()
            return False

        with open(save_path, "wb") as f:
            f.write(reply.readAll().data())
        reply.deleteLater()
        return True

    # ---------- Daten-Handling ----------
    def load_saved_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        elif os.path.exists(self.bak_file):
            with open(self.bak_file, "r") as f:
                return json.load(f)
        return {}

    def save_data(self, program_data):
        output_dir = os.path.dirname(self.data_file)
        os.makedirs(output_dir, exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(program_data, f, indent=2)

    def get_flatpak_info(self, app_id):
        url = f"https://flathub.org/api/v2/appstream/{app_id}"
        data = self._get_json_from_url(url)
        if not data:
            return "", "", ["none"]

        description = data.get("description", [])
        if description != "":
            description = self.translate_text(description)
        print(description)
        screenshots = data.get("screenshots", [])
        app_categories = data.get("categories", [])
        icon_url = data.get("icon", [])

        if icon_url:
            self.download_icon(app_id, icon_url)

        screenshot_url = ""
        if screenshots:
            screenshot = screenshots[0]
            size = screenshot.get("sizes", [])[0]
            screenshot_url = size.get("src")
        return screenshot_url, description , app_categories

    def download_icon(self, app_id, url):
        icon_path = os.path.join(self.icons_path, f"{app_id}.png")
        if not os.path.exists(icon_path):
            print(f"Download Icon {app_id} -- {datetime.now().time()}")
            self._download_file(url, icon_path)
        return icon_path

    def check_category(self, app_categories):
        categories = [
            "Game", "Office", "Graphics", "AudioVideo", "Utility",
            "Network", "Education", "Science", "Development", "System"
        ]
        for wort1 in categories:
            for wort2 in app_categories:
                if wort1 == wort2:
                    return wort1
        return "Other"

    def get_all_apps(self):
        try:
            result = subprocess.run(
                ["flatpak", "remote-ls", "--app", "--columns=name,application,version,installed-size,description"],
                capture_output=True,
                text=True,
                check=True
            )
            app_names, app_ids, app_versions, app_sizes, app_desc_shorts = [], [], [], [], []
            for line in result.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) > 1:
                    app_names.append(parts[0])
                    app_ids.append(parts[1])
                    app_versions.append(parts[2])
                    app_sizes.append(parts[3])
                app_desc_shorts.append(parts[4] if len(parts) > 4 else " ")
            return app_ids, app_names, app_versions, app_sizes, app_desc_shorts
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[Fehler] Flatpak: {e}")
            return None

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

    # ---------- Komplett-Aktualisierung ----------
    def update_all_apps(self):
        program_data = self.load_saved_data()
        all_apps = self.get_all_apps()
        if not all_apps:
            return

        app_ids, app_names, app_versions, app_sizes, app_desc_shorts = all_apps
        total = len(app_ids)

        for i, app_id in enumerate(app_ids):
            if self.show_progress:
                self.progress.setValue(int((i + 1) / total * 100))
                self.label.setText(f"{i+1}/{total} – {app_names[i]}")
                QApplication.processEvents()

            if app_names[i] not in program_data:
                thumb, desc, cats = self.get_flatpak_info(app_id)
                category = self.check_category(cats)
                program_data[app_names[i]] = {
                    "category": category,
                    "id": app_id,
                    "description": desc,
                    "thumbnail": thumb,
                    "version": app_versions[i],
                    "size": app_sizes[i],
                    "short-desc": self.translate_text(app_desc_shorts[i])
                }

        self.save_data(program_data)
        self.close_btn.show()
        self.label.setText("Flatpak-Daten wurden aktuallisiert !!")
        self.progress.hide()

# ---------- Teststart ----------
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    fetcher = FlatpakInfoFetcher(show_progress=True)
    fetcher.show()
    fetcher.update_all_apps()
    sys.exit(app.exec_())
