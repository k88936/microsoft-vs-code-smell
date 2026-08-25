These are classes that have fields, getting and setting methods for the fields, and nothing else. Such classes are dumb
data holders and are often being manipulated in far too much detail by other classes.

Data classes are often a sign of behavior in the wrong place, which means you can make big progress by moving it from
the client into the data class itself. But there are exceptions, and one of the best exceptions is a record that’s being
used as a result record from a distinct function invocation. A good example of this is the intermediate data structure
after you’ve applied Split Phase (154). A key characteristic of such a result record is that it’s immutable (at least in
practice). Immutable fields don’t need to be encapsulated and information derived from immutable data can be represented
as fields rather than getting methods.
