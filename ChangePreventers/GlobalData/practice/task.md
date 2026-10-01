# Introduce
This piece of code is a piece of UI Editor logic.

<img src="../../../res/ui-editor.webp">

it has a preview window to let the user interactively adjust the UI position, size...
so there are some global variables to record the camera status.

you see, the read and write to variables are protected by a mutex.
it is buggy since some caller may forget to lock or unlock the mutex.

# Task

extract a camera manager as a module-level single instance to encapsulate the camera status,
and provide restricted access to the camera status.
