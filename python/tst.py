"""
    Script to test serial devices
"""
#import os
#from time import sleep
import pylibftdi
from ftdiwrap import LibFTDI_wrap


import ftdiwrap
S=b'All your base are belong to us!!!\r\n'
D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 115200)
D.tx(S)

res=D.rx()
