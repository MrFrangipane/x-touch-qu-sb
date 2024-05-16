"""Study of the XTouch XT using Reaper's CSI and a midi logger"""


# tp 15: MackieControl XT
# cm 12: Text
# cm 72: Color

#
# Meters
# xx 00 > 0D (clip: 0E) + offset de 32 par channel
# CC 13 ?
'D0 xx'

#
# Colors
'F0 00 00 66 tp cm s1 s2 s3 s4 s5 s6 s7 s8 F7'

# track 1
'F0 00 00 66 15 72 01 04 07 07 07 07 07 07 F7'  # red
'F0 00 00 66 15 72 04 04 07 07 07 07 07 07 F7'  # blue
'F0 00 00 66 15 72 03 04 07 07 07 07 07 07 F7'  # yellow

# track 2
'F0 00 00 66 15 72 03 01 03 07 07 07 07 07 F7'  # red
'F0 00 00 66 15 72 03 04 03 07 07 07 07 07 F7'  # blue
'F0 00 00 66 15 72 03 03 03 07 07 07 07 07 F7'  # yellow

# track 3
'F0 00 00 66 15 72 03 03 01 07 07 07 07 07 F7'  # red
'F0 00 00 66 15 72 03 03 04 07 07 07 07 07 F7'  # blue
'F0 00 00 66 15 72 03 03 03 07 07 07 07 07 F7'  # yellow

#
# Text
'F0 00 00 66 tp cm ps xx xx xx xx xx xx xx F7'

# track 1
'F0 00 00 66 15 12 00 61 20 20 20 20 20 20 F7'  # a on line 1
'F0 00 00 66 15 12 00 62 20 20 20 20 20 20 F7'  # b on line 1
'F0 00 00 66 15 12 38 20 20 20 31 20 20 3E F7'  # 1> on line 2
'F0 00 00 66 15 12 38 3C 20 20 31 20 20 20 F7'  # <1 on line 2

# track 2
'F0 00 00 66 15 12 07 61 20 20 20 20 20 20 F7'  # a on line 1
'F0 00 00 66 15 12 07 62 20 20 20 20 20 20 F7'  # b on line 1
'F0 00 00 66 15 12 3F 20 20 20 31 20 20 3E F7'  # 1> on line 2
'F0 00 00 66 15 12 3F 3C 20 20 31 20 20 20 F7'  # <1 on line 2

# track 3
'F0 00 00 66 15 12 0E 61 20 20 20 20 20 20 F7'  # a on line 1
'F0 00 00 66 15 12 0E 62 20 20 20 20 20 20 F7'  # b on line 1
'F0 00 00 66 15 12 46 20 20 20 31 20 20 3E F7'  # 1> on line 2
'F0 00 00 66 15 12 46 3C 20 20 31 20 20 20 F7'  # <1 on line 2


if __name__ == '__main__':
    import time
    import math

    import mido
    from mido.messages import Message

    def set_meter(offset, ch=0):
        val = int(math.cos(time.time() * 5 + offset) * 7 + 7)
        val += ch * 16
        port.send(Message.from_bytes(
            b'\xD0' + val.to_bytes()
        ))
        time.sleep(0.01)

    try:
        with mido.open_output('X-Touch-Ext 1') as port:
            while True:
                for i in range(8):
                    set_meter(i / 3.0, i)
    except KeyboardInterrupt:
        pass
