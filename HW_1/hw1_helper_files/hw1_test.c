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
    printf("ESRCH: %d\n",ESRCH );
    printf("EEXIST: %d\n",EEXIST );
    printf("EFAULT: %d\n",EFAULT );
    printf("ENOMEM: %d\n",ENOMEM );

	// Invite us to be friends
	res = procenet_invite(pid, "Hello me, meet the real me, and my misfit's way of life");
	assert(res == 0);

    // Fetch our invitation
    res = procenet_invitations(&invitation, 1);
    assert(res == 0); // No more invitations to read

    assert(invitation.pid == pid);
    printf("Invitation message: %s\n", invitation.message);

    // Accept
    res = procenet_respond(pid, 1);
    assert(res == 0);

    // Get our friends
    res = procenet_info(pid, friends_list);
    assert(res == 1); // We expect one friend
    printf("Our friend %d is %s\n", friends_list[0].pid, friends_list[0].alive == 1 ? "alive" : "dead!");

	return 0;
}
