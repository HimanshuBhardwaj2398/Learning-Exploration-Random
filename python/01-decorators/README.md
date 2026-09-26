# Decorators

> `@deco` above a `def` is exactly `f = deco(f)`: a decorator is name rebinding, and the wrapper keeps the original alive in its closure.

Kind: concept · Status: learning

**Notebook:** [decorators.py](decorators.py) (the say_whee rebinding stepper, a live clock demo, `wraps` measured, a stacking lab, `functools.cache` call counts, live pitfalls, three decorator exercises). Run `marimo edit python/01-decorators/decorators.py` locally, or open it on the site.

## Spot it
- Behaviour that should wrap many functions without editing them: timing, logging, caching, retries, auth, registration
- In the wild: `@functools.cache`, `@property`, `@dataclass`, `@app.get(...)`, `@pytest.fixture`, marimo's `@app.cell`

## Template
```python
import functools

def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper

def repeat(times):                 # with arguments: a factory, three layers
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

## Traps (the ones that bite)
- Forgetting `return wrapper` → the name becomes `None`
- Forgetting `return result` → every call returns `None`
- No `*args, **kwargs` → only fits zero-argument functions
- `@repeat` instead of `@repeat(3)` → the function is passed as `times`
- No `functools.wraps` → `__name__` and `__doc__` report the wrapper
- The decorator body runs at **import** time; only the wrapper runs per call
- Stacking: `@a @b def f` is `a(b(f))`; b is applied first, a's wrapper runs first

## Ladder
| # | Exercise | Stage | Done |
| :--- | :--- | :--- | :--- |
| 1 | `@count_calls` | worked | |
| 2 | `@retry(times)` | faded | |
| 3 | `@memoize` | solo | |

## Questions
<!-- question notebooks for this topic live in questions/; tools/new_topic.py adds them here -->

## Review log
Counted from the day this topic reaches `Status: solid`:
- [ ] +2 days: write `@timer` and `@retry(times)` from a blank file
- [ ] +5 days: explain the say_whee rebinding out loud, then the stacking order
- [ ] +12 days: a class-based decorator with `__call__`
- [ ] +26 days: read a real decorator (FastAPI's `app.get`, `functools.lru_cache`) and explain it

## Resources
- Lab: [Rebinding say_whee](rebinding-say-whee.html)
- [Real Python: Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [functools docs](https://docs.python.org/3/library/functools.html) · [PEP 318](https://peps.python.org/pep-0318/)
- *Fluent Python* (Ramalho), ch. 9: decorators and closures
