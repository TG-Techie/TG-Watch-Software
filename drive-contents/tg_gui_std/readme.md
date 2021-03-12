## Pages:

Pages has two modes of initing
- Single instance classes
- Widget instances

Single instance classes are similar to Single instance `Layout` Classes,
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
`__init__` and passing the pages argument to `super().__init__(...)`.
