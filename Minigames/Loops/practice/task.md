### Introduce

there are different builtin pipeline api provided by different languages.

Here are concise examples transforming a list of integers `[1, 2, 3, 4]` by doubling each element (map) and summing them (reduce).

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

However, python does not provide a chainable, pipeline-like builtin api like those above; Its api is more function-like:
```python
from functools import reduce

nums = [1, 2, 3, 4]
sum_val = reduce(lambda acc, x: acc + x, map(lambda x: x * 2, nums), 0)
# Idiomatic Python prefers: sum(x * 2 for x in nums)
```
