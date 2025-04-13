#!/usr/bin/sh

minfo () {
  echo -e "[\e[34m*\e[0m] $1"
}
mdone () {
  echo -e "[\e[32mV\e[0m] $1"
}
merror () {
  echo -e "[\e[31mX\e[0m] $1"
}

minfo "Installing Python dependencies"
pip install PyQt5 pyyaml --break-system-packages
if [[ "$?" != "0" ]]; then
  merror "Error while installing Python dependencies"
  merror "Try to install these manually with command \e[1mpip install PyQt5 PyYaml\e[0m"
  merror "If it didn't help, try to download and modidy this script."
  exit 1
fi
minfo "Changed directory to /tmp"
cd /tmp
minfo "Cloning NXMV repository"
git clone https://github.com/vladosnx/nxvm
if [[ "$?" != "0" ]]; then
  merror "Error while cloning NXVM repository"
  exit 1
fi
mdone "Cloned NXVM repo without errors"
cd nxvm
cp nxvm.py /usr/bin/nxvm.py
cp nxvm /usr/bin/nxvm
chmod +x /usr/bin/nxvm.py
chmod +x /usr/bin/nxvm
mdone "Copied nxvm binary to /usr/bin and made it executable"
cp nxvm.desktop /usr/share/applications/nxvm.desktop
mdone "Copied NXVM.desktop to /usr/share/applications"
mdone "NXVM installation is done!"
minfo "Thanks for downloading NXVM!"
minfo "Program is beta-testing state, please report all bugs at https://github.com/vladosnx/nxvm"
