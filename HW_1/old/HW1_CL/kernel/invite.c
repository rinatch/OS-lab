
#define SUCCESS 0

#include <linux/sched.h>
#include <asm/current.h>
#include <asm/uaccess.h>
#include <linux/module.h>  /* Needed by all modules */
#include <linux/kernel.h>  /* Needed for KERN_ALERT */

#include <linux/procenet_structs.h>
#include <linux/errno.h>
//#include "procenet_api.h"
#include <linux/slab.h>

int sys_procenet_invite(pid_t pid, char *message) {
    printk(KERN_ERR "got into invite!!\n");
    
    if (pid < 1) {
        return -EINVAL;
	printk(KERN_ERR "EINVAL\n");
    } else if (!find_task_by_pid(pid)) {
        printk(KERN_ERR "ESRCH\n");
        return -ESRCH;
    }
    int i;
    for (i=0; i<=MAX_FRIENDS; i++){
      if( *(&current->friends[i].pid) == pid){
	 printk(KERN_ERR "already friends\n");
	 return -EEXIST;	     
      }
    }
    struct invitation_t* curr_inv_list;
    pid_t my_pid = *(&current->pid);
    task_t* other_process = find_task_by_pid(pid);
    list_t* invitation_it; //todo: check if to get back to head
    list_for_each(invitation_it, &other_process->invitations)
    {
        curr_inv_list = list_entry(invitation_it, struct invitation_t, ptr);
        if ((curr_inv_list->pid) == my_pid) {
	   printk(KERN_ERR "invitation already exists, do nothing\n");
            return SUCCESS;
        }
    }
    //If we get here the invitation should be added to the list
    //create the invitation:
    struct invitation_t* new_invitation = kmalloc(sizeof(struct invitation_t), GFP_KERNEL);
    if (!new_invitation) {
        return -ENOMEM;
    }
    new_invitation->pid = pid;
    if (message == NULL) {
        char default_message[MAX_MESSAGE] = "Hi! Please be my friend";
        if (strcpy((new_invitation->message), default_message) == NULL) {
            return -EFAULT;
        }
    }
    if (strcpy((new_invitation->message), message) == NULL) {
        return -EFAULT;
    }
    //push the invitation to the list
    printk(KERN_ERR "message is: %s. \n",(new_invitation->message));
    list_add_tail(&new_invitation->ptr,&other_process->invitations);
    /*
    printk(KERN_ERR "printing invitations list of other process\n");
    list_for_each(invitation_it, &other_process->invitations)
    {
       {
            curr_inv_list = list_entry(invitation_it, struct invitation_t, ptr);
            printk(KERN_ERR "message is: %s.\n",curr_inv_list->message);
        }
    }*/
    
    return SUCCESS;
}


