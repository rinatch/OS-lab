#include <stdio.h>
#include <time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>
#include "procenet_api.h"

#define TIMEDIFF_IN_USECS(x, y) ((x.tv_sec - y.tv_sec)*1e6 + (x.tv_usec - y.tv_usec))

void spend_time(int s) {
    struct timeval start_time;
    struct timeval cur_time;
    long us = s * 1e6;
    int i;
    int x=10000000;

    gettimeofday(&start_time, NULL);
    cur_time = start_time;
    while (TIMEDIFF_IN_USECS(cur_time, start_time) < us) {
        for (i=0; i<x; i++) {}
        gettimeofday(&cur_time, NULL);
    }
}

int main()
{
	// simple self test
    pid_t cpid, ppid;
	int res = -1;
    time_t start_time, end_time;
    
    ppid = getpid();
    cpid = fork();
    if (cpid == 0) {
        //printf("child start\n");
        // In child: run for 5 seconds
        spend_time(5);
       // printf("child end\n");
        return 0;
    }
    // In parent: send an invitation to the child and make sure we're blocked right afterwards
    start_time = time(NULL);
   // printf("dad start\n");
    procenet_invite(cpid, NULL);

   // printf("dad end1\n");
    end_time = time(NULL);
    wait(NULL);
    //printf("dad end 2\n");

    // Make sure return value and polling time was as expected

	assert(end_time - start_time > 4);
    //int r = (end_time - start_time);
    //printf("end_time - start_time = %d\n",r);
	assert(end_time - start_time < 6);
	printf("Test Done\n");
	
	return 0;
}
