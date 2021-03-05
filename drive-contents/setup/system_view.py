import gc
import os

from tg_gui_core import *
from tg_gui_std.all import Rect, Pages, PageState, Label

from setup.watchface import default_face
from setup.watchshade import shade

# scan and choose an app to load
PREFERED_APP_TO_LOAD = None  # None for auto

availble_apps = [app_dir for app_dir in os.listdir("/apps")]
public_apps = [app_dir for app_dir in availble_apps if not app_dir.startswith("_")]

if (PREFERED_APP_TO_LOAD in availble_apps) or (len(public_apps) > 0):
    if PREFERED_APP_TO_LOAD in availble_apps:
        app_dir = PREFERED_APP_TO_LOAD
    else:
        app_dir = public_apps[0]
    app_module = __import__(f"/apps/{app_dir}")
    app_widget = app_module.Application
else:
    app_widget = Label(text="No App Loaded")


# for later
# apps = {}
# for app in availble_apps:
#     if not app.startswith("_"):
#         mod = __import__(f"/apps/{app}")
#         app_obj = mod.Application
#         del mod
#         apps[app] = app_obj


class SystemView(Pages):

    # page = PageState(self.face)
    page = PageState(
        0,  # REQUIRES PATCH to allow for specifying by name
        mode=PageState.mode.page_widget,
    )

    face = default_face
    shade = shade

    app_page = PageState(0)
    apptray = Pages(
        show=app_page,
        pages=(app_widget,),
    )

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
