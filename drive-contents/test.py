from tg_gui_platform import all
from system import clock
from runtime_importer import *

rep = lambda msg: (
    gc.collect(),
    gc.collect(),
    gc.collect(),
    print(msg, gc.mem_free()),
    gc.mem_free()
    # gc.collect(),
    # print(gc.mem_free(), end=" "),
    # gc.collect(),
    # print(gc.mem_free(), end=" "),
    # gc.collect(),
    # print(gc.mem_free()),
)[-1]
rep("init")

# diff = []
# for _ in range(1000):
#     m = ModuleWrapper("apps/calc")
#     pre = rep("post mod")
#
#     m._load_()
#     rep("post load")
#
#     m._clear_()
#     post = rep("post clear")
#
#     print(pre - post)
#     diff.append(pre - post)


from setup.watchsetup import (
    DisplayioRootWrapper,
    screen,
    display,
    event_loop,
    Pages,
    PageState,
    Layout,
    Button,
    Rect,
)

from setup.appview import app_view


@DisplayioRootWrapper(screen=screen, display=display, size=(240, 240))
class root(Layout):

    appview = app_view

    def _any_(self):
        self.appview((0, 0), self.dims)


root._superior_._std_startup_()
gc.collect()


diff = []
for _ in range(10):
    # m = ModuleWrapper("apps/calc")
    # pre = rep("post mod")
    #
    # m._load_()
    # rep("post load")
    #
    # m._clear_()
    # post = rep("post clear")
    #
    # print(pre - post)
    # diff.append(pre - post)

    pre = rep("pre")
    app_view.load_app("apps/calc")
    display.refresh()
    mid = rep("mid")
    app_view.close_app
    post = rep("post")
    print(pre - post, pre, mid, post)
    diff.append(pre - post)

print(diff)
