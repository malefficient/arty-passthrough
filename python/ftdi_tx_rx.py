"""
    Script to test serial devices
"""
from time import sleep
import sys
import pylibftdi
from ftdiwrap import LibFTDI_wrap

def perform_sync(dev):

    sync_msg_l=[ (b'?', b'Synchronized\r\n'),
                 (b'Synchronized\r\n', b'Synchronized\rOK\r'),
                 (b'12000\r\n', b'12000\rOK\r\n')
    ]
  
    failed_l=[]
    cnt=0
    for t in sync_msg_l:
        r=dev.tx_ex(t[0],t[1])
        if (r == -1):
            print("💣")
            failed_l.append( (cnt, t))
        else:
            print("👍")
        sleep(1)
        cnt+=1
   
    if len(failed_l) == 0:
        print("No errors reported! device synced")
        return True
    else:
        print("## (%d/%d) syncronization messages failed" %(len(failed_l), len(sync_msg_l)))
        return False
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
 