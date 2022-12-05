
#define SUCCESS 0

#include <linux/sched.h>
#include <asm/current.h>
#include <asm/uaccess.h>
#include <linux/module.h>  /* Needed by all modules */
#include <linux/kernel.h>  /* Needed for KERN_ALERT */

#include <linux/procenet_structs.h>
#include <linux/errno.h>
#include <linux/slab.h>
//#include <net/pkt_sched.h>
//#include </usr/src/linux-2.4.18-14custom/kernel/sched.c>

//#define cpu_rq(cpu) (runqueues + (cpu))
//#define this_rq() cpu_rq(smp_processor_id())
//typedef struct runqueue runqueue_t;

int sys_procenet_invite(pid_t pid, char *message) {
    //printk(KERN_ERR "got into invite!!\n");
    if (!message) {
        //printk(KERN_ERR "message is NULL\n");
    }
    if (pid < 1) {
        return -EINVAL;
        //printk(KERN_ERR "EINVAL\n");
    } else if (!find_task_by_pid(pid)) {
        //printk(KERN_ERR "ESRCH\n");
        return -ESRCH;
    }
    int i;
    for (i = 0; i <= MAX_FRIENDS; i++) {
        if (*(&current->friends[i].pid) == pid) {
            //printk(KERN_ERR "already friends\n");
            return -EEXIST;
        }
    }
    struct invitations_list_node *curr_inv_list;
    pid_t my_pid = *(&current->pid);
    task_t *other_process = find_task_by_pid(pid);
    //printk(KERN_ERR " &other_process->invitations1 : %p\n", &other_process->invitations);

    list_t *invitation_it;
    list_for_each(invitation_it, &other_process->invitations)
    {
        curr_inv_list = list_entry(invitation_it,
        struct invitations_list_node, ptr);
        if ((curr_inv_list->inv_data.pid) == my_pid) {
           // printk(KERN_ERR "invitation already exists, do nothing\n");
            return SUCCESS;
        }
    }
    //If we get here the invitation should be added to the list
    //create the invitation data:
    struct invitations_list_node *new_list_node = kmalloc(sizeof(struct invitations_list_node), GFP_KERNEL);
    if (!new_list_node) {
        return -ENOMEM;
    }
    new_list_node->inv_data.pid = my_pid;
    //new_list_node->inv_data.message = kmalloc(MAX_MESSAGE*sizeof(char),GFP_KERNEL);
    //if(!new_list_node->inv_data.message){
    // return -ENOMEM;
    //}
    if (!message) {
       // printk(KERN_ERR "message is NULL\n");
        char default_message[MAX_MESSAGE] = "Hi! Please be my friend";
        int len = strlen(default_message);
        //printk(KERN_ERR "message len :%d\n", len);
//        printk(KERN_ERR "default_message :%p\n", default_message);
//        printk(KERN_ERR "new_list_node->inv_data.message :%p\n", new_list_node->inv_data.message);
        if (strncpy((new_list_node->inv_data.message), default_message, len) == NULL) {
            //printk(KERN_ERR "strcpy failed - default msg\n");
            return -EFAULT;
        }
        //printk(KERN_ERR "passed strcpy\n");
    } else {
        //printk(KERN_ERR "message is :%s\n", message);

        int fail_cp = copy_from_user(new_list_node->inv_data.message, message, MAX_MESSAGE);
        if (fail_cp) {
            //printk(KERN_ERR "copy_from_user failed\n");
            return -EFAULT;
        }
//        printk(KERN_ERR "message_ptr is :%p\n", new_list_node->inv_data.message);
//        printk(KERN_ERR "message copied is :%s\n", new_list_node->inv_data.message);
    }
    //printk(KERN_ERR "passed else\n");
    //push the invitation to the list
    //printk(KERN_ERR " &other_process->invitations2 : %p\n", &other_process->invitations);
    list_add_tail(&new_list_node->ptr, &other_process->invitations);
    *(&other_process->invitations_num) = *(&other_process->invitations_num) + 1;
    invite_schedule(other_process);
    sort_rq_enqueue(other_process);
    //debug:
   // printk(KERN_ERR "in invite after sort\n");
    schedule();

    return SUCCESS;
}

