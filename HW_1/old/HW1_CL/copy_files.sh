#!/bin/bash

echo "starting copying"
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/include/linux/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/include/linux/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/kernel/Makefile /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/HW1_CL/arch/i386/kernel/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished"
