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
    pid_t cpid, ppid, gpid;
	int res = -1;
    time_t start_time, end_time;
    
    ppid = getpid();
    cpid = fork();
    if (cpid == 0) {
        // In child: run for 5 seconds
        gpid = fork();
        start_time = time(NULL);
        procenet_invite(gpid, NULL);
        end_time = time(NULL);
        //spend_time(5);
        return 0;
    }
    // In parent: send an invitation to the child and make sure we're blocked right afterwards
    start_time = time(NULL);
    procenet_invite(cpid, NULL);
    end_time = time(NULL);
    wait(NULL);

    // Make sure return value and polling time was as expected
	assert(end_time - start_time > 4);
	assert(end_time - start_time < 6);
	printf("Test Done\n");
	
	return 0;
}
