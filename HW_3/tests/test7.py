#!/usr/bin/python

from __future__ import division
from struct import *
import fcntl
import struct
import os
import errno

#
# Globals
#
DEVICE_PATH0 = '/dev/devnet0'
DEVICE_PATH1 = '/dev/devnet1'
MTU = 1500
QUEUE_SIZE = 128

#
# Utilities for calculating the IOCTL command codes.
#
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

def unpack_packet(packet):
    packet_format = "B3xii1500B"
    p = struct.unpack(packet_format, packet)
    payload = p[3:][:p[2]]
    payload_str = ''.join(map(chr, payload))
    return {'source_file': p[0], 'source_pid': p[1], 'payload': payload_str}

def connect_address(file_number, port):
    return port * 256 + file_number

def main():
    """Test the device driver"""
    print("test 7 - release a port with 1 message and than try to write new 1")
    pid = os.getpid()
    #
    # Calculate the ioctl cmd number
    #
    MY_MAGIC = 'r'
    LISTEN = _IOW(MY_MAGIC, 0, 'long')
    CONNECT = _IOW(MY_MAGIC, 1, 'long')

    # Open two device files
    f1 = os.open(DEVICE_PATH0, os.O_RDWR)
    f2 = os.open(DEVICE_PATH1, os.O_RDWR)
    
    # LISTEN on one
    fcntl.ioctl(f1, LISTEN, 12)
    # CONNECT on the other
    fcntl.ioctl(f2, CONNECT, connect_address(0, 12))

    message = 'Hellooooo'
    os.write(f2, message)
    os.close(f1)

    # Write a message
    try:
        os.write(f2, message+'2')
    except :
        print("pass")
        return 0;
    print("not pass")
    return 1;



    
if __name__ == '__main__':
    main()
