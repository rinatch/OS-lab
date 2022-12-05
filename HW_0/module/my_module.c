/* my_module.c: Example char device module.
 *
 */
/* Kernel Programming */
#define MODULE
#define LINUX
#define __KERNEL__

#include <linux/kernel.h>  	
#include <linux/module.h>
#include <linux/fs.h>       		
#include <asm/uaccess.h>
#include <linux/errno.h>  

#include "my_module.h"

#define MY_DEVICE "ex0_device"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("OS-Lab");

/* globals */
int my_major = 0; /* will hold the major # of my device driver */

struct file_operations my_fops = {
    .open = my_open,
    .release = my_release
};


int init_module(void)
{
    my_major = register_chrdev(my_major, MY_DEVICE, &my_fops);

    if (my_major < 0)
    {
	printk(KERN_WARNING "can't get dynamic major\n");
	return my_major;
    }

    printk("Device driver registered - called from insmod\n");
    return 0;
}


void cleanup_module(void)
{
    printk("Before calling device driver unregister - called from rmmod\n");
    unregister_chrdev(my_major, MY_DEVICE);

    return;
}


int my_open(struct inode *inode, struct file *filp)
{
    unsigned int minor = MINOR(inode->i_rdev);
    printk("Device file opened with minor number %d\n", minor);
    return 0;
}


int my_release(struct inode *inode, struct file *filp)
{
    unsigned int minor = MINOR(inode->i_rdev);
    printk("Device file closed with minor %d\n", minor);
    return 0;
}
