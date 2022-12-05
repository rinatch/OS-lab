#!/bin/bash

echo "starting copying-yael"
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/Makefile /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/yael/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished"
