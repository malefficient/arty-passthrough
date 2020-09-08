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
    rx_b=dev.rx() 
    
    ##-----begin new non-forward-looking return parser-----
    ##Header: response is of the form RETCODE\r\nDATA\r\n ((possible OK\r\n))
    ##Phase 1: Retcode
    ret_code_eol=rx_b.find(b'\r\n')
    
    if (ret_code_eol == -1):
        print("Fatal error parsing response. Retcode EOL delineator missing.")
        sys.exit(-2)
    if (ret_code_eol != 1):
        print("##Warn! unexpected offset to retcode EOL: %d" % (ret_code_eol))
    print("ret_code_eol: %d\n" % (ret_code_eol))
    ret_code=int(rx_b[0]) #ret_code found as expected, single byte followedby \r\n
    ##pop retcode message off rx_buff
    rx_b=rx_b[3:]
    ##Phase 2: response data
    eol_data=rx_b.find(b'\r\n')
    if (eol_data == -1):
        print("##!Medium error parsing response. end of payload not found")
        sys.exit(-1)
    read_response=rx_b[:eol_data]
    
    ##Phase 3: Dopple buff: Any bytes that were read in following read response data
    dopple_buff=rx_b[eol_data:]
    rx_b=bytes() ##rx_buff is officially empty
    
    ########End non-forward looking parser. Begin validating and interpreting parsed response
    ###---- Okay: the retcode to read request is in ret_code, 
    ###-----      the newline delimited response is in read_response
    ###-----      and any ancillary data is in dopple_buff
    print("###----begin read response interpretation----")
    print("##Ret_code: 0x%02X" % (ret_code))
    print("##len(response_buff) = %d" % (len(read_response)))
    print("###ReadResp(%d): %s " % (len(read_response), hexdump.dump(read_response)))
    if (len(read_response) != 45 and length==32): #known good
        print("##Warning: unexpected read response length (%d)" %(len(read_response)))
   
    if (ret_code == 0x30):
        print("##Command returned success!")
    else:
        print("##Warn: command return fail: 0x%02X" % (ret_code))
    print("## len(dopple_buf) : %d" % (len(dopple_buff)))
    print("## dopple_buff: %s" % (hexdump.dump(dopple_buff))) 


    for l in (hexdump.hexdump(dopple_buff,'generator')):
        print("##Dp(%03d)--: %s ##"  % (len(dopple_buff), l))
    # 4D.tx_ex(b'OK\r\n', b'OK\r\n') ##Acknowledge valid reply
    ##Last step: try to syncronize these ACKnowledgements
    ## TODO: Last step: try to syncronize these ACK messages
    dev.tx_ex(b'OK\r\n', b'OK\r\n') ##Acknowledge  reply regardless of retcode 
    #sleep(0.5)
    straggler_buff=dev.rx()
    if len(straggler_buff) != 0:
        print("###Straggler alert:! len(%d)" % (len(straggler_buff)))
        for l in (hexdump.hexdump(straggler_buff,'generator')):
            print("##St(%03d)--: %s ##"  % (len(ret_b), l))
    else:
        print("##Good: No straggling bytes detected")
    return read_response
    
if __name__ == '__main__':
    #S=b'All your base are belong to us!!!\r\n'
    D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 115200)
    perform_sync(D)
    print("************ flushing rx******")

    l = 32
    for i in range(0x10000000, 0x20000000, l):
        buff=read_address(D, i,l) #XXX change 16 back to i just checking for overlapping matches
        if (buff == None):
            print("Q")
            #sys.exit(0)
        else:
            print("****0x%08lX,%04d|%s|____" % (i, l, hexdump.dump(buff)))
    
   
    sys.exit(0)
    
    ###Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##
    ##Rx(016)--: 00000000: 24 3E 3D 60 44 35 45 39  36 0D 0A 34 35 31 0D 0A  $>=`D5E96..451.. ##