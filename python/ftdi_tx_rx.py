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
                 (b'12000\r', b'12000\rOK\r\n')]
  
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
        #print("No errors reported! sending dummy read: 0x80000000 4")
        #dev.tx(b'R 0268435468 0004\r\n')
        #print("###returned")
        #r = dev.rx()
        return True
    else:
        print("## (%d/%d) syncronization messages failed" %(len(failed_l), len(sync_msg_l)))
        return False
def read_address(dev, address, length):
    cmd ="R %010d %04d\x0D\x0A" % (address, length)
    ##note: during the synchronization phase the protocol is
    ##      send(msg)\r recv(mesg)\r\n, once we get to the read command this inexplicably flips to
    ##      send(msg)\r\n recv(msg)\r
    tx_b = str.encode(cmd, 'utf-8')
    ex_b = tx_b[:-1]
    print("##Expecting:\n")
    print("##Ex(%03d)--:           %s ##\n" % (len(ex_b), hexdump.dump(ex_b)), end="")
    ########_---------------
    
    if (dev.tx_ex(tx_b, ex_b) < 0):
        print("##Error: Echo back failed") 
        return None
    ##if we make it this far the command was succesfullly tx'd and echo'd back
    ##read any/all bytes remaining in the buffer
    rx_b=dev.rx(n=0x32) #56 == sizeof response for read (len=32)
    if (len(rx_b) != 56):
        print("##Warning: un-expected return length: %d" %(len(rx_b)))
    ##Check return val up front:
    ##note that even failed commands are ACK'd with OK at end of transaction
    if (rx_b[0] == 0x30):
        print("Command returned success (0x30)")
    else:
        print("Command failed: (0x%02X)" % rx_b[0])

    ##-----begin new non-forward-looking return parser-----
    ##Header: response is of the form RETCODE\r\nDATA\r\n ((possible OK\r\n))
    if (b'\r\n' not in rx_b):
        print("Major parsing error fail.")
        sys.exit(0)
    if rx_b.find(b'\r\n') != 1:
        print("Error parsing response. Return code not found")
        sys.exit(0)
    ret_code=int(rx_b[0])
    print("Received ret code: %d" % (ret_code))
    ##pop initial 3 parsed bytes off rx buff
    rx_b=rx_b[3:]
    ##look for second newline delineator (required)
    eol_data=rx_b.find(b'\r\n')
    print("EOL2 found: %s\n" % (eol_data))
    read_response=rx_b[:eol_data]
    print("###ReadResp(%d): %s " % (len(read_response), hexdump.dump(read_response)))
    if (len(read_response) != 45 and length==32): #known good
        print("##Warning: unexpected read response length (%d)" %(len(read_response)))
    rx_b=rx_b[eol_data:]
    
    dopple_buff=rx_b
    rx_b=bytes() ##rx_buff is officially empty
    print("## doppleganger rx_b: len=%d" % (len(dopple_buff)))
    print("## DopppleD:  %s" % (hexdump.dump(dopple_buff)))
    ###---- Okay: the retcode to read request is in ret_code, 
    ###-----      the newline delimited response is in read_response
    ###-----      and any ancillary data is in dopple_buff
    print("###----begin read response interpretation----")
    print("Ret_code: 0x%02X" % (ret_code))
    print("len(response_buff) = %d" % (len(read_response)))
    print("###Todo: retcode validation etc etc")
    sys.exit(0)
    if ( rx_b[0] == 0x30 and rx_b[-2] == 0x0D and rx_b[-1] == 0x0A):
        print("##Read response: %s" % (hexdump.dump(rx_b)))
        ret=rx_b[3:-2] ##first three bytes are 'header', last two are '\r\n'
        print("##trimmed retval  : %s" % (hexdump.dump(ret)))
        D.tx_ex(b'OK\r\n', b'OK\r\n') ##Acknowledge valid reply

    else:
        print("##!Fail on payload validation:")
        print("##failed retval   : %s" % (hexdump.dump(rx_b)))
        ret = None

    D.tx_ex(b'OK\r\n', b'OK\r\n') ##Acknowledge  reply regardless of retcode 
    return ret
    
if __name__ == '__main__':
    #S=b'All your base are belong to us!!!\r\n'
    D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 115200)
    perform_sync(D)
    print("************ flushing rx******")

    l = 32
    for i in range(0x10000000, 0x10000040, l):
        buff=read_address(D, i,l)
        if (buff == None):
            print("Q")
            #sys.exit(0)
        else:
            print("****0x%08lX,%04d|%s|____" % (i, l, hexdump.dump(buff)))
    
   
    sys.exit(0)
    
    ###Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##
    ##Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##