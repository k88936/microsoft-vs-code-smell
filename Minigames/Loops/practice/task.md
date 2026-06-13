# Introduce

Here are concise examples transforming a list of integers `[1, 2, 3, 4]` by doubling each element (map) and summing them (reduce)
in different languages.

we can just get a glance of their api design.

### Java(Stream API)
```java
import java.util.List;

int sum = List.of(1, 2, 3, 4).stream()
              .map(n -> n * 2)
              .reduce(0, Integer::sum);
```

### C++ (Ranges/Views - C++20)

```cpp
#include <vector>
#include <ranges>
#include <numeric>

std::vector<int> v = {1, 2, 3, 4};
auto doubled = v | std::views::transform([](int n) { return n * 2; });
int sum = std::accumulate(doubled.begin(), doubled.end(), 0);
```


### JavaScript (high-rank function)
```javascript
const nums = [1, 2, 3, 4];
const sum = nums.map(n => n * 2).reduce((acc, curr) => acc + curr, 0);
```

### Rust (iterable)
```rust
let nums = vec![1, 2, 3, 4];
let sum: i32 = nums.iter().map(|&x| x * 2).sum();
// Reduce equivalent: nums.iter().map(|&x| x * 2).reduce(|acc, x| acc + x).unwrap_or(0)
```

---

However, python does not provide a oop-like builtin api; Its api is more function-like:
```python
from functools import reduce

nums = [1, 2, 3, 4]
sum_val = reduce(lambda acc, x: acc + x, map(lambda x: x * 2, nums), 0)
# Idiomatic Python prefers: sum(x * 2 for x in nums)
```

We will implement Stream class supporting these operations
and use it to rewrite the sunshine-to-damage calculation.

# Task

* impl the `filter` for Stream. You should use the built-in filter function. You can refer to the implementation of `map`.
* rewrite the sunshine-to-damage calculation using Stream.
    ```python
    # example: compute the sum of (multiply 10 foreach( even numbers from 1 to 5))
    stream = (Stream([1, 2, 3, 4, 5])
              .filter(lambda x: x % 2 == 0)
              .map(lambda x: x * 10))

    # Consumes lazily
    print(stream.reduce(lambda acc,x: acc +x, 0))  # Output: 60 (20 + 40)
    ```