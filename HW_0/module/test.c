#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main()
{
   // Open our sample device file
   int fd  = open("/dev/ex0_device", O_RDWR);
   if (fd < 0) printf("Failed openning device file\n");

   // Now close it
   close(fd);
   return 0;
}
