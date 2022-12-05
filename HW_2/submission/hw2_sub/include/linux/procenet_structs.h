

#ifndef _PROCENET_STRUCTS_H
#define _PROCENET_STRUCTS_H
#define MAX_FRIENDS 32
#define MAX_MESSAGE 128

#include <linux/list.h>

struct friend_t{
    pid_t pid;
    int alive;
};

struct invitation_t{
    pid_t pid;
    char message[MAX_MESSAGE];
};

struct invitations_list_node{
    struct invitation_t inv_data;
    list_t ptr;
};



#endif //_PROCENET_STRUCTS_H
