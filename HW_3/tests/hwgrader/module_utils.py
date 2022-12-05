#!/usr/bin/python

__all__ = ('_IOC', '_IO', '_IOR', '_IOW', '_IOWR', 'moduleLoad', 'moduleUnload', 'createDeviceFile', 'rmDeviceFile')

from __future__ import division
from struct import calcsize
import os


sizeof = {
    'byte': calcsize('c'),
    'signed byte': calcsize('b'),
    'unsigned byte': calcsize('B'),
    'short': calcsize('h'),
    'unsigned short': calcsize('H'),
    'int': calcsize('i'),
    'unsigned int': calcsize('I'),
    'long': calcsize('l'),
    'unsigned long': calcsize('L'),
    'long long': calcsize('q'),
    'unsigned long long': calcsize('Q')
}

_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRMASK = ((1 << _IOC_NRBITS)-1)
_IOC_TYPEMASK = ((1 << _IOC_TYPEBITS)-1)
_IOC_SIZEMASK = ((1 << _IOC_SIZEBITS)-1)
_IOC_DIRMASK = ((1 << _IOC_DIRBITS)-1)

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = (_IOC_NRSHIFT+_IOC_NRBITS)
_IOC_SIZESHIFT = (_IOC_TYPESHIFT+_IOC_TYPEBITS)
_IOC_DIRSHIFT = (_IOC_SIZESHIFT+_IOC_SIZEBITS)

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IOC(dir, _type, nr, size):
    if type(_type) == str:
        _type = ord(_type)
        
    cmd_number = (((dir)  << _IOC_DIRSHIFT) | \
        ((_type) << _IOC_TYPESHIFT) | \
        ((nr)   << _IOC_NRSHIFT) | \
        ((size) << _IOC_SIZESHIFT))

    return cmd_number

def _IO(_type, nr):
    return _IOC(_IOC_NONE, _type, nr, 0)

def _IOR(_type, nr, size):
    return _IOC(_IOC_READ, _type, nr, sizeof[size])

def _IOW(_type, nr, size):
    return _IOC(_IOC_WRITE, _type, nr, sizeof[size])

def _IOWR(_type, nr, size):
    return _IOC(_IOC_READ|_IOC_WRITE, _type, nr, sizeof[size])

def moduleLoad(path, module_name):
    status = os.system('/sbin/insmod -f %s' % os.path.join(path, '%s.o' % module_name))
    if status:
        raise Exception('Failed loading the module (error: %d)\n' % status)


def moduleUnload(module_name, silent=True):
    status = os.system('/sbin/rmmod %s' % module_name)
    if status and not silent:
        raise Exception('Failed unloading the module (error: %d)\n' % status)


def createDeviceFile(device_names, file_path, minor):
    f = open('/proc/devices', 'r')

    for line in f:
        temp = line.strip().split()
        
        try:
            if temp[1] == device_names or temp[1] in device_names:
                major = int(temp[0])
                break
        except:
            continue

    status = os.system('mknod %s c %d %d' % (file_path, major, minor))
    if status:
        raise Exception('Failed creating the device file (error: %d)\n' % status)


def rmDeviceFile(file_path, silent=False):
    status = os.system('rm -f %s' % file_path)
    if status and not silent:
        raise Exception('Failed removing device file (error: %d)\n' % status)


def main():
    """main"""
    
    #
    # Calculate the ioctl cmd number
    #
    MY_MAGIC = 'r'
    MY_RESET = _IOW(MY_MAGIC, 0, 'int')
    MY_RESTART = _IOW(MY_MAGIC, 1, 'int')

   
if __name__ == '__main__':
    main()
    
