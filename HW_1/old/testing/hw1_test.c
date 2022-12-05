#include <stdio.h>
#include <assert.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include "procenet_api.h"


int main()
{
	int res = -1;
    pid_t pid = getpid();
    struct invitation_t invitation;
    struct friend_t friends_list[MAX_FRIENDS];

	// Invite us to be friends
	res = procenet_invite(pid, "Hello me, meet the real me, and my misfit's way of life");
	assert(res == 0);
    printf("passed invite\n");
    // Fetch our invitation
       res = procenet_invitations(&invitation, 1);
    printf("res = %d\n",res);
    assert(res == 0); // No more invitations to read
    printf("passed invitations1");

    printf("invitation.pid == %d\n",invitation.pid);
    //printf("invitation->pid == %d\n",invitation->pid);
    printf("should be pid == %d\n",pid);
    assert(invitation.pid == pid);
    printf("Invitation message: %s\n", invitation.message);
    printf("passed invitations2\n");


    // Accept
    res = procenet_respond(pid, 1);
    assert(res == 0);

    // Get our friends
    res = procenet_info(pid, friends_list);
    printf("res = %d\n",res);
    assert(res == 1); // We expect one friend
    printf("Our friend %d is %s\n", friends_list[0].pid, friends_list[0].alive == 1 ? "alive" : "dead!");

	return 0;
}
