#!/usr/bin/sh

minfo () {
  echo -e "\e[44mINFO \e[0m $1"
}
mdone () {
  echo -e "\e[42mDONE \e[0m $1"
}
merror () {
  echo -e "\e[41mERROR\e[0m $1"
}

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
chmod +x /usr/bin/nxvm.py
mdone "Copied nxvm binary to /usr/bin and made it executable"
cp nxvm.desktop /usr/share/applications/nxvm.desktop
mdone "Copied NXVM.desktop to /usr/share/applications"
mdone "NXVM installation is done!"
minfo "Thanks for downloading NXVM!"
minfo "Program is beta-testing state, please report all bugs at https://github.com/vladosnx/nxvm"