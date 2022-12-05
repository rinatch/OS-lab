#!/bin/bash

echo "starting copying-submission"
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/Makefile /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/sched.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished copying"
#cd /usr/src/linux-2.4.18-14custom
#make bzImage
