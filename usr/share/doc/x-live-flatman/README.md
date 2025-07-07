x-live-flatman for Debian
==========================

x-live-flatman is a simple GUI-based Flatpak installer and permission manager,
inspired by Flatseal. It allows users to search, install, and manage Flatpak
applications graphically on Debian-based systems.

This tool is especially useful for users who want a lightweight, native
alternative to Flatpak command-line tools and Flatseal.

Features:
---------

 - Search and install Flatpak apps from Flathub
 - View detailed metadata before installation
 - Manage permissions of installed Flatpak apps (similar to Flatseal)
 - Clean and intuitive PyQt5-based interface

Dependencies:
-------------

The following packages are required and are declared in the control file:

 - python3
 - python3-requests
 - python3-bs4
 - python3-pyqt5
 - python3-pil
 - wget
 - appstream
 - gawk

These should be installed automatically when using a proper `.deb` package.

Usage:
------

To run the application, execute:

    x-live-flatman

Alternatively, launch it from your applications menu under
"Utilities" or "X-Live Apps".

Project Source:
---------------

GitHub repository:
https://github.com/VerEnderT/x-live-flatman

Bug reports, feature requests, and contributions are welcome!

Author:
-------

Frank Maczollek aka VerEnderT  
<chaosz932@gmail.com>

License:
--------

This program is licensed under the GNU General Public License version 3 or later.  
See `/usr/share/doc/x-live-flatman/copyright` for full licensing details.
