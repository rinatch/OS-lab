#define SUCCESS 0

#include <linux/kernel.h>
#include <linux/sched.h>
#include <asm/current.h>
#include <asm/uaccess.h>
#include <linux/module.h>  /* Needed by all modules */
#include <linux/kernel.h>  /* Needed for KERN_ALERT */
//#include </usr/src/linux-2.4.18-14custom/include/linux/unistd.h>
#include <linux/procenet_structs.h>
#include <linux/errno.h>
#include <linux/slab.h>
//#include </usr/src/linux-2.4.18-14custom/include/linux/types.h>

int sys_procenet_respond(pid_t pid, int response) {
   // printk(KERN_ERR "got into respond!!\n");
    if (response != 0 && response != 1) {
       // printk(KERN_ERR "response is not 0 or 1\n");
        return -EINVAL;
    }
    int found = 0;
    //int friends_num = 0;
    struct invitations_list_node *curr_invitation;
    list_t *invitation_it;
    list_for_each(invitation_it, &current->invitations)
    {
        curr_invitation = list_entry(invitation_it,
        struct invitations_list_node, ptr);
//        printk(KERN_ERR "pid given is %d\n", pid);
//        printk(KERN_ERR "pid of current node is:%d\n", curr_invitation->inv_data.pid);

        if ((curr_invitation->inv_data.pid) == pid) {
           // printk(KERN_ERR "found pid's invitation in invitations list\n");
            found = 1;
            break;
        }
    }
    if (found == 0) {
        //printk(KERN_ERR "didnt find the pid\n");
        return -ESRCH;
    }/*
    int i;
    for (i=0; i<=MAX_FRIENDS; i++){
    	if (&current->friends[i])
	{
		friends_num++;
		printk(KERN_ERR "current->friends[%d] not null\n", i);
		printk(KERN_ERR "pid is: %d\n",&current->friends[i].alive);
	}
    }*/
    //printk(KERN_ERR "friends num is: %d.\n", *(&current->friends_num));
//    printk(KERN_ERR "after the search!!!!!!!!!!!!!!\n");
//
//    printk(KERN_ERR "&current->friends_num = %d\n", &current->friends_num);
//
//    printk(KERN_ERR "invitation_it ptr = %p\n", invitation_it);


    if (*(&current->friends_num) >= MAX_FRIENDS) {
        //printk(KERN_ERR "got to max friends \n");
        return -ENOSPC;
    }
    //printk(KERN_ERR "no MAX friend\n");
    //if response is equal to 1, add friend to my friends' list and pid's friend list.
    struct friend_t *new_friend = kmalloc(sizeof(struct friend_t), GFP_KERNEL);
    if (!new_friend) {
        //printk(KERN_ERR "kmalloc failed\n");
        return -ENOMEM;
    }
    //printk(KERN_ERR "now we look at cases of responding:\n");
    if (response == 1) {
        //printk(KERN_ERR "respond == 1\n");
        if (!find_task_by_pid(pid)) {
            (new_friend->alive) = 0;
            new_friend->pid = pid;
            //printk(KERN_ERR "made the dead friend node\n");

            *(&current->friends[*(&current->friends_num)]) = *new_friend;
            *(&current->friends_num) = *(&current->friends_num) + 1;

        } else {// new friend is alive
            (new_friend->alive) = 1;
            new_friend->pid = pid;
            *(&current->friends[*(&current->friends_num)]) = *new_friend;
            *(&current->friends_num) = *(&current->friends_num) + 1;

            struct friend_t *me_as_friend = kmalloc(sizeof(struct friend_t), GFP_KERNEL);
            if (!me_as_friend) {
                //printk(KERN_ERR "kmalloc failed 2 \n");
                return -ENOMEM;
            }
            me_as_friend->pid = *(&current->pid);
            me_as_friend->alive = 1;
            //friends_num = 0;
            task_t *other_process = find_task_by_pid(pid);
            /*
                for (i=0; i<=MAX_FRIENDS; i++){
                if (&other_process->friends[i]){
                friends_num++;
                }
                 }*/
            other_process->friends[*(&other_process->friends_num)] = *me_as_friend;
            *(&other_process->friends_num) = *(&other_process->friends_num) + 1;
        }
    }
    //both in response 0 and 1 we do:
    list_del(invitation_it);
    *(&current->invitations_num) = *(&current->invitations_num) - 1;


    task_t *tmp_other_process = find_task_by_pid(pid);
    respond_schedule(tmp_other_process);
    sort_rq_enqueue(tmp_other_process);
    schedule();

    return SUCCESS;
}


