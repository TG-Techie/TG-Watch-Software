# from . import ports
# from . import _display
# from ._display import display
from . import drivers

drivers.init()

from .drivers import display


def deinit():
    drivers.deinit()
