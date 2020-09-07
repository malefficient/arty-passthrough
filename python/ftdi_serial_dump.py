"""
    Simple read-only hex-dumper
"""
import pylibftdi
from ftdiwrap import LibFTDI_wrap
D=LibFTDI_wrap(pylibftdi.INTERFACE_B, 9600)
D.verbose = True
while (True):
    D.rx(333)
