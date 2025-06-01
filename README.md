# x-live-flatman
Software Manager für Flatpak Anwendungen / Software Manager for Flatpak applications


!! installation unter debian


1. Abhängigkeiten installieren

sudo apt update
sudo apt install curl jq gawk

2. Script herunterladen und installieren

curl -L https://raw.githubusercontent.com/soimort/translate-shell/master/translate.sh -o translate.sh
chmod +x translate.sh
sudo mv translate.sh /usr/local/bin/trans

3. Flatman installieren
lade dir flatman.deb herunter und installiere es mit

sudo apt install ./flatman.deb
