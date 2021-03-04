# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from ._imple import *

# from tg_gui_core.pages import Pages
import gc


class DisplayioScreen(Screen):

    _nest_count_override = 1

    def __init__(self, *, display, **kwargs):
        self._display_ = display
        self._root_ = None
        if not isinstance(display, displayio.Display):
            raise TypeError(
                f"screen must be of type 'Display', found '{type(self).__name__}'"
            )
        super().__init__(**kwargs)

        self._selectbles_ = []
        self._pressables_ = []
        self._updateables_ = []

    def on_widget_nest_in(_, wid: Widget):
        if not hasattr(wid, "_group"):
            wid._group = None

    def on_widget_unnest_from(_, wid: Widget):
        if hasattr(wid, "_group"):
            del wid._group

    def on_widget_render(self, wid: Widget):
        if wid._group is not None:
            sgroup = wid._superior_._group
            group = wid._group
            wid._superior_._group.append(group)

        if hasattr(wid, "_selected_"):
            self._selectbles_.append(wid)
        if hasattr(wid, "_press_"):
            self._pressables_.append(wid)
        if hasattr(wid, "_update_coord_"):
            self._updateables_.append(
                wid,
            )

    def on_widget_derender(self, wid: Widget):
        if wid._group is None:
            pass
            # while wid._group in wid._superior_._group:
        else:
            wid._superior_._group.remove(wid._group)

        if wid in self._selectbles_:
            self._selectbles_.remove(wid)
            if wid in self._selectbles_:
                raise RuntimeError(f"double _selectbles_ error {wid}")

        if wid in self._pressables_:
            self._pressables_.remove(wid)
            if wid in self._pressables_:
                raise RuntimeError(f"double _pressables_ error {wid}")

        if wid in self._updateables_:
            self._updateables_.remove(wid)
            if wid in self._updateables_:
                raise RuntimeError(f"double _updateables_ error {wid}")

    def on_container_render(_, wid: Widget):
        if hasattr(wid, "_nest_count_override"):
            wid._group = Group(
                x=wid._rel_x_,
                y=wid._rel_y_,
                max_size=wid._nest_count_override,
            )
        else:
            wid._group = Group(
                x=wid._rel_x_,
                y=wid._rel_y_,
                max_size=max(
                    1,
                    len(wid._nested_),
                ),
            )
        wid._screen_._root_.refresh_whole()

    def on_container_derender(_, wid: Widget):
        del wid._group
        wid._group = None

    def on_widget_show(_, wid: Widget, _full_refresh=False):
        pass
        if _full_refresh:
            wid._screen_._root_.refresh_whole()

    def on_widget_hide(_, wid: Widget):
        pass
        # if isinstance(wid, Pages):
        #     wid._screen_._root_.refresh_whole()


class DisplayioRootWrapper(RootWrapper):
    def __init__(self, *, display, screen, **kwargs):
        # assert isinstance(display, displayio.Display)
        self._display = display
        display.auto_refresh = False

        if not isinstance(screen, DisplayioScreen):
            raise TypeError(
                f"screen must be of type 'DisplayioScreen', found '{type(screen).__name__}'"
            )

        super().__init__(screen=screen, **kwargs)

        self._group = group = Group(max_size=1)  # only has one child
        self.refresh_whole = lambda: None
        screen._root_ = self

    def _std_startup_(self):
        super()._std_startup_()
        self._display.show(self._group)
        self.refresh_whole = self._refresh_whole

    def _refresh_whole(self):
        self._display.show(None)
        self._display.show(self._group)
        self._display.refresh()
