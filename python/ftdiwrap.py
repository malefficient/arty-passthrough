"""
   Simple wrapper for libftdi. Provides sane defaults, error-checking
"""
import time
import binascii
import struct
import hexdump
import sys
#from pylibftdi import Device, Driver, INTERFACE_B
import pylibftdi
import re

class FTDIWrap_Err(Exception):
    """Generic FTDIWrap exception
    Attributes:
        action -- read|write
        retval -- return value of libftdi.dev.read|write
        expected_retval -- expected return value
    """
    ##self.retval = 0
    ##self.expected_retval = 0
    ##self.action = None
    def __init__(self, _action, _v=None, _ex=None):
        self.retval = _v
        self.expected_retval = _ex
        self.action = _action
    def __str__(self):
        ret = "FTDIWrap Error: %s" % (self.action)
        if (self.retval):
            ret += "returned: %s" % (self.retval)
        if (self.expected_retval):
            ret += " (expected %s)" %(self.expected_retval)
        return ret
class LibFTDI_wrap():

    def __init__(self, iface, baudrate=115200, _mode='b'):
        print("##LibFTDI_Wrap::init baudrate:%d mode=%s" % (baudrate, _mode))
        ##Use binary mode! ('b')
    
        self.dev = pylibftdi.Device(mode=_mode, interface_select=pylibftdi.INTERFACE_B)
        self.mode = _mode
        self.dev.baudrate = baudrate
        self.rx_poll_n=10
        self.rx_timeout_s=1
        self.read_size = 128
        self.default_read_chunk_size=128
        self.verbose=1
        self.tx_ex_raise_except = False

    def find_b(self, buff, contain_s=1):
        """Performs logical equivalent of str.find, on bytes using reg-ex"""
        
        if (type(buff) == str):
            buff=str.encode(buff, 'utf-8')
        if (type(contain_s) == str):
            contain_s=str.encode(contain_s, 'utf-8')
        
        m = re.compile(re.escape(contain_s))
        r=m.search(buff)
        if r == None:
            return -1
        else:
            return r.start()

    def tx(self,msg):
       
        ##Tx:string passed msg as string, convert to bytes as convenience
        if type(msg) == str:
            msg=str.encode(msg, 'utf-8') 
        #out_b=msg

        if (self.verbose):
            for l in (hexdump.hexdump(msg,'generator')):
                print("##Tx(%03d)--: %s" % ( len(msg),l))
            
        ret = self.dev.write(msg)
        if (ret != len(msg)):
            raise FTDIWrap_Err('write', ret, len(msg))
    
        return ret

    def rx(self, secs=None, n=None):
        if (secs == None):
            secs=self.rx_timeout_s
        if (n == None):
            n=self.default_read_chunk_size
            print("##QQ default read size %d enabled" %(n))
        else:
            print("##Rx::n_bytes=%d" %(n))
        poll_time =secs / self.rx_poll_n
     
        ret_b = bytes()
        bytes_left_to_read = n
        # poll the device at most rx_poll_n times
        for i in range(0, self.rx_poll_n):
            t = self.dev.read( min(self.default_read_chunk_size, bytes_left_to_read))
            ret_b += t
            bytes_left_to_read -= len(t)
            if (bytes_left_to_read == 0):
                print("##RX !! limit rx bytes hit. returning")
                #ex_buff = self.dev.read(self.default_read_chunk_size)
                #print("##There are %d to many bytes dequeued" % (len(ex_buff)))
                #print("## XX %s" % (repr(ex_buff)))
                break
            if (bytes_left_to_read < 0):
                raise(FTDIWrap_Err('RX_Overflow', ret, len(msg)))
            time.sleep(poll_time)

        if (self.verbose):
            for l in (hexdump.hexdump(ret_b,'generator')):
                print("##Rx(%03d)--: %s ##"  % (len(ret_b), l))

        return ret_b



    def expect(self, match, timeout=1):
        """reads out buffered input, returns True if match contained in input"""
        rx_buff = self.rx(secs=timeout)
        r=self.find_b(rx_buff, match)
        return r

    def tx_ex(self, tx_s, ex_s):
        self.tx(tx_s)
        r_buff = self.rx(1, len(ex_s))
        
        ret = self.find_b(r_buff, ex_s)
        if (ret == -1 and self.tx_ex_raise_except):
            raise FTDIWrap_Err('tx_ex::', r_buff, ex_s)
        return ret
def synchronize(self):
    # Detect baud rate
    self.tx('?')

    # Wait for 'Synchronized\r\n'
    self.rx(b'Synchronized')

    # Reply 'Synchronized\r\n'
    ftdw.tx('Synchronized\r\n')

    # Verify 'Synchronized\rOK\r\n'
    ftdw.rx('Synchronized\rOK\r\n')

    # Set a clock rate (value doesn't matter)
    ftdw.tx("12000\r\n")

    # Verify OK
    res = ftdw.rx('12000\rOK\r\n')
    print("%s" %(res))

if __name__ == "__main__":
    print("##ftdi_tx_rx: main")
    D = LibFTDI_wrap(pylibftdi.INTERFACE_B, 115200)
    D.tx(b'All your base are belong to us!')
    s=D.rx()
    print("##")
    print("## %s: "% (s.decode()))
    #synchronize(D)
