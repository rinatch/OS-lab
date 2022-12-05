#ifndef _MPI_API_H
#define __API_H
#include <errno.h>


int sys_procenet_invite(pid_t pid, char *message)
{
    printf("we are here 1");
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
    printf("we are here 2");
    if (res >= (unsigned long)(-125))
	{
		errno = -res;
		res = -1;
	}
	return (int)res;	
}


