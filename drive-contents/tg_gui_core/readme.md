# TG-Gui

## What is sunder?
Just how dunder is reserved by python the language, sunder is revered by TG-Gui
A "sunder" varible function or variable will start and end with a single underscore (`_`).

This Api uses sunder to signify the boundaries for protocols or anything __internal__
that will interact between objects. That is to say sunder is used to separate the public, "user-facing" API from the internal protocols.

Any sunder method, function, property, class, etc is reserved as part of the framework and is subject to change in implementation, behavior, or purpose between internal revision of TG-Gui.

#### Why not use dunder?
Since dunder attributes are reserved by python, it is not "couth" to invent new ones.
Instead, TG-Gui defines sunder attributes when it needs "magic" behavior.

## The widget process:
- __init__ / __del__
- nest / unnest
- format / deformat
    - form / deform
    - place / pickup
- build / demol
    - render / derender
    - link / unlink
- show / hide
