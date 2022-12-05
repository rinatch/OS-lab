#!/bin/bash

reset () {
    dmesg -c > /dev/null
    rm -f /dev/devnet*
    rmmod devnet
    insmod ./devnet.o
    maj=$(cat /proc/devices | grep devnet | awk '{print $1}')
    mknod /dev/devnet0 c $maj 0
    mknod /dev/devnet1 c $maj 1
}

finish () {
    rm -f /dev/devnet*
    rmmod devnet
}

cd /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests

dmesg -c > /dev/null
echo " ###### removing all ###### "
rm -f /dev/devnet*
rmmod devnet

echo " ###### make clean and make ###### "
make clean
make

echo " ###### create devnet ###### "
insmod ./devnet.o
lsmod | grep devnet

echo " ###### getting major num ###### "
cat /proc/devices | grep devnet
maj=$(cat /proc/devices | grep devnet | awk '{print $1}')
echo "major = $maj"

echo " ###### creating nodes ###### "
mknod /dev/devnet0 c $maj 0
mknod /dev/devnet1 c $maj 1
ls -lh /dev | grep devnet

echo " ###### running test  ######"
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/before_test.txt
dmesg -c > /dev/null

./test1.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test1
reset

./test2.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test2
reset

./test3.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test3
reset

./test4.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test4
reset

./test5.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test5
reset

./test6.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test6
reset

./test7.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test7
reset

./test8.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test8
reset

./test9.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test9
reset

./test10.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test10
reset

./test11.py
dmesg > /mnt/hgfs/shared_folder/OS_Lab/HW_3/tests/test11
reset

finish