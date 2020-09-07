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
                 (b'12000\r', b'12000\rOK\r')]
  
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
        print("No errors reported! sending dummy read: 0x80000000 4")
        dev.tx(b'R 0268435468 0004\r\n')
        print("###returned")
        r = dev.rx()
        return True
    else:
        print("## (%d/%d) syncronization messages failed" %(len(failed_l), len(sync_msg_l)))
        return False
def read_address(dev, address, length):
    cmd ="R %010d %04d\x0D\x0A" % (address, length)
    
    ##TX format: R address len\x0D\x0A
    ##RX format: R address len\x0D\x30\x0D\x0A
    ##            Data goes here!
    tx_b = str.encode(cmd, 'utf-8')
    ex_b = tx_b[:-1]
    print("##Expecting:\n")
    print("##Ex(%03d)--:           %s ##\n" % (len(ex_b), hexdump.dump(ex_b)), end="")
   
    D.read_size=len(ex_b)
    r = dev.tx_ex(tx_b, ex_b) #We are carefyl not to read past the echo back by setting D.read_size
    #TODO: it looks like a max-length argument for rx() would be handy here
    if (r == -1):
        print("##Error: did not receive echo back for read request")
        ##JC: TODO: Log this somewhere or something?
    else:
        print("##Read request Acknowledged")
    
    res=dev.rx()
    fail=0
    print("#^^^respons above. if \x0D\x00 THEN good things?")
    sys.exit(0)
    print("##XXX %s" % (hexdump.dump(res)))
    if (len (res) != 16):
        print("##Invalid response size: %d" % (len(res)))
        return None
        
    if (res[0] == 0x24 and res[-2] == 0x0D and res[-1] == 0x0A): ## '$'
        print("##!!! payload detected")
        payload=res[1:-2]
        print("##%s" %(res))
        print(hexdump.dump(res))
        return payload
    else:
        print("##!Fail on payload validation: fail=%d" % (fail))
        print(hexdump.dump(res))
        return None
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
    perform_sync(D)
    print("************ flushing rx******")
    for i in range(0x10000000, 0x10000008, 4):
        read_address(D, i,4)
    
   
    sys.exit(0)
    
    ###Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##
    ##Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##