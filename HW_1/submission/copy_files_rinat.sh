#!/bin/bash

echo "starting copying-submission"
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/include/linux/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/include/linux/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/Makefile /usr/src/linux-2.4.18-14custom/kernel
#cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/kernel/sched.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_1/submission/arch/i386/kernel/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished copying"
#cd /usr/src/linux-2.4.18-14custom
#make bzImage
