#

import pathlib

with open("original.dec", "rb") as f:
    bl2_package = f.read(0xC000)
    fip = f.read()

with open("parts/bl2.package", "wb") as f:
    f.write(bl2_package)

with open("parts/fip", "wb") as f:
    f.write(fip)

with open("../../u-boot/u-boot.bin", "rb") as f:
    bl33_new = f.read()

def upper_16K(num):
    count, remain = divmod(num, 0x4000)
    if (remain):
        return 0x4000 * (count + 1)
    else:
        return num

def to_16K(num):
    remain = num % 0x4000
    if (remain):
        return 0x4000 - remain
    else:
        return 0

def from_u64(array, offset):
    return int.from_bytes(array[offset:offset+8], "little", signed=False)

offset_bl33 = from_u64(fip, 0x98)
size_bl33_old = from_u64(fip, 0xA0)
size_bl33_new = len(bl33_new)
size_bl33_pad = to_16K(size_bl33_new)

fip_new = fip[:0xA0] + size_bl33_new.to_bytes(8, "little", signed=False) + fip[0xA8:offset_bl33] + bl33_new + b'\0' * size_bl33_pad

with open("parts/fip_new", "wb") as f:
    f.write(fip_new)

with open("with_mainline", "wb") as f:
    f.write(bl2_package)
    f.write(fip_new)