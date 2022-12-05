
#define SUCCESS 0

#include <linux/sched.h>
#include <asm/current.h>
#include <asm/uaccess.h>
#include <linux/module.h>  /* Needed by all modules */
#include <linux/kernel.h>  /* Needed for KERN_ALERT */

#include <linux/procenet_structs.h>
#include <linux/errno.h>
#include <linux/slab.h>

int sys_procenet_invite(pid_t pid, char *message) {
    printk(KERN_ERR "got into invite!!\n");
    if(!message){
       printk(KERN_ERR "message is NULL\n");
    }
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
    struct invitations_list_node* curr_inv_list;
    pid_t my_pid = *(&current->pid);
    task_t* other_process = find_task_by_pid(pid);
    list_t* invitation_it; //todo: check if to get back to head
    list_for_each(invitation_it, &other_process->invitations)
    {
        curr_inv_list = list_entry(invitation_it, struct invitations_list_node, ptr);
        if ((curr_inv_list->inv_data.pid) == my_pid) {
	        printk(KERN_ERR "invitation already exists, do nothing\n");
            return SUCCESS;
        }
    }
    //If we get here the invitation should be added to the list
    //create the invitation data:
    struct invitations_list_node* new_list_node = kmalloc(sizeof(struct invitations_list_node), GFP_KERNEL);
    if (!new_list_node) {
        return -ENOMEM;
    }
    new_list_node->inv_data.pid = my_pid;
    /*new_list_node->inv_data.message = kmalloc(MAX_MESSAGE*sizeof(char),GFP_KERNEL);
    if(!new_list_node->inv_data.message){
       return -ENOMEM;
    }*/
    if (!message) {
        printk(KERN_ERR "message is NULL\n");
        char default_message[MAX_MESSAGE] = "Hi! Please be my friend";
        /*if (strcpy((new_list_node->inv_data.message), default_message) == NULL) {
            return -EFAULT;
        }*/
	int fail_cp = copy_from_user(new_list_node->inv_data.message, default_message, MAX_MESSAGE);
	if (fail_cp){
        printk(KERN_ERR "EFAULT, default message\n");
	   return -EFAULT;
	}
	
    }else{
        int fail_cp = copy_from_user(new_list_node->inv_data.message, message, MAX_MESSAGE);
	if (fail_cp){
        printk(KERN_ERR "EFAULT, given message\n");
        return -EFAULT;
	 }
    }

    //push the invitation to the list
    list_add_tail(&new_list_node->ptr, &other_process->invitations);
    *(&other_process->invitations_num) = *(&other_process->invitations_num) + 1;
   /* 
    printk(KERN_ERR "printing invitations list of other process\n");
    list_t* it;
    list_for_each(it, &other_process->invitations)
    {
       {
            curr_inv_list = list_entry(it,struct invitations_list_node, ptr);
            printk(KERN_ERR "message is: %s.\n",curr_inv_list->inv_data.message);
	    printk(KERN_ERR "pid %ld  in list invitations.\n",(long) curr_inv_list->inv_data.pid);
        }
    }*/
    return SUCCESS;
}

