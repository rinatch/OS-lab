#include <linux/kernel.h>
#include <linux/sched.h>
#include <asm/current.h>
#include <asm/uaccess.h>

int sys_ex0_syscall(void) {
	// Make process sleep for 5 seconds, first set task state
 	set_current_state(TASK_INTERRUPTIBLE);

	// Normalize to jiffies
	schedule_timeout(5*HZ);
   	
	return 0;
}
