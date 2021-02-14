from . import ports
from . import _display
from ._display import display
from . import drivers

def deinit():
    ports.deinit()
    _display.deinit()
    drivers.deinit()
    
