from tg_gui_core import Container, Widget, declarable, center


@declarable
class View(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._body = self._scan_class_for_body()

    def _on_nest_(self):
        self._nest_(self._body)

    def _form_(self, dim_spec):
        self._body._form_(dim_spec)
        super(Container, self)._form_(self._body.dims)

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)
        self._body._place_(center)

    def _build_(self):
        super(Container, self)._build_()
        self._body._build_()
        self._screen_.on_container_build(self)

    def _show_(self):
        super(Container, self)._show_()
        self._body._show_()
        self._screen_.on_container_show(self)

    def _scan_class_for_body(self):
        cls = type(self)
        body_attr = getattr(cls, "body")
        if isinstance(body_attr, property):
            return self.body
        elif isinstance(body_attr, Widget):
            return body_attr
        else:
            raise TypeError(f"{self} had no declared body attribute or property")
