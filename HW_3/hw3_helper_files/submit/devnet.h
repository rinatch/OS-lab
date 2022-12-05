#ifndef _DEVNET_H_
#define _DEVNET_H_

#include <linux/ioctl.h>
#include <linux/types.h>

#define MTU 1500
#define QUEUE_SIZE 128

//
// Function prototypes
//
int my_open(struct inode *, struct file *);

int my_release(struct inode *, struct file *);

ssize_t my_read(struct file *, char *, size_t, loff_t *);

ssize_t my_write(struct file *, const char *, size_t, loff_t *);

int my_ioctl(struct inode *inode, struct file *filp, unsigned int cmd, unsigned long arg);

struct packet {
	unsigned char source_file;
	pid_t source_pid;
	int payload_size;
	unsigned char payload[MTU];
};

#define MY_MAGIC 'r'
#define LISTEN  _IOW(MY_MAGIC, 0, long)
#define CONNECT  _IOW(MY_MAGIC, 1, long)

#endif
