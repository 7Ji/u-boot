# Bootloader modification for mibox3/3c (MDZ-16-AA)
## Unsign
```
unamlbootsig original original.dec
```
 - `unamlbootsig` is provided by [meson-tools]
 - `original` is usually `bootloader.PARTITION` in the burning image

## Replace FIP
```
mkdir parts
python new_fip.py
```
 - `u-boot.bin` should be stored as `../../u-boot/u-boot.bin` (or you can modify the python script)
 - `parts` folder exists in current work directory
 - out bootloader image is `with_mainline`

## Resign
```
amlbootsig with_mainline with_mainline.enc
```
 - `amlbootsig` is provided by [meson-tools]
 - replace `bootloader.PARTITION` in your burning image with `with_mainline.enc`
 - `with_mainline.enc` should be written to eMMC with offset 0 (unlike post-GXL SoCs with 512Byte offset)



[meson-tools]: https://github.com/afaerber/meson-tools