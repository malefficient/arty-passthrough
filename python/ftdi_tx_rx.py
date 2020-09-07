"""
    Script to test serial devices
"""
from time import sleep
import sys
import pylibftdi
from ftdiwrap import LibFTDI_wrap

def perform_sync(dev):

    try_s=[]
    ##send '?', receive 'Synchronized
    try_s.append ((b'?', b'Synchronized\r\n'))
    try_s.append((b'Synchronized\r\n', b'Synchronized\r'))
    #try_s.append((b'1200\r\n', b'\x00\x00\x00\x00'))
    failed_s=[]
    cnt=0
    for t in try_s:
        #print("##%02d: Tx:%s, Ex:%s" %(cnt, repr(t[0]), repr(t[1])), end="")
        r=dev.tx_ex(t[0],t[1])
        if (r >= 0):
            print("👍")
        else:
            print("💣")
            failed_s.append(cnt)
        sleep(1)
        cnt+=1
   
    if len(failed_s) == 0:
        print("No errors reported! device synced")


def read_address(dev, address, length):
    cmd = 'R {:d} {:d}\r\n'.format(address, length)
    dev.tx_ex(cmd, b'\r')

    
    # Check if command succeeded.
    #if '\r0' in result:
    #    board_write('OK\r\n')
    #    expect_read('OK\r\n')
    #    return result

    return None

if __name__ == '__main__':
    #S=b'All your base are belong to us!!!\r\n'
    D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 9600)
    perform_sync(D)
    print("************ flushing rx******")
    sys.exit(0)
 