#include <stdio.h>
#include <sys/time.h>
#include <errno.h>

int ex0_syscall(void)
{
	int res;
	__asm__
	(
		"pushl %%eax;"
		"movl $243, %%eax;"
		"int $0x80;"
		"movl %%eax, %0;"
		"popl %%eax;"
		:"=m" (res)
	);
	
	if (res >= (unsigned long)(-125))
	{
		errno = -res;
		res = -1;
	}
	return (int)res;	
}

int main()
{
   struct timeval start, end;
   gettimeofday(&start, NULL);
   ex0_syscall();
   gettimeofday(&end, NULL);
   double latency = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) * 1e-6;
   printf("Time passed after the syscall is: %lf\n", latency);
   return 0;
}
