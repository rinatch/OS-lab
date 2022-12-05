To compile the python extension put your 'procenet_api.h' header file in this
folder and type the following command in the terminal:

python setup.py build_ext -b .

If the compilation succeeds a new file will be created: 'pyProcenet.so'.
This extension presents four functions that call your new system calls:
1) invite
2) respond
3) invitations
4) info

You can use this functions in a python script or directly from the python
interpreter. Type 'python' in the terminal and then the following commands:

>>>import pyProcenet
>>>import os
>>>pyProcenet.invite(123, "Be my friend!")

Note that the python wrapper can change the function signatures a bit, to make
it more Pythonic. For example, a C function that returns 0 on success or -1
on error will in Python return None on success and throw an exception on error.
Each function's documentation shows its usage:

>>>import pyProcenet
>>>help(pyProcenet.invite)

You can also use the ipython interpreter (you can find the rpm package in the
course website). After running ipython (type 'ipython' in the terminal) do:

[1] import pyProcenet
[2] pyProcenet.invite?
