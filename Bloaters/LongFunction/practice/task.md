> first refactor the program to make it easy to add the feature, then add the feature.

---

# Introduce

In this task, you need to split a long method into small ones.

This is a program computing the bill of comedy , (for demo purpose, the given function is not quite long compared to
those monsters in the real world)  
for example, input the example data, and ouput in text format:

```txt
Statement for BigCo
  Hamlet: $650.00 (55 seats)
  As You Like It: $580.00 (35 seats)
  Othello: $500.00 (40 seats)
Amount owed is $1730.00
You earned 47 credits
```

# Task

Think about we are having a new feature request: ALSO support HTML format output.

* before adding that feature, let us do a refactor first.

* we recommend splitting it into *compute based on rules* and *render to text* 2 steps, and passing a dataclass between
  them. Thus we can easily replace the latter render method.

* ps: we have written a [regression test](file:///CodeSmell/LongFunction/practice/tests/regression_test.py) to make sure
  it remains the same behavior after refactoring.

### Hints

<div class="hint" title="Shortcut for Extract method refactoring">

&shortcut:ExtractMethod; – shortcut to extract a method.
</div>
