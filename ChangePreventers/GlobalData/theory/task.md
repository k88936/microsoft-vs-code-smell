The problem with global data is that it can be modified from anywhere in the code base,
and there’s no mechanism to discover which bit of code touched it.

Time and again, this leads to bugs that breed from a form of spooky action from a distance,
and it’s very hard to find out where the buggy part of the program is.
The most obvious form of global data is global variables,
but we also see this problem with class variables and singletons.

[//]: # (TODO some global attack ???)