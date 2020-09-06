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
        ret = "FTDIWrap Error: %s"
        if (self.retval):
            ret += "returned: %d" % (self.retval)
        if (self.expected_retval):
            ret += " (expected %d)" %(self.expected_retval)
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
        self.debug=1


    def tx(self,msg):
       
        ##Tx:string passed msg as string, convert to bytes as convenience
        if type(msg) == str:
            msg=str.encode(msg, 'utf-8') 
        #messages are passed to libftdi in TLV format: prepend length
        out_b = struct.pack('B',len(msg)) + msg 
        for l in (hexdump.hexdump(out_b,'generator')):
            print("##Tx: %s" % (l))
        
        ret = self.dev.write(out_b)
        if (ret != len(out_b)):
            raise FTDIWrap_Err('write', ret, len(out_b))
    
        return ret

    def rx(self, secs=None):
        if (secs == None):
            secs=self.rx_timeout_s
        ret_b = bytes()
        # poll the device at most rx_poll_n times, or secs
        sleep_val=secs / self.rx_poll_n
        for i in range(0, self.rx_poll_n):
            time.sleep(sleep_val)
            t = self.dev.read(self.read_size)
            if len(t) > 0:
                ret_b += t
                print("##Rx(%d/%d): (%d:%d)" % (i, self.rx_poll_n, len(t), len(ret_b)))
        
        for l in (hexdump.hexdump(ret_b,'generator')):
            print("##Rx: %s" % (l))
        return ret_b

        
 
    



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
