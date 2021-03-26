from hardware import display
from hardware.drivers import touchscreen, rtc
from . import splash_screen

from tg_gui_core import *

splash_screen.update_progress(0.65)
from tg_gui_std.all import *
from tg_gui_platform.event_loops import SinglePointEventLoop
from tg_gui_platform.root_wrapper import DisplayioRootWrapper, DisplayioScreen

splash_screen.update_progress(0.70)

default_theme = Theme(
    margin=6,
    radius=240 // 8,
    border=3,
    plain=Palette(
        # layers
        foregnd=0xD2D2D2,
        pregnd=0xB0B0B0,
        midgnd=0x9B9B9B,
        postgnd=0x636363,
        backgnd=0x000000,
        # texts
        foretext=0x303030,
        pretext=0x606060,
        midtext=0x909090,
        posttext=0xC4C4C4,
        text=0xFFFFFF,
        # accents
        accent=0x9B9B9B,
        accenttext=0xFFFFFF,
        active=0x636363,
        activetext=0xD2D2D2,
    ),
    action=SubPalette(
        theme.plain,
        accent=0x20609F,
        active=0x7FFFFF,
        accenttext=0xFFFFFF,
        activetext=0x000000,
        text=0x70F0F0,
    ),
    warning=SubPalette(
        theme.plain,
        accent=0xFFC900,
        active=0xD2D2D2,
        accenttext=0x909090,
        activetext=0xFFC900,
        text=0xFFC900,
    ),
    alert=SubPalette(
        theme.plain,
        accent=0xFF2922,
        active=0xD2D2D2,
        accenttext=0xFFFFFF,
        activetext=0xC80000,
        text=0xFF2922,
    ),
    # indicator=SubPalette(
    #     accent=0x9B9B9B,
    #     active=0x7EC636,
    #     accenttext=0xFFFFFF,
    #     activetext=0x000000,
    # ),
    label_style=LabelStyle(
        theme.plain,
        text=palette.text,
        alignment=align.center,
        font=font.label,
    ),
    button_style=ButtonStyle(
        theme.action,
        fill=palette.accent,
        text=palette.accenttext,
        selected_fill=palette.active,
        selected_text=palette.activetext,
        font=font.label,
        radius=theme.radius,
        alignment=align.center,
    ),
    slider_style=SliderStyle(
        theme.action,
        bar=palette.accent,
        knob=palette.foregnd,
        knob_border=palette.midgnd,
        bar_thickness=theme.min_visible,
        border_thickness=theme.border,
        radius=ratio(height // 2),
    ),
)

screen = DisplayioScreen(
    layout_class=layout_class.wearable,
    display=display,
    min_size=240 // 4,
    min_visible=8,
    min_margin=5,
    border=4,
    # radius=240 // 8,
    theme=default_theme,
)


def get_touch_coord():
    global touchscreen
    if touchscreen.touched:
        point_dict = touchscreen.touches[0]
        return (
            int(240 * point_dict["x"] / 300),
            int(240 * point_dict["y"] / 300),
        )
    else:
        return None


event_loop = SinglePointEventLoop(screen=screen, poll_coord=get_touch_coord)

display.refresh()
splash_screen.update_progress(1.0)
