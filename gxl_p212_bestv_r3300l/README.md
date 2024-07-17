# Bootloader modification for r3300l

## FIP extraction

For the best effort, it's recommended to extract FIP from the original Android image. 

### From Amlogic USB burning image

For ease of obtaining though, you can extract from https://github.com/7Ji/u-boot/releases/download/v2023.01-r3300l/r3300l-milton-bare.img

using `ampack` from https://github.com/7Ji/ampack to unpack the Amlogic USB burning image
```
ampack unpack r3300l-milton-bare.img unpacked
```
This FIP image would be `unpacked/bootloader.PARTITION`

### From eMMC

If your box is running Android, you can extract FIP from the eMMC user hwpartition, by dumping the first 4M after the initial 512 block (reserved for MBR) from the corresponding block device
```
adb shell dd if=/dev/mmcblkN of=/sdcard/fip bs=512 skip=1 count=8191
adb pull /sdcard/fip fip
```

Be sure you dumped from the right block device (the one with boot0 and boot1 companions). For generic Linux scenarios dd directly without adb pulling.


#### Special case: FIP on boot hwpartition

For SoCs since GXL family, it's possible to store FIP on eMMC boot hwpartition (those listed as mmcblkNboot0 and mmcblkNboot1) rather than the user hwpartition. However this is never used by any stock Amlogic Android image or third party Linux images. If this is the case (like on my tinkered box), dump from the corresponding `boot0` or `boot1` block device instead.

## FIP Decryption

using `gxlimg` from https://github.com/repk/gxlimg to extract all BL parts from FIP

_Note: the tool has a naive bug that returns the result of `snprintf` (non-zero), which would result in bad exit when it actually succeeded, apply [my patch](./0001-fip-gi_fip_extract_bl3x-fix-non-zero-return-code-on-.patch) before building if that annoys you_

```
mkdir fip-parts
gxlimg --extract unpacked/bootloader.PARTITION fip-parts
```

The output folder would contain the following members:

```
> ls fip-parts/
bl2.sign  bl301.enc  bl30.enc  bl31.enc  bl33.enc  fip  fip.enc
```

## BL33 Building

Build your own u-boot from the mainline codebase, using either `p212` config in mainline repo, or `r3300l` from `random-boxes` here

Let's assume you have built `u-boot.bin`. Make sure you can `go` to it from the existing u-boot onboard.

## BL33 encryption

using `gxlimg` to encrypt u-boot binary (assume `u-boot.bin` is at `../u-boot.bin`)
```
gxlimg --type bl3x --encrypt ../u-boot.bin bl33.enc
```

This would replace the BL33 with our own

## FIP repack

using `gxlimg` to repack the parts into a FIP image

```
gxlimg --type fip --bl2 bl2.sign --bl30 bl30.enc --bl301 bl301.enc --bl31 bl31.enc --bl33 bl33.bin ../new-fip.img
```

## FIP writing

The FIP image `new-fip` shall be stored at either one of the following places:
- eMMC user hwpartition (`mmcblkN`)
- eMMC boot hwpartition 1 (`mmcblkNboot0`)
- eMMC boot hwpartition 2 (`mmcblkNboot1`)

with 512 offset (reserved for MBR), thus it would conflict with GPT but not MBR. Be sure you only create MBR partition table if you do write it to eMMC user partition.

**Special note: If you're using amlogic-boot-fip and got `u-boot.bin.sd.bin`, then you do not need the initial 512 offset, as the image already contains that**

E.g. to write to eMMC user hwpartition:
```
sudo dd if=new-fip.img of=/dev/mmcblkN bs=512 seek=1
```

E.g. to write to eMMC boot hwpartition 1:
```
echo 0 | sudo tee /sys/block/mmcblkNboot0/force_ro 
sudo dd if=new-fip.img of=/dev/mmcblkNboot0 bs=512 seek=1
```

The lookup order for FIP is user hw partition -> boot hwpartition 1 -> boot hw partition 2, be sure to erase the earlier targets if your target is later.