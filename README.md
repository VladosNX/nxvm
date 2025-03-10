[NXVM Site is online!](https://vladosnx.github.io/nxvm)

**WARNING** You're reading a README.md file for beta-version v0.2.2!
This version has a lot of bugs and program can be exited with errors for a many times.
Please report bugs at [project page](https://github.com/vladosnx/nxvm).

# NXVM v0.2.2

> *Just a VM manager for QEMU*

![NXVM Logo](NXVMLogo.png)

![NXVM Home page](screenshot.png)

## What is NXVM

**NXVM** is project which helps you to use QEMU emulator in a few clicks. Please note that NXVM is just a QEMU manager,
not a written from scratch virtual machine.

## Preparing for installation

Now, NXVM has this dependencies:

- `qemu-base`
- `qemu-system-x86`
- `qt5-base`
- `python-pip`

Installation on Arch Linux and systems based on it:

> sudo pacman -S qemu-base qemu-system-x86 qt5-base python-pip

Installation on Debian-based systems:

> sudo apt install qtbase5-dev qemu qemu-system-x86 python-pip

## Installation

Open your terminal and execute command:

> curl -sSL https://raw.githubusercontent.com/VladosNX/nxvm/refs/heads/main/install.sh | sudo bash

This command will download and install NXVM from source without buildings.
