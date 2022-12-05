#!/bin/bash

echo "starting copying-rinat"
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/procenet_structs.h /usr/src/linux-2.4.18-14custom/include/linux
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/sched.h /usr/src/linux-2.4.18-14custom/include/linux
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/fork.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/exit.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/info_procenet.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/invite.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/invitations.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/respond.c /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/Makefile /usr/src/linux-2.4.18-14custom/kernel
cp /mnt/hgfs/shared_folder/OS_Lab/HW_1/rinat/entry.S /usr/src/linux-2.4.18-14custom/arch/i386/kernel
echo "finished"
