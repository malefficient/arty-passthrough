#!/usr/bin/python
##crp_patcher.py: Simple python script to manually patch CRP values into LPC1343 firmware

import sys, struct
magic_nums={0x12345678: 'CRP1', 0x87654321: 'CRP2', 0x43218765: 'CRP3', 0x00000000: 'CRP_DISABLED', 0x4E697370:'NO_ISP'}

if len(sys.argv) <= 1:
    print("Usage: crp_patcher.py firmware.bin [CRP_DISABLED|NO_ISP|CRP1|CRP2|CRP3]")
    sys.exit(0)

infile = open(sys.argv[1], "r+b")
infile.seek(0x2FC)
crp = struct.unpack("<I", infile.read(4))[0]
infile.close()
if not crp in magic_nums.keys():
    print("%s: Warning:  CRP value present in %s un-recognized: 0x%08x" % (sys.argv[0], sys.argv[1], crp))
else:
    print("Current CRP value (%s): 0x%08x '%s'" % ( sys.argv[1], crp, magic_nums[crp]))

if len(sys.argv)<3:
    sys.exit(0)

opt = sys.argv[2]
crp=None
for k,v in magic_nums.items():
    if (v == opt):
        crp = k
if (crp == None):
    print("Error: Specified CRP not recognized: %s"%(opt))
    sys.exit(-1)

infile = open(sys.argv[1], "r+b")
infile.seek(0x2FC)
infile.write(struct.pack("<I", crp))
infile.close()
print("New CRP value 0x%08x '%s' written" % (crp, opt))
 
