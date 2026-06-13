Primitive Obsessions are the overuse of primitives (eg. 1, 3.14, "Hello", False),
rather than classes that make use of those primitives.

A Primitive Obsession is often a result of the programmer’s desire not to create a small class, but having small classes is not itself a bad thing.

We thus see calculations that treat monetary amounts as plain numbers,
or calculations of physical quantities that ignore units (adding inches to millimeters),
or lots of code doing `if (a < upper && a > lower)`

Strings are particularly common containers for this kind of smell:
* A telephone number is more than just a collection of characters.
* A Position will be ambiguous and need extra doc if provided as a string.
* ...

<img src="../../../res/primitive_obsession.webp">

Primitive Obsessions are also often Data Clumps.