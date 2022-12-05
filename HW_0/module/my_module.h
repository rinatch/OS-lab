#ifndef _MY_MODULE_H_
#define _MY_MODULE_H_

#include <linux/ioctl.h>

#define MY_OP1 _IOW('r', 0, int)

//
// Function prototypes
//
int my_open(struct inode *, struct file *);

int my_release(struct inode *, struct file *);

#endif
