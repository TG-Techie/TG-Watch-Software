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

debug_file = const(0)  # 0 for false, 1 for true


class DisplayioScreen(Screen):

    _nest_count_override = 1

    def __init__(self, *, display, **kwargs):
        if not isinstance(display, displayio.Display):
            raise TypeError(
                f"screen must be of type 'Display', found '{type(self).__name__}'"
            )
        super().__init__(**kwargs)

        self._display_ = display
        self._root_ = None

        self._selectbles_ = []
        self._pressables_ = []
        self._updateables_ = []

    def on_widget_nest_in(_, widget: Widget):
        pass

    def on_widget_unnest_from(_, widget: Widget):
        pass

    def on_widget_build(self, widget: Widget):
        if not hasattr(widget, "_group"):
            widget._group = None

    def on_widget_demolish(self, widget: Widget):
        if hasattr(widget, "_group"):
            del widget._group

    def on_widget_show(self, widget: Widget):
        if debug_file:
            print(f"on_widget_show(_, {widget}): ", end="")
        # link into this implenations version of pressing
        if hasattr(widget, "_selected_"):
            if debug_file:
                print("selectable", end=" ")
            self._selectbles_.append(widget)
        if hasattr(widget, "_press_"):
            if debug_file:
                print("pressable", end=" ")
            self._pressables_.append(widget)
        if hasattr(widget, "_update_coord_"):
            if debug_file:
                print("update-coord", end=" ")
            self._updateables_.append(
                widget,
            )
        if debug_file:
            print()
        # show the widget on the screen by adding it to the element tree
        if widget._group is not None:
            # print(widget, widget._superior_, widget._superior_._group)
            widget._superior_._group.append(widget._group)

    def on_widget_hide(self, widget: Widget):
        # if it is on the screen, remove it
        if widget._group in widget._superior_._group:
            widget._superior_._group.remove(widget._group)

        # remove this wqidget form this platofroms ui interaction
        if widget in self._selectbles_:
            self._selectbles_.remove(widget)
            if debug_file and widget in self._selectbles_:
                raise RuntimeError(f"double _selectbles_ error {widget}")

        if widget in self._pressables_:
            self._pressables_.remove(widget)
            if debug_file and widget in self._pressables_:
                raise RuntimeError(f"double _pressables_ error {widget}")

        if widget in self._updateables_:
            self._updateables_.remove(widget)
            if debug_file and widget in self._updateables_:
                raise RuntimeError(f"double _updateables_ error {widget}")

    # container tie-ins
    def on_container_build(_, widget: Widget):
        if hasattr(widget, "_nest_count_override"):
            group_size = widget._nest_count_override

        else:
            group_size = len(widget._nested_)

        rel_x, rel_y = widget._rel_coord_
        widget._group = Group(
            x=rel_x,
            y=rel_y,
            max_size=group_size,
        )
        # widget._screen_._root_.refresh_whole()

    def on_container_demolish(_, widget: Widget):
        del widget._group
        widget._group = None

    def on_container_show(_, widget: Widget, _full_refresh=False):
        # print(
        #     widget,
        #     widget._full_refresh_
        #     if hasattr(widget, "_full_refresh_")
        #     else "does not have",
        # )
        if hasattr(widget, "_full_refresh_") and widget._full_refresh_ is True:
            widget._screen_._root_.refresh_whole()

    def on_container_hide(_, widget: Widget):
        pass
        # if hasattr(widget, "_full_refresh_") and widget._full_refresh_ is True:
        #     widget._screen_._root_.refresh_whole()

    def widget_is_built(_, widget: Widget):
        # print(f"widget_is_built(_, {widget}) -> widget._group={widget._group}")
        return widget._group is not None


class DisplayioRootWrapper(Root):
    def __init__(self, *, display, screen, size, **kwargs):
        # assert isinstance(display, displayio.Display)
        if not isinstance(screen, DisplayioScreen):
            raise TypeError(
                f"screen must be of type 'DisplayioScreen', found '{type(screen).__name__}'"
            )

        super().__init__(screen=screen, size=size, **kwargs)

        self._display = display
        display.auto_refresh = False

        self.refresh_whole = lambda: None
        screen._root_ = self

    def _std_startup_(self):
        super()._std_startup_()
        self._display.show(self._group)
        self.refresh_whole = self._refresh_whole

    def _refresh_whole(self):
        # print(f"!!refreshsing whole: {self}")
        # make the retire tree for re-rendering
        self._display.show(None)
        self._display.show(self._group)

    def _show_(self):
        super()._show_()
        assert self._group is not None
        self._display.show(self._group)

    def _hide_(self):
        super()._hide_()
        self._display.show(None)
