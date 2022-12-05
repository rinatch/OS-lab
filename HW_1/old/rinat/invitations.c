
#include <linux/sched.h>
#include <asm/current.h>
#include <asm/uaccess.h>
#include <linux/module.h>  /* Needed by all modules */
#include <linux/kernel.h>  /* Needed for KERN_ALERT */

#include <linux/procenet_structs.h>
#include <linux/errno.h>
#include <linux/slab.h>


ssize_t sys_procenet_invitations(struct invitation_t *invitations, ssize_t size) {
    printk(KERN_ERR "got into invitations!!\n");
/*
    //get len of processes invitations list //todo add to task_struct
    int len = 0;
    struct invitations_list_node* curr_inv_list;
    list_t* invitation_it;
    list_for_each(invitation_it, &current->invitations)
    {
        printk(KERN_ERR "counting:");
        curr_inv_list = list_entry(invitation_it, struct invitations_list_node, ptr);
        printk(KERN_ERR "check curr_inv_list:");
        if (curr_inv_list != NULL) {
            len++;
        }
    }
*/
    int len = *(&current->invitations_num);
    printk(KERN_ERR "invitatons, len = %d\n",len);
    if (size < 0) {
        printk(KERN_ERR "EINVAL\n");
        return -EINVAL;
    } else if (size == 0 || invitations == NULL) {
        printk(KERN_ERR "size == 0 || invitations == NULL. len = %d\n", (int)len);
        return (ssize_t)len;
    }
    // If we get here, there are invitations to add to the buffer
    struct invitation_t*  tmp_invitations = kmalloc((int)size * sizeof(struct invitation_t), GFP_KERNEL);
    if(!invitations){
        printk(KERN_ERR "ENOMEM\n");
        return -ENOMEM;
    }
    printk(KERN_ERR "now need to copy from list to buffer:\n");


    //run on invitations list and copy to the array
    struct invitations_list_node *new_inv_node;
    list_t* invitations_it;
    int i = 0;

    list_for_each(invitations_it, &current->invitations)
    {
        if (len > 0) {//there are more invitations to copy
            new_inv_node = list_entry(invitations_it, struct invitations_list_node, ptr);
            tmp_invitations[i].pid = new_inv_node->inv_data.pid;
            //printk(KERN_ERR "tmp_invitations[i].pid=%d\n",tmp_invitations[i].pid);
           // printk(KERN_ERR "new_inv_node->inv_data.pid=%d\n",new_inv_node->inv_data.pid);

            if (strcpy(tmp_invitations[i].message , new_inv_node->inv_data.message ) == NULL){
                return -EFAULT;
            }
           // printk(KERN_ERR "tmp_invitations[i].message=%s\n",tmp_invitations[i].message);
           // printk(KERN_ERR "new_inv_node->inv_data.message=%s\n",new_inv_node->inv_data.message);
            len--;
            printk(KERN_ERR "now, len = %d\n",(int)len);
        } 
	else//need to add empty invitations
       	{
            tmp_invitations[i].pid = 0;
            if (strcpy(tmp_invitations[i].message , "" ) == NULL){
                return -EFAULT;
            }
        }
        i++;
        size--;
       // printk(KERN_ERR "size = %d\n",(int)size);
        if(size == 0) break;
       // printk(KERN_ERR "not yet broken,  %d\n");
    }
    printk(KERN_ERR "tmp_invitations[i].pid=%d\n",tmp_invitations[0].pid);
    printk(KERN_ERR "tmp_invitations[i].message=%s\n",tmp_invitations[0].message);
    int fail_cp = copy_to_user(invitations, tmp_invitations, (int)size * sizeof(struct invitation_t));
    if (fail_cp){
       printk(KERN_ERR "-EFAULT, copy tmp\n");
       return -EFAULT;
    }

    printk(KERN_ERR "invitations end!!\n");
    printk(KERN_ERR "after copy to user! invitation.pid=%d\n", invitations[0].pid);
    printk(KERN_ERR "after copy to user! invitation.message=%s\n", invitations[0].message);
    return (ssize_t)len;
}
