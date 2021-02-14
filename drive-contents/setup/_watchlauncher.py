from tg_gui_platform.all import *
from system.applocals import *


import time
import system
import os
import json

from .appview import app_view

print("loading apps")

import displayio


class Image(Widget):
    def __init__(self, *, path, size, **kwargs):
        super().__init__(**kwargs)
        self._path = path
        self._size = size

    def _place_(self, coord, dims):
        super()._place_(coord, dims)
        self._image_file = image_file = open(self._path, "rb")
        self._layer = layer = displayio.OnDiskBitmap(image_file)
        # p = displayio.Palette(10)
        # p[2] = 0xFF0000
        # p[3] = 0x00FF00
        # p[4] = 0xFF00FF
        image_width, image_height = self._size
        x, y, width, height = self._rel_placement_
        self._group = displayio.TileGrid(
            layer,
            x=x + width // 2 - image_width // 2,
            y=y + height // 2 - image_height // 2,
            pixel_shader=displayio.ColorConverter(),
        )
        # p.make_transparent(0)

    def _pickup_(self):
        del self._group, self._layer, self._image_file
        self._group = None
        super()._pickup_()


class LaunchWidget(Layout):
    def __init__(self, *, widget, title, path, **kwargs):
        self._widget = widget
        self._title = title
        self._title_src = State(title)
        self._path = path
        super().__init__(**kwargs)

    def _press_(self):
        global app_view
        app_view.load_app(self._path)
        app_view.open_view()

    @property
    def title(self):
        return self._title

    def _setup_(self):
        self._label = Label(text=self._title_src, size=1)

    def _on_nest_(self):
        self._nest_(self._widget)
        self._nest_(self._label)
        # self._nest_(self._image)

    def _any_(self):
        widget = self._widget((center, top), (90, 90))
        self._label(below(widget), (self.width, self.height - 90))

    _selected_ = None

    def _select_(self):
        self._title_src.update(f"<{self._title}>")

    def _deselect_(self):
        self._title_src.update(self._title)

    @classmethod
    def frominfo(cls, path, info):
        title = info["title"]
        iconinfo = info["icon"]
        kind = iconinfo["kind"]
        if kind == "index-bitmap":
            iconpath = f"{path}/{iconinfo['path']}"
            widget = Image(path=iconpath, size=(85, 85))
        elif kind == "text":
            widget = Rect(margin=3)
        else:
            raise ValueError(f"unknown icon format {repr(kind)}")

        del info

        return cls(
            widget=widget,
            path=path,
            title=title,
        )


class LauncherPage(Layout):
    _placements = (
        (left, top),
        (right, top),
        (left, bottom),
        (right, bottom),
    )

    def __init__(self, launch_widgets, **kwargs):
        self._launch_widgets = launch_widgets
        super().__init__(**kwargs)

    def _on_nest_(self):
        self._widgets = widgets = []
        for launch_widget in self._launch_widgets:
            self._nest_(launch_widget)
            widgets.append(launch_widget)

    def _any_(self):
        # size = (self.width // 2, self.height // 2)
        x, y = self.width // 4 - 85 // 2, self.height // 4 - 85 // 2
        size = (self.width // 2, self.height // 2)
        placements = (
            (left, top),  # (x, 0),
            (right, top),  # (-x, 0),
            (left, bottom),  # (x, -y),
            (right, bottom),  # (-x, -y),
        )
        for widget, location in zip(self._widgets, placements):
            widget._place_(location, size)


apps = {}
appfolders = os.listdir("/apps")
for app in appfolders:
    if app.startswith("_"):
        pass
    else:
        with open(f"/apps/{app}/info.json") as file:
            try:
                info = json.load(file)
            except:
                print(f"unable to load app info {file(file)}")
                continue
            launch_widget = LaunchWidget.frominfo(f"/apps/{app}", info)
            apps[app] = launch_widget
# print(apps)

launch_widgets = list(apps.values())
launch_widgets.sort(key=lambda item: item.title)

launch_page_groups = []
while len(launch_widgets):
    # launch_pages.append(LauncherPage(appinfos=launch_widgets[0:4]))
    launch_page_groups.append(tuple(launch_widgets[0:4]))
    launch_widgets = launch_widgets[5:]

# launch_pages = tuple(launch_pages)
# print(launch_pages)
# singleinstance = lambda cls: cls()


@singleinstance
class default_launcher(Layout):
    def _setup_(self):
        self._launch_pages = launch_pages = []
        if len(launch_page_groups) == 0:
            page_group.append(Widget())
        else:
            for page_group in launch_page_groups:
                launch_pages.append(LauncherPage(page_group))
        self._portpage = portpage = PageState(0)
        self._port = Pages(show=portpage, pages=self._launch_pages)

    def _on_nest_(self):
        self._nest_(self._port)

    def _wearable_(self):
        # back = self.back((left, top), (self.width // 2, self.height // 6))
        # prev = self.prev((left, bottom), (self.width // 2, self.height // 5))
        # self.next((right, bottom), (self.width // 2, self.height // 5))
        self._port((left, top), self.dims)
