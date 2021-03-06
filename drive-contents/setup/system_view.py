import gc
import os

from tg_gui_core import *
from tg_gui_std.all import Rect, Pages, PageState

from setup.watchface import default_face
from setup.watchshade import shade

APP_TO_LOAD = "hex_mixer"

apps = {}
appfolders = os.listdir("/apps")
for app in (app for app in appfolders if not app.startswith("_")):
    # with open(f"/apps/{app}/info.json") as file:
    #     try:
    #         info = json.load(file)
    #     except:
    #         print(f"unable to load app info {file(file)}")
    #         continue
    mod = __import__(f"/apps/{app}")
    app_obj = mod.Application
    del mod
    apps[app] = app_obj
    # launch_widget = LaunchWidget.frominfo(f"/apps/{app}", info)
    # apps[app] = launch_widget

app_page_state = PageState(0)
app_pages = Pages(
    show=app_page_state,
    pages=(apps[APP_TO_LOAD],),  # tuple(apps.values()),
    # _buffered=False,
)


class SystemView(Pages):

    # page = PageState(self.face)
    page = PageState(
        0,  # REQUIRES PATCH to allow for specifying by name
        # mode=PageState.mode.page_widget,
    )

    face = default_face
    shade = shade

    app_page = app_page_state
    apptray = app_pages

    open_stack = []

    current_module_wrapper = None

    def swipe_down(self):
        self.push_view(self.shade)

    def swipe_up(self):
        page = self.page
        if page is self.shade:
            self.pop_view()
        elif page is self.face:
            self.page = self.apptray
        else:
            self.page = self.face

    def push_view(self, page_to_open):
        stack = self.open_stack
        if len(stack) == 0 or stack[-1] is not page_to_open:
            stack.append(self.page)
        self.page = page_to_open

    def swipe_left(self):
        self.app_page = (self.app_page + 1) % len(apps)

    def swipe_right(self):
        self.app_page = (self.app_page - 1) % len(apps)

    def pop_view(self):
        if len(self.open_stack):
            self.page = topage = self.open_stack.pop(-1)
        else:
            self.page = self.face
