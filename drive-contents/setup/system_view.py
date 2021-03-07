import gc
import os

from tg_gui_core import *
from tg_gui_std.all import Rect, Pages, PageState, Label

from setup.watchface import default_face
from setup.watchshade import shade

# scan and choose an app to load
apps_dir_contents = os.listdir("/apps")

# if there is a preferred.txt read it in
if "preferred.txt" in apps_dir_contents:
    with open("apps/preferred.txt", "r") as preferred_app:
        preferred_app_to_load = preferred_app.read().strip()
    if len(preferred_app_to_load) == 0:
        preferred_app_to_load = None
else:
    preferred_app_to_load = None

# filter for file
availble_apps = [app_dir for app_dir in apps_dir_contents if "." not in app_dir]
# filter for public apps
public_apps = [app_dir for app_dir in availble_apps if not app_dir.startswith("_")]

if (preferred_app_to_load in availble_apps) or (len(public_apps) > 0):
    if preferred_app_to_load in availble_apps:
        app_dir = preferred_app_to_load
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
        # mode=PageState.mode.page_widget,
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
