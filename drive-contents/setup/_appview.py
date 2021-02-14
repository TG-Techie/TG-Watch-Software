from tg_gui_platform.all import *
import gc

from runtime_importer import ModuleWrapper
from system import applocals


@singleinstance
class app_view(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._module = None

    def load_app(self, path):

        module_loaded = self._module is not None

        if module_loaded and path == self._module._wrapped_module_path_:
            return  # bail early, no action needed
        elif module_loaded:
            self._close_module()
        else:
            pass

        self._load_module(path)

    def close_app(self):

        if self._module is not None:
            self._close_module()

        gc.collect()
        print(f"app closed", gc.mem_free())

    def _load_module(self, path):
        assert self._module is None

        self._path = path

        gc.collect()
        self._module = module = ModuleWrapper(path)
        gc.collect()
        module._load_()

        app = module.Application
        # some of memory issue was somehwere in here START
        self._nest_(app)
        if self.isplaced():
            self._place_nested_()
        if self.isrendered():
            self._render_nested_()
        # END, that section has most likely been resolved

        gc.collect()
        print("_load_module:", repr(path), "mem_free=", gc.mem_free())

    def _close_module(self):
        assert self._module is not None

        current = self._loaded_app()

        self._module._clear_()
        del self._module
        self._module = None

        if current is not None:  # allow opt-out for laod fails
            if self.isrendered():
                self._derender_nested_()
            if self.isplaced():
                self._pickup_nested_()
            self._unnest_(current)
        del current
        gc.collect()

    def _loaded_app(self):
        if len(self._nested_):
            return self._nested_[0]
        else:
            return None

    def _app_is_loaded(self):
        return bool(self._loaded_app() is not None)

    def open_view(self):
        self._superior_.open_appview()

    def close_view(self):
        self._superior_.pop_view()

    def _place_nested_(self):
        if self._app_is_loaded():
            self._loaded_app()._place_((0, 0), self.dims)

    def _pickup_nested_(self):
        if self._app_is_loaded():
            self._loaded_app()._pickup_()

    def _render_nested_(self):
        if self._app_is_loaded():
            self._loaded_app()._render_()

    def _derender_nested_(self):
        if self._app_is_loaded():
            self._loaded_app()._derender_()


# class AppView(Layout):
#     def __init__(self, widget=None, **kwargs):
#         super().__init__(**kwargs)
#         if widget is None:
#             widget = Widget()
#         self._widget = widget
#
#     def _on_nest_(self):
#         self._nest_(self._widget)
#
#     def _place_(self, coord, dims):
#         Widget._place_(self, coord, dims)
#         self._screen_.on_container_place(self)
#         self._widget._place_((0, 0), self.dims)
#         self._widget = None
#
#     @property
#     def app(self):
#         raise AttributeError(f"cannot get the app nested in {self}, only set it")
#
#     @app.setter
#     def app(self, Application):
#         # assert isinstance(
#         #     new_widget, Widget
#         # ), f"expected an instance of a Widget, found an {type(new_widget)}"
#         # remove previous widget
#         if len(self._nested_):
#             old_widget = self._nested_[0]  # self._widget
#             if self.isrendered():
#                 old_widget._derender_()
#             if self.isplaced():
#                 old_widget._pickup_()
#             # old_widget must be nested, so unnest the widget
#             self._unnest_(old_widget)
#
#             # self._widget = new_widget
#             del old_widget
#         gc.collect()
#
#         # then add the new one
#         new_widget = Application
#
#         self._nest_(new_widget)
#         if self.isplaced():
#             new_widget._place_((0, 0), self.dims)
#         if self.isrendered():
#             new_widget._render_()
#         gc.collect()
