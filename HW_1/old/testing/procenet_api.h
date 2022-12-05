#ifndef _PROCENET_API_H
#define _PROCENET_API_H

#include <errno.h>
#define MAX_FRIENDS 32
#define MAX_MESSAGE 128

struct friend_t {
    pid_t pid;
    int alive;
};

struct invitation_t {
    pid_t pid;
    char message[MAX_MESSAGE];
};

int procenet_invite(pid_t pid, char *message)
{
    printf("we are here 1\n"); //todo:remove!!
    int res;
    __asm__
    (
    "pushl %%eax;"
    "pushl %%ebx;"
    "pushl %%ecx;"
    "movl $243, %%eax;"
    "movl %1, %%ebx;"
    "movl %2, %%ecx;"
    "int $0x80;"
    "movl %%eax, %0;"
    "popl %%ecx;"
    "popl %%ebx;"
    "popl %%eax;"
    :"=m" (res)
    : "m" (pid) ,"m" (message)
    );
    printf("we are here 2\n");
    if (res >= (unsigned long)(-125))
    {
        errno = -res;
        res = -1;
    }
    return (int)res;
}

int procenet_respond(pid_t pid, int response)
{
    printf("we are here 3\n");
    int res;
    __asm__
    (
    "pushl %%eax;"
    "pushl %%ebx;"
    "pushl %%ecx;"
    "movl $244, %%eax;"
    "movl %1, %%ebx;"
    "movl %2, %%ecx;"
    "int $0x80;"
    "movl %%eax, %0;"
    "popl %%ecx;"
    "popl %%ebx;"
    "popl %%eax;"
    :"=m" (res)
    : "m" (pid) ,"m" (response)
    );
    printf("we are here 4\n");
    if (res >= (unsigned long)(-125))
    {
        errno = -res;
        res = -1;
    }
    return (int)res;
}

ssize_t procenet_invitations(struct invitation_t *invitations, ssize_t size)
{
    printf("we are here 5\n");
    int res;
    __asm__
    (
    "pushl %%eax;"
    "pushl %%ebx;"
    "pushl %%ecx;"
    "movl $245, %%eax;"
    "movl %1, %%ebx;"
    "movl %2, %%ecx;"
    "int $0x80;"
    "movl %%eax, %0;"
    "popl %%ecx;"
    "popl %%ebx;"
    "popl %%eax;"
    :"=m" (res)
    : "m" (invitations) ,"m" (size)
    );
    printf("we are here 6\n");
    if (res >= (unsigned long)(-125))
    {
        printf("we are here -errno\n");
        errno = -res;
        res = -1;
    }
    return (int)res;
}

ssize_t procenet_info(pid_t pid, struct friend_t* friends)
{
    int res;
    __asm__
    (
    "pushl %%eax;"
    "pushl %%ebx;"
    "pushl %%ecx;"
    "movl $245, %%eax;"//todo: change
    "movl %1, %%ebx;"
    "movl %2, %%ecx;"
    "int $0x80;"
    "movl %%eax, %0;"
    "popl %%ecx;"
    "popl %%ebx;"
    "popl %%eax;"
    :"=m" (res)
    : "m" (pid) ,"m" (friends)
    );
    if (res >= (unsigned long)(-125))
    {
        errno = -res;
        res = -1;
    }
    return (int)res;
}

#endif //_PROCENET_API_H

