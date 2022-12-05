#ifndef PROCENET_API_H
#define PROCENET_API_H
#include <errno.h>
#include <stdio.h>
#include <sys/types.h>
#define MAX_MESSAGE 128
#define MAX_FRIENDS 32

struct invitation_t {
   pid_t pid;
   char message[MAX_MESSAGE];
};

struct friend_t {
   pid_t pid;
   int alive;
};

int procenet_invite(pid_t pid, char* message) {
    int res;

    __asm__(
        "pushl %%eax;"
        "pushl %%ebx;"
        "pushl %%ecx;"
        "movl $243, %%eax;"
        "movl %1, %%ebx;"
        "movl %2, %%ecx;"
        "int $0x80;"
        "movl %%eax,%0;"
        "popl %%ecx;"
        "popl %%ebx;"
        "popl %%eax;"
        : "=m"(res)
        : "m"(pid), "m"(message));
    if (res < 0)
    {
        errno = -res;
        res = -1;
    }
    return res;
}

int procenet_respond(pid_t pid, int response) {
    int res;

    __asm__(
        "pushl %%eax;"
        "pushl %%ebx;"
        "pushl %%ecx;"
        "movl $244, %%eax;"
        "movl %1, %%ebx;"
        "movl %2, %%ecx;"
        "int $0x80;"
        "movl %%eax,%0;"
        "popl %%ecx;"
        "popl %%ebx;"
        "popl %%eax;"
        : "=m"(res)
        : "m"(pid), "m"(response));
    if (res < 0)
    {
        errno = -res;
        res = -1;
    }
    return res;
}

int procenet_invitations(struct invitation_t* invitations, ssize_t size) {
    int res;

    __asm__(
        "pushl %%eax;"
        "pushl %%ebx;"
        "pushl %%ecx;"
        "movl $245, %%eax;"
        "movl %1, %%ebx;"
        "movl %2, %%ecx;"
        "int $0x80;"
        "movl %%eax,%0;"
        "popl %%ecx;"
        "popl %%ebx;"
        "popl %%eax;"
        : "=m"(res)
        : "m"(invitations), "m"(size));
    if (res < 0)
    {
        errno = -res;
        res = -1;
    }
    return res;
}

int procenet_info(pid_t pid, struct friend_t* friends) {
    int res;

    __asm__(
        "pushl %%eax;"
        "pushl %%ebx;"
        "pushl %%ecx;"
        "movl $246, %%eax;"
        "movl %1, %%ebx;"
        "movl %2, %%ecx;"
        "int $0x80;"
        "movl %%eax,%0;"
        "popl %%ecx;"
        "popl %%ebx;"
        "popl %%eax;"
        : "=m"(res)
        : "m"(pid), "m"(friends));
    if (res < 0)
    {
        errno = -res;
        res = -1;
    }
    return res;
}
#endif
