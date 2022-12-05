#!/bin/bash

echo "starting copying-rinat files"
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/Makefile /usr/src/linux-2.4.18-14custom/kernel
#cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/sched.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW2/submission/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished"