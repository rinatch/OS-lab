#include <linux/module.h>  /* Needed by all modules */
#include <linux/kernel.h>  /* Needed for KERN_ALERT */
#include <linux/procenet_structs.h>
#include <linux/list.h>
#include <linux/sched.h>
#include <asm/current.h>
#include <linux/slab.h>
#include <asm/uaccess.h>
#include <linux/errno.h>


ssize_t sys_procenet_info(pid_t pid, struct friend_t* friends) {
    //printk(KERN_ERR "got into info!!\n");
    if(friends == NULL){
        return -EINVAL;
    }
    task_t* other_process = find_task_by_pid(pid);
    if (!other_process) {
        return -ESRCH;
    }

    int i;
    for (i = 0; i < MAX_FRIENDS; ++i) {
        if(other_process->friends[i].pid == 0){
            break;
        }
        if(!find_task_by_pid(other_process->friends[i].pid)){
            other_process->friends[i].alive = 0;
        }
    }

    int fail_cp = copy_to_user( friends, other_process->friends , MAX_FRIENDS * sizeof(struct friend_t));
    if (fail_cp){
       // printk(KERN_ERR "-EFAULT, copy tmp\n");
        return -EFAULT;
    }
    return (other_process->friends_num);
}


/* debug:
    tmp_friends= kmalloc(MAX_FRIENDS * sizeof(struct friend_t), GFP_KERNEL);
    if (!friends) {
        printk(KERN_ERR "kmalloc failed\n");
        return -ENOMEM;
    }
    int i;
    for (i = 0; i < MAX_FRIENDS; ++i) {
        friends[i].alive = (&other_process->friends[i])->alive;
        friends[i].pid = (&other_process->friends[i])->pid;
    }

    printk(KERN_ERR "end info!!\n");
    for (i = 0; i < 5; ++i) {
        printk(KERN_ERR "friends[i].alive = %d\n",friends[i].alive);
        printk(KERN_ERR "friends[i].pid = %d\n",friends[i].pid);
    }
    printk(KERN_ERR "num = %d\n",other_process->friends_num);*/

