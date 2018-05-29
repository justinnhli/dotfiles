#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p etc/X11/xorg.conf.d/
cp -f /etc/fstab etc/
cp -f /etc/pacman.conf etc/
cp -f /etc/X11/xorg.conf.d/10-marble-mouse.conf etc/X11/xorg.conf.d/
