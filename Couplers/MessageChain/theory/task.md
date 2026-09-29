Message Chains occur when a class (class A),
in order to get some data from class D,
must access class B and use it to access class C,
and use class C to access class D.

The reason to avoid this is that class A becomes reliant on the implementation of the in-between classes (classes B and
C).