"""
    Script to test serial devices
"""
import pylibftdi
from ftdiwrap import LibFTDI_wrap


import ftdiwrap
S=b'All your base are belong to us!!!\r\n'
D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 9600)
while (True):
    D.rx()