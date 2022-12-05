#!/bin/bash

echo "starting copying-submission"
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/include/linux/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/include/linux/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/kernel/Makefile /usr/src/linux-2.4.18-14custom/kernel
cp -p /mnt/hgfs/shared_folder/OS_Lab/HW_2/submission/hw1_sub/arch/i386/kernel/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished copying"
#cd /usr/src/linux-2.4.18-14custom
#make bzImage
