import busio
import board

import displayio
displayio.release_displays()

def deinit():
    try: i2c.deinit()
    except: pass

    try: spi.deinit()
    except: pass


try:
    i2c = board.I2C()
    spi = board.SPI()
except Exception as err:
    deinit()
    raise err
