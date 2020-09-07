"""
    Script to test serial devices
"""
from time import sleep
import sys
import pylibftdi
from ftdiwrap import LibFTDI_wrap
import hexdump

def perform_sync(dev):

    sync_msg_l=[ (b'?', b'Synchronized\r\n'),
                 (b'Synchronized\r', b'Synchronized\rOK\r\n'),
                 (b'12000\r', b'12000\rOK\r')
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
    cmd = 'R {:d} {:d}\x0D\x0A'.format(address, length)
    ##TX format: R address len\x0D\x0A
    ##RX format: R address len\x0D\x30\x0D\x0A
    ##            Data goes here!
    tx_b = str.encode(cmd, 'utf-8')
    ex_b = b'\x0A' + tx_b[:-1] + b'\x30\x0D\x0A'
    print("##Expecting:\n")
    print("##Ex(%03d)--:           %s ##\n" % (len(ex_b), hexdump.dump(ex_b)), end="")
   
    ##By varying D.max_read, we can carefully parse the results of a read adddress command
    D.read_size=len(ex_b)
    r = dev.tx_ex(tx_b, ex_b)
    #dev.tx(tx_b)
    #TODO: it looks like a max-length argument for rx() would be handy here
    if (r == -1):
        print("Read address 0x%08LX failed:" % (address))
        sys.exit(-1)
    else:
        print("##-----XYZRead command ACK RES follow!---")
        results=dev.rx()
        return
    
    # Check if command succeeded.
    #if '\r0' in result:
    #    board_write('OK\r\n')
    #    expect_read('OK\r\n')
    #    return result

    return None

if __name__ == '__main__':
    #S=b'All your base are belong to us!!!\r\n'
    D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 9600)
    #perform_sync(D)
    print("************ flushing rx******")
    for i in range(0x10000004, 0x10000100):
        read_address(D, i,4)
        break
   
    sys.exit(0)
    ###Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##
