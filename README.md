# x-live-flatman
Software Manager für Flatpak Anwendungen / Software Manager for Flatpak applications


!! installation unter debian


1. Abhängigkeiten installieren / Install dependencies

sudo apt update
sudo apt install curl jq gawk

2. Script herunterladen und installieren / Download and install the script

curl -L https://raw.githubusercontent.com/soimort/translate-shell/master/translate.sh -o translate.sh
chmod +x translate.sh
sudo mv translate.sh /usr/local/bin/trans

3. flatman.deb herunterladen und installieren mit / Download and install flatman.deb with

sudo apt install ./flatman.deb


-----

![screenshot](flatman.png)

