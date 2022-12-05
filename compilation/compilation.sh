#!/bin/bash

cd /usr/src/linux-2.4.18-14custom
make bzImage
make modules
make modules_install
make install
cd /boot
mkinitrd -f 2.4.18-14custom.img 2.4.18-14custom
#reboot