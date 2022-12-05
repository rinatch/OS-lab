/* devnet.c: Example char device module.
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
#include <asm/segment.h>
#include <asm/current.h>
#include <linux/slab.h>

#include "devnet.h"

#define EMPTY -1
#define LISTENING 0
#define CONNECTING 1

#define MY_DEVICE "devnet"

MODULE_AUTHOR("Anonymous");
MODULE_LICENSE("GPL");


struct packets_list_node{
    struct packet p;
    list_t p_ptr;
};
//TODO: make port linked list containing packets
struct port{
    pid_t pid;
    struct packets_list_node packets_list;
};
struct file_private_data{
    int minor;
    struct port *port_ptr;
    int dest_minor;
    int listen_or_connect; // listen=0, connect=1, neither=-1
};
struct my_file{
    int minor;
    int q_size;
    int users_counter;
    struct port ports_arr[256];//todo:check if * is needed
};

/* globals */
int my_major = 0; /* will hold the major # of my device driver */
struct my_file files_arr[256];

struct file_operations my_fops = {
    .open = my_open,
    .release = my_release,
    .read = my_read,
    .write = my_write,
    .ioctl = my_ioctl,
};

int init_module(void)
{
    // This function is called when inserting the module using insmod

    my_major = register_chrdev(my_major, MY_DEVICE, &my_fops);

    if (my_major < 0)
    {
	printk(KERN_WARNING "can't get dynamic major\n");
	return my_major;
    }
    //initialize files_arr[256]
    int i, j;
    for(i=0; i<255; i++){
        files_arr[i].q_size = 0;
        files_arr[i].minor = EMPTY;
        files_arr[i].users_counter = 0;
        for(j=0; j<255; j++){ //TODO: fix here according to new port
            files_arr[i].ports_arr[j].pid = EMPTY;
            INIT_LIST_HEAD(&files_arr[i].ports_arr[j].packets_list.p_ptr);
        }
    }
    return 0;
}


void cleanup_module(void)
{
    // This function is called when removing the module using rmmod
    unregister_chrdev(my_major, MY_DEVICE);
    //
    // do clean_up();
    //no allocating memory in init_module so no need to free memory
    return;
}

int my_open(struct inode *inode, struct file *filp)
{
    printk(KERN_ERR "opening\n");
    unsigned int new_minor = MINOR(inode->i_rdev);
    struct file_private_data* new_private_data = kmalloc(sizeof(struct file_private_data), GFP_KERNEL);
    if (!new_private_data){
        printk(KERN_WARNING "can't allocate memory ");
        return -ENOMEM;
    }
    new_private_data->minor = new_minor;
    new_private_data->port_ptr = NULL; //being filled in ioctl
    new_private_data->dest_minor = EMPTY; //being filled in ioctl
    new_private_data->listen_or_connect = EMPTY;
    filp->private_data = new_private_data;

    //TODO: ask if minor is unique tp "file" or "process"?
    files_arr[new_minor].minor = new_minor;
    files_arr[new_minor].users_counter += 1;
    return 0;
}

int my_release(struct inode *inode, struct file *filp)//todo free all allocated mem since open
{

    // handle file closing
    struct file_private_data* f_info = (struct file_private_data*)filp->private_data;
    int file_idx = f_info->minor;
    if(f_info->listen_or_connect == LISTENING){
        f_info->port_ptr->pid = EMPTY;//mark that no one listen to port anymore
    }
    if(files_arr[file_idx].users_counter == 0){
        int i;
        //int k=0;
        for ( i = 0; i < 255; ++i) {
            list_t* it;
            list_for_each(it,&files_arr[file_idx].ports_arr[i].packets_list.p_ptr){
                kfree(&files_arr[file_idx].ports_arr[i].packets_list.p_ptr);
                //printk(KERN_ERR " i=%d k=%d\n",i,k);
                //break;
                //if(k == 10){
                //    break;
                //}
            }
        }
    }else{
        files_arr[file_idx].users_counter -= 1;
    }
    kfree(filp->private_data);
    return 0;
}

ssize_t my_read(struct file *filp, char *buf, size_t count, loff_t *f_pos)
{
    // Do read operation.
    // Return number of bytes read.
    if(buf == NULL){
        return -EFAULT;
    }
    struct file_private_data* f_info = (struct file_private_data*)filp->private_data;
    //If didn't do listen before trying to read
    if (f_info->listen_or_connect != LISTENING){
        return -EINVAL;
    }
    if(count < sizeof(struct packet)){
        return -ENOSPC;
    }

    if(list_empty(&f_info->port_ptr->packets_list.p_ptr)){
        return 0;
    }

    struct packets_list_node* new_packet_node;
    list_t* it;
    list_for_each(it,&f_info->port_ptr->packets_list.p_ptr){
        new_packet_node = list_entry(it,struct packets_list_node,p_ptr);
        break;
    }
    int fail_cp = copy_to_user(buf, &new_packet_node->p , sizeof(struct packet));
    if (fail_cp) {
        return -EFAULT;
    }

    list_del(it);
    files_arr[f_info->dest_minor].q_size -= 1;
    return sizeof(struct packet);
}

ssize_t my_write(struct file *filp, const char *buf, size_t count, loff_t *f_pos)
{
    // Do write operation.
    // Return number of bytes written.
    if(buf == NULL){
        return -EFAULT;
    }

    struct file_private_data* f_info = (struct file_private_data*)filp->private_data;

    //If didn't connect before trying to write
    if (f_info->listen_or_connect != CONNECTING){
        return -EINVAL;
    }

    if(f_info->port_ptr->pid == EMPTY){ //no one listen to port anymore)
        return -ECONNRESET;
    }

    //if q_size is maximum
    if (files_arr[f_info->dest_minor].q_size >= QUEUE_SIZE){
        return -EAGAIN;
    }

    struct packets_list_node* new_p_node = kmalloc(sizeof(struct packets_list_node), GFP_KERNEL);
    if(!new_p_node){
        return -ENOMEM;
    }
    new_p_node->p.source_file = f_info->minor;
    new_p_node->p.source_pid = *(&current->pid);;

    //copy only first MTU bytes
    int fail_cp;
    int len = (count > MTU) ? MTU : count;

    fail_cp = copy_from_user(new_p_node->p.payload , buf, MTU);
    if (fail_cp) {
        return -EFAULT;
    }

    new_p_node->p.payload_size = len;
    list_add_tail(&new_p_node->p_ptr,&f_info->port_ptr->packets_list.p_ptr);

    files_arr[f_info->dest_minor].q_size +=1;
    return len;
}

int my_ioctl(struct inode *inode, struct file *filp, unsigned int cmd, unsigned long arg)
{
    struct file_private_data* f_info = (struct file_private_data*)filp->private_data;
    int port_index;
    int file_minor;
    int number = (int)arg;

    switch(cmd)
    {
    case LISTEN:
        // TODO: how to extract first byte?
        port_index = (number) & 0xff;
        file_minor = MINOR(inode->i_rdev);

        if (f_info->listen_or_connect != EMPTY){ //alredy listening or connecting with fd
            return -EINVAL;
        }
        else if(files_arr[file_minor].ports_arr[port_index].pid != EMPTY){ //port already taken
            return -EADDRINUSE;
        }
        else{
            f_info->listen_or_connect = LISTENING;
            f_info->dest_minor = file_minor;
            files_arr[file_minor].ports_arr[port_index].pid = *(&current->pid);
            f_info->port_ptr = &files_arr[file_minor].ports_arr[port_index];
        }
        break;

    case CONNECT:
        //
        port_index = (number >> 8) & 0xff;
        file_minor = (number) & 0xff;
           // printk(KERN_ERR "inside conect, port is %d and minor is %d\n", port_index, file_minor);

        if (f_info->listen_or_connect != EMPTY){ //alredy listening or connecting with fd
            return -EINVAL;
        }
        else if(files_arr[file_minor].ports_arr[port_index].pid == EMPTY){ //no one listen to the port
            return -ECONNREFUSED;
        }
        else{
            f_info->listen_or_connect = CONNECTING;
            f_info->dest_minor = file_minor;
            f_info->port_ptr = &files_arr[file_minor].ports_arr[port_index];
        }
        break;

    default:
	    return -ENOTTY;
    }
    return 0;
}
