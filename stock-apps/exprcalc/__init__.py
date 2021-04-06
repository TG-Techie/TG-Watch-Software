from tg_gui_std.all import *
import time


def row(*args):
    for arg in args:
        # if isinstance(arg, str):
        #      yield Button(text=arg, press=(arg), margin=2)
        if isinstance(arg, Widget) or arg is None:
            yield arg
        elif isinstance(arg, tuple) and len(arg) == 2:
            text, action = arg
            if isinstance(action, AttributeSpecifier):
                action = action(text)
            yield Button(text=text, press=action, margin=2)
        else:
            raise NotImplementedError(
                f"row item from `{repr(arg)}` of type {type(arg)}"
            )
    else:
        return None


@singleinstance
class Application(Layout):

    stack = State((1, 2, 3, 4))
    # roll_counter = State(0)
    shown_expr = DerivedState(stack, lambda s: str(s[-1]))
    view = shown_expr
    # view = DerivedState((roll_counter, shown_expr), lambda rc, e: f"{'XYZT'[rc]}: {e}")
    last_key_press = -1

    stackview = ZStack(
        Button(text="", press=self.roll()),
        Rect(fill=color.black, radius=0),
        Label(text=view, _alignment=align.leading),
    )

    # @singleinstance
    # class keypad(Pages):
    #     page = PageState(self.numpad)
    numpad = HSplit(
        VSplit(*row(("789", self.enter_num), ("+", self.op), ("*", self.op))),
        VSplit(*row(("456", self.enter_num), ("-", self.op), ("/", self.op))),
        VSplit(
            *row(
                ("123", self.enter_num), ("0", self.add_zero()), ("del", self.delchar())
            )
        ),
    )

    def _any_(self):
        width, height = self.width // 3, self.height // 4
        self.stackview(top, (self.width, height))
        self.numpad(bottom, (self.width, height * 3))

    def roll(self):
        a, b, c, d = self.stack
        print("rolling:")
        # self.readout()
        self.stack = d, a, b, c
        self.readout()
        # self.roll_counter = (self.roll_counter + 1) % 4

    def readout(self):
        a, b, c, d = self.stack
        print(f"""  {a}\n  {b}\n  {c}\n  {d}""")

    def enter_num(self, numset):
        a, b, c, d = self.stack
        nums = tuple(numset)
        shown_expr = self.shown_expr

        now = time.monotonic()
        since_since_last = now - self.last_key_press
        print(f"since_since_last={since_since_last}")
        self.last_key_press = now

        num_in_set = shown_expr[-1] in nums
        if num_in_set and since_since_last <= 0.65:
            # swap the last digit for the next in the num set
            current_digit = shown_expr[-1]
            next_digit = nums[(nums.index(current_digit) + 1) % len(nums)]
            print(shown_expr, ":", current_digit, "into", next_digit)
            numstr = shown_expr[0:-1] + next_digit
            if "." in numstr:
                val = float(numstr)
            else:
                val = int(numstr)
        else:
            val = d * 10 + int(nums[0])

        self.stack = a, b, c, val

    def delchar(self):
        a, b, c, d = self.stack
        shown_expr = self.shown_expr
        next_str = shown_expr[0:-1]
        if len(next_str) == 0:
            val = 0
        elif "." in next_str:
            val = float(next_str)
        else:
            val = int(next_str)
        self.stack = a, b, c, val

    def add_zero(self):
        a, b, c, d = self.stack
        print(f"key: 0")
        self.stack = a, b, c, d * 10
        self.readout()

    def op(self, opchar):
        a, b, c, d = self.stack
        print(f"{c} {opchar} {d}")
        if "Err" == c or "Err" == d:
            val = "Err"
        elif opchar == "+":
            val = c + d
        elif opchar == "-":
            val = c - d
        elif opchar == "*":
            val = c * d
        elif opchar == "/":
            if d == 0:
                val = "Err"
            val = c / d
        else:
            raise NotImplementedError(f"no operation for '{op}'")

        self.stack = a, a, b, val
        self.readout()
