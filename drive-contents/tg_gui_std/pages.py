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

import gc

from tg_gui_core.stateful import State
from tg_gui_core.base import Container, Widget
from tg_gui_core.attribute_specifier import AttributeSpecifier
from tg_gui_core.constant_groups import ConstantGroup

# PageState shoud either have two modes ot two classes with a __new__ method
# IndexedPageState(0) and IdentityPageState(self.attr)
# each's __get__ retun eh appropriate type and can only the the apropriat type
# See if Pages is able to use _nested_ as the index value
# remeber taht the__get__ and __set__ will be used by a Layout and not the Pages itself
#


class PageState(State):
    pass


class Pages(Container):
    """
    Pages has two modes of initing
    - Single instance classes
    - Widget instances

    Single incstance classes are similar to Single instance `Layout` Classes,
    subclass `Pages` and set the sub-pages as class attributes:
    ```python
    class my_pages(Pages):
        page = PageState(0)

        page1 = WidgetTypeForPage1()
        page2 = WidgetTypeForPage3()
        page3 = WidgetTypeForPage3()
    ```

    Widget instances are created by calling `Pages(show=..., pages=...)` where
    show is a PageState object and pages is a tuple of Widget (to use as pages).

    You can make re-usbale, pages widgets by subclassing `Pages` and modifying
    __init__ and passing the pages argument to `super().__init__(...)`.
    """

    def __init__(self, show=None, pages=None, _hot_rebuild=False):
        super().__init__()

        # determin if is called, declared, or invalid
        was_declared = show is None and pages is None
        was_called = show is not None and pages is not None

        if was_declared:
            # find the decalred pages
            show, pages = self._scan_class_for_pages()

        elif was_called:
            assert isinstance(show, State), (
                f"when calling {type(self).__name__} the 'show' argumetn must "
                + "be a state or PageState object"
            )
            assert isinstance(pages, tuple) and len(pages), (
                f"when calling {type(self).__name__} the 'pages' argumetn must "
                + "a tuple with one or more widgets"
            )
        else:
            raise TypeError(
                f"{self} incorrectly inited, Pages must be called with a state "
                + "object and a tuple of pages or subclasses and declared "
                + "with @singleinstance"
            )

        self._state = show
        self._pages = pages
        self._current_page = None
        self._hot_rebuild = _hot_rebuild

    def _on_nest_(self):
        for widget in self._pages:
            self._nest_(widget)

    def _format_(self, pos_spec, dim_spec):
        super(Container, self)._format_(pos_spec, dim_spec)
        size = self._size_
        for widget in self._pages:
            widget._format_((0, 0), size)

    def _build_(self):
        super(Container, self)._build_()
        if not self._hot_rebuild:
            for widget in self._pages:
                widget._build_()

    def _show_(self):
        super(Container, self)._show_()
        self._current_page = to_show = self._pages[self._state.value()]
        to_show._build_()
        to_show._show_()

    def _hide_(self):
        self._current_page._hide_()
        if self._hot_rebuild:
            self._current_page._demolish_()
        self._current_page = None
        super(Container, self)._hide_()

    def _switch_page(self, index):
        self._current_page._hide_()
        if self._hot_rebuild:
            self._current_page._demolish_()
        self._current_page = to_show = self._pages[index]
        if self._hot_rebuild:
            to_show._build_()
        to_show._show_()

    @classmethod
    def _scan_class_for_pages(cls):

        # see if the user added a page class attribute(attr)
        if hasattr(cls, "page"):
            state = cls.page
        else:
            raise TypeError(
                f"no page stae object declared in {cls}, add `page = State(0)` "
                + "to  the body"
            )

        attrs = [getattr(cls, name) for name in dir(cls)]
        found_pages = []
        for attr in attrs:
            if isinstance(attr, Widget):
                found_pages.append(attr)
            elif isinstance(attr, type) and issubclass(attr, Widget):
                raise TypeError(
                    f"type {attr} found in the body of {cls}, this is not a "
                    + "valid declaration. did you mean to decorate it "
                    + "with @singleinstance"
                )
            else:
                pass
        found_pages.sort(key=lambda widget: widget._id_)
        return state, tuple(found_pages)
        # page = show
        # # scan for class attrs
        # if pages is None and page is None:  # if called
        #     cls = type(self)
        #     pageattrs = []
        #     for attrname in dir(cls):
        #         attr = getattr(cls, attrname)
        #         if isinstance(attr, Widget):
        #             pageattrs.append(attr)
        #             # pages[attr] = attr
        #         elif isinstance(attr, type) and issubclass(attr, Widget):
        #             # pageattrs.append(attr())
        #             raise TypeError(
        #                 f"{type(self)} has a class as an attribute, "
        #                 + f"this is not poeritted. found {attr}"
        #             )
        #         else:
        #             pass
        #     else:
        #         pageattrs.sort(key=lambda item: item._id_)
        #         pages = {index: widget for index, widget in enumerate(pageattrs)}
        #     if show is None:
        #         if hasattr(cls, "page"):
        #             show = getattr(cls, "page")
        #             assert isinstance(show, PageState), f"found {show}"
        #         else:
        #             raise TypeError(
        #                 f"{cls} has no attribute page, a `Pages` subclass must "
        #                 + "have a `.page` attribute. `page = PageState(0)`"
        #             )
        #         # find the widget with the lowest id (as they are chronological)
        #         # show = State(0)
        #     else:
        #         raise TypeError(
        #             "when 'pages' is not specified show must not be either, "
        #             + f"found {show}"
        #         )
        # elif isinstance(pages, (tuple, list)):
        #     pages = dict(enumerate(pages))
        # elif isinstance(pages, dict):
        #     pass
        # else:
        #     raise TypeError(
        #         "argument pages must be a tuple, dict, or None, "
        #         + f"found {type(self)}"
        #     )
        #
        # if _hot_rebuilded is None and hasattr(self, "_hot_rebuilded_"):
        #     self._hot_rebuilded = self._hot_rebuilded_
        # else:
        #     self._hot_rebuilded = _hot_rebuilded
        #
        # self._page_key_src = show
        # self._pages = pages
        # self._page_key = None


# _PageStateModes = ConstantGroup("PageStateMode", ("key", "page_widget"))
#
#
# class PageState(State):
#
#     mode = _PageStateModes
#
#     def __init__(self, arg, mode=_PageStateModes.key, **kwargs):
#         super().__init__(arg, **kwargs)
#         self._mode = mode
#
#     def __get__(self, owner: object, ownertype: type):
#         global _PageStateModes
#         mode = self._mode
#         if mode is _PageStateModes.key:
#             return super().__get__(owner, ownertype)
#         elif mode is _PageStateModes.page_widget:
#             return owner._pages[super().__get__(owner, ownertype)]
#         else:
#             raise TypeError(
#                 f"cannot use {mode} for a PageState mode, "
#                 + "only PageState.mode.key or PageState.mode.page"
#             )
#
#     def __set__(self, owner, value):
#         global Pages
#         # print(f"{owner}.__set__ : {self} = {value}")
#         is_page_inst = isinstance(value, Widget)
#         # is_page_type = isinstance(value, type) and issubclass(value, Widget)
#         if is_page_inst:
#             for page_key, page_inst in owner._pages.items():
#                 if value is page_inst:
#                     value = page_key
#         self.update(value)
#
#
# class Pages(Container):
#
#
#     def set_page(self, value):
#         if isinstance(value, AttributeError):
#             value = value._get_attribute_(self)
#         self._page_key_src.update(value)
#
#     def _on_nest_(self):
#         for page in self._pages.values():
#             self._nest_(page)
#
#     def _place_(self, coord, dims):
#         Widget._place_(self, coord, dims)
#         if self._hot_rebuilded is True:
#             for page in self._pages.values():
#                 page._place_((0, 0), self.dims)
#         self._screen_.on_container_place(self)
#
#     def _pickup_(self):
#         self._screen_.on_container_pickup(self)
#         for page in self._pages:
#             page._pickup_()
#         Widget._pickup_(self)
#
#     def _render_(self):
#         Widget._render_(self)
#
#         self._page_key_src._register_handler_(self, self._rerender_pages)
#         self._page_key = page_key = self._page_key_src.value()
#
#         page = self._pages[page_key]
#         if self._hot_rebuilded is False:
#             if not page.isplaced():
#                 page._place_((0, 0), self.dims)
#         page._render_()
#         self._screen_.on_container_render(self, _full_refresh=True)
#
#     def _derender_(self):
#         page = self._pages[self._page_key]
#         page._derender_()
#         # page._pickup_()
#         # gc.collect()
#         Widget._derender_(self)
#         self._screen_.on_container_derender(self)
#         self._page_key_src._deregister_handler_(self)
#
#     def _rerender_pages(self, page_key):
#         self._screen_.on_container_derender(self)
#         page = self._pages[self._page_key]
#         page._derender_()
#         # page._pickup_()
#         # gc.collect()
#         self._page_key = page_key  #  = self._page_key_src.value()
#         page = self._pages[page_key]
#         if self._hot_rebuilded is False:
#             if not page.isplaced():
#                 page._place_((0, 0), self.dims)
#         page._render_()
#         self._screen_.on_container_render(self, _full_refresh=True)
