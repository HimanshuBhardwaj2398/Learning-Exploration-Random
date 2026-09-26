import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Decorators · Python")


@app.cell
def _():
    import contextlib
    import functools
    import io
    import itertools
    import textwrap

    import marimo as mo

    from learnkit import Case, assert_cases, check, code_view, kv_view, line_of, run_cases, solution

    return (
        Case,
        assert_cases,
        check,
        code_view,
        contextlib,
        functools,
        io,
        itertools,
        kv_view,
        line_of,
        mo,
        run_cases,
        solution,
        textwrap,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Decorators

    **Concept 01 · Python.** A decorator adds behaviour *around* a function (timing, logging, caching, retries, access checks, registration) without editing the function itself. You already use them: `@functools.cache`, `@property`, `@dataclass`, `@app.get("/")` in FastAPI, `@pytest.fixture`. Even this notebook's source file is a stack of `@app.cell` decorators.

    **The one idea:** `@deco` above a `def` is exactly `f = deco(f)`. A decorator isn't magic, it's **name rebinding** spelled with an `@`.
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md("**How to use this notebook.** Online it runs in your browser; locally, `marimo edit python/01-decorators/decorators.py`. "
              "Order: **mental model → prove it live → build it up → stacking → real decorators → pitfalls → practice → recall.**"),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Mental model: names are labels, functions are objects

    Python names are **labels stuck on objects**. `def` is really an **assignment**: it builds a function object and binds a name to it. So the line `say_whee = not_during_the_night(say_whee)` moves the `say_whee` label off the function you wrote and onto a brand-new one, `wrapper`, which keeps the original inside it as `func`.

    Step through the file the way Python runs it (this is the example from Real Python's decorator primer):
    """)
    return


@app.cell
def _(textwrap):
    QUIET_NIGHT = textwrap.dedent('''
    # quiet_night.py
    from datetime import datetime

    def not_during_the_night(func):
        def wrapper():
            if 7 <= datetime.now().hour < 22:
                func()
            else:
                pass  # neighbours are asleep
        return wrapper

    def say_whee():
        print("Whee!")

    say_whee = not_during_the_night(say_whee)

    # your file
    >>> from quiet_night import say_whee
    >>> say_whee()
    ''').strip()

    REBIND_STEPS = [
        (set(), [], "Importing a module **runs the whole file once**, top to bottom. Keep your eye on the name `say_whee`."),
        ({"N1", "OA", "AR1"}, ["def not_during_the_night"], "`def` is an **assignment**: it builds a function object and binds the name `not_during_the_night` to it."),
        ({"N1", "OA", "AR1", "N2", "OB", "AR2B"}, ["def say_whee", 'print("Whee!")'], "Same again: `say_whee` now points at the **original** function that prints Whee!"),
        ({"N1", "OA", "AR1", "N2", "OB", "AR2B", "OC", "ARF"}, ["say_whee = not_during_the_night"],
         "The **right-hand side runs first**. Calling the decorator builds a brand-new function, `wrapper`, which remembers the original as its `func`. Nothing is rebound yet."),
        ({"N1", "OA", "AR1", "N2", "OB", "OC", "ARF", "AR2C", "DIM"}, ["say_whee = not_during_the_night"],
         "Now the `=` runs: it **moves the say_whee label** onto `wrapper`. The original still exists, but only inside wrapper."),
        ({"N1", "OA", "AR1", "N2", "OB", "OC", "ARF", "AR2C", "DIM", "N3", "AR3"}, [">>> from quiet_night"],
         "`import` doesn't re-read your source or pick a `def`. It copies the **current value** of the name `say_whee`, and that value is `wrapper`."),
        ({"N1", "OA", "AR1", "N2", "OB", "OC", "ARF", "AR2C", "DIM", "N3", "AR3", "CALL"}, [">>> say_whee()"],
         "So `say_whee()` runs **wrapper**, which checks the hour and only then calls the original. That's the whole trick."),
    ]

    def rebinding_svg(show: set) -> str:
        indigo, teal, amber, grey = "#6366f1", "#0d9488", "#d97706", "#6b7280"

        def box(x, y, w, h, stroke, fill, lines, dim=False):
            opacity = ".4" if dim else "1"
            texts = "".join(
                f'<text x="{x + 12}" y="{y + 20 + 17 * k}" font-size="{13 if k == 0 else 11}" font-weight="{700 if k == 0 else 400}" '
                f'fill="currentColor" opacity="{1 if k == 0 else .7}" font-family="monospace">{t}</text>'
                for k, t in enumerate(lines)
            )
            return f'<g opacity="{opacity}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>{texts}</g>'

        parts = [
            '<defs><marker id="rb-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1L9 5L1 9z" fill="{indigo}"/></marker>'
            '<marker id="rb-func" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M1 1L9 5L1 9z" fill="{amber}"/></marker></defs>',
            '<text x="20" y="22" font-size="11" fill="currentColor" opacity=".55" letter-spacing="2">NAMES · labels</text>',
            '<text x="400" y="22" font-size="11" fill="currentColor" opacity=".55" letter-spacing="2">OBJECTS · in memory</text>',
        ]
        call = "CALL" in show
        width = "3.2" if call else "2.2"
        if "AR1" in show:
            parts.append(f'<path d="M262 62 L398 62" stroke="{indigo}" stroke-width="2.2" fill="none" marker-end="url(#rb-arrow)"/>')
        if "AR2B" in show:
            parts.append(f'<path d="M262 162 L398 162" stroke="{indigo}" stroke-width="2.2" fill="none" marker-end="url(#rb-arrow)"/>')
        if "AR2C" in show:
            parts.append(f'<path d="M262 162 C 320 162, 340 300, 398 300" stroke="{indigo}" stroke-width="2.2" fill="none" marker-end="url(#rb-arrow)"/>')
        if "AR3" in show:
            parts.append(f'<path d="M262 330 L398 318" stroke="{indigo}" stroke-width="{width}" fill="none" marker-end="url(#rb-arrow)"/>')
        if "ARF" in show:
            parts.append(f'<path d="M520 268 L520 196" stroke="{amber}" stroke-width="{width}" fill="none" marker-end="url(#rb-func)"/>'
                         f'<text x="528" y="236" font-size="11" fill="{amber}" font-family="monospace">func</text>')
        if "N1" in show:
            parts.append(box(20, 40, 242, 44, indigo, "rgba(99,102,241,.08)", ["not_during_the_night"]))
        if "N2" in show:
            parts.append(box(20, 140, 242, 50, indigo, "rgba(99,102,241,.08)", ["say_whee", "in quiet_night"]))
        if "N3" in show:
            parts.append(box(20, 306, 242, 50, indigo, "rgba(99,102,241,.08)", ["say_whee", "in your file, after import"]))
        if "OA" in show:
            parts.append(box(400, 40, 250, 44, grey, "rgba(127,127,127,.12)", ["function not_during_the_night"]))
        if "OB" in show:
            parts.append(box(400, 130, 250, 62, amber, "rgba(217,119,6,.12)", ["function say_whee (original)", 'prints "Whee!"'], dim="DIM" in show))
        if "OC" in show:
            parts.append(box(400, 270, 250, 78, teal, "rgba(13,148,136,.12)", ["function wrapper", "checks the hour, then maybe", "calls func → the original"]))
        if not show:
            parts.append('<text x="340" y="200" text-anchor="middle" font-size="13" fill="currentColor" opacity=".5">Move the slider to run the file</text>')
        return f'<svg viewBox="0 0 670 370" width="100%" style="max-width:670px;color:inherit">{"".join(parts)}</svg>'

    return QUIET_NIGHT, REBIND_STEPS, rebinding_svg


@app.cell
def _(REBIND_STEPS, mo):
    rebind_step = mo.ui.slider(0, len(REBIND_STEPS) - 1, value=0, label="Step", full_width=True, show_value=True)
    rebind_step
    return (rebind_step,)


@app.cell
def _(
    QUIET_NIGHT,
    REBIND_STEPS,
    code_view,
    line_of,
    mo,
    rebind_step,
    rebinding_svg,
):
    _show, _snippets, _caption = REBIND_STEPS[rebind_step.value]
    _active = [line_of(QUIET_NIGHT, s) for s in _snippets]
    mo.vstack([
        mo.hstack([code_view(QUIET_NIGHT, active=_active, title="quiet_night.py, then your REPL"), mo.Html(rebinding_svg(_show))], align="start", gap=2, wrap=True),
        mo.md(f"**Step {rebind_step.value + 1} of {len(REBIND_STEPS)}.** {_caption}"),
        mo.callout(mo.md("`say_whee = not_during_the_night(say_whee)` is **exactly** what `@not_during_the_night` above the `def` does."), kind="neutral"),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · Prove it, live

    The same decorator, but with the clock injected so you can move time. Every value below is computed by running the code in this notebook.
    """)
    return


@app.cell
def _(mo):
    hour = mo.ui.slider(0, 23, value=23, label="It is this hour", show_value=True)
    hour
    return (hour,)


@app.cell
def _(contextlib, hour, io, kv_view):
    def make_quiet_decorator(current_hour):
        def not_during_the_night(func):
            def wrapper():
                if 7 <= current_hour() < 22:
                    func()
                else:
                    pass  # neighbours are asleep
            return wrapper
        return not_during_the_night

    _not_during_the_night = make_quiet_decorator(lambda: hour.value)

    def _say_whee():
        print("Whee!")

    _original = _say_whee
    _say_whee = _not_during_the_night(_say_whee)
    _buffer = io.StringIO()
    with contextlib.redirect_stdout(_buffer):
        _say_whee()
    _printed = _buffer.getvalue().strip() or "(nothing: neighbours are asleep)"
    kv_view({
        "say_whee() printed": _printed,
        "say_whee.__name__": _say_whee.__name__,
        "say_whee is the original?": _say_whee is _original,
        "wrapper's func is the original?": dict(zip(_say_whee.__code__.co_freevars, (c.cell_contents for c in _say_whee.__closure__)))["func"] is _original,
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    Notice `say_whee.__name__` is **`wrapper`**: the label moved, and the new object doesn't know it's supposed to be called `say_whee`. Section 3 fixes that. And the original is still alive inside the wrapper's **closure**: that's how `wrapper` can call `func` long after `not_during_the_night` returned.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3 · Build it up

    | Need | Pattern |
    | :--- | :--- |
    | work with any signature, keep the return value | `def wrapper(*args, **kwargs): return func(*args, **kwargs)` |
    | keep `__name__`, `__doc__`, `__wrapped__` | `@functools.wraps(func)` on the wrapper |
    | configure the decorator (`@repeat(3)`) | a **factory**: a function that returns the decorator (three layers) |
    | keep state between calls | an attribute on the wrapper, a `nonlocal`, or a class with `__call__` |

    **The canonical template, pseudo code first:** *take func → define wrapper(*args, **kwargs) → do something before → call func and keep its result → do something after → return the result → return wrapper.*

    ```python
    import functools

    def decorator(func):
        @functools.wraps(func)                # copy __name__, __doc__, set __wrapped__
        def wrapper(*args, **kwargs):
            # before
            result = func(*args, **kwargs)
            # after
            return result
        return wrapper


    def repeat(times):                        # factory: returns a decorator
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = None
                for _ in range(times):
                    result = func(*args, **kwargs)
                return result
            return wrapper
        return decorator
    ```
    """)
    return


@app.cell
def _(functools, mo):
    def _plain(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def _wrapped(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def _greet(name: str) -> str:
        """Say hello."""
        return f"hello {name}"

    _a, _b = _plain(_greet), _wrapped(_greet)
    mo.md(
        "What survives wrapping, measured:\n\n| | without `wraps` | with `functools.wraps` |\n| :--- | :--- | :--- |\n"
        f"| `__name__` | `{_a.__name__}` | `{_b.__name__}` |\n"
        f"| `__doc__` | `{_a.__doc__!r}` | `{_b.__doc__!r}` |\n"
        f"| `__wrapped__` | {'present' if hasattr(_a, '__wrapped__') else 'missing'} | {'present' if hasattr(_b, '__wrapped__') else 'missing'} |\n"
        f"| call result | `{_a('ana')!r}` | `{_b('ana')!r}` |\n\n"
        "Without `wraps`, tracebacks, logs, `help()` and debuggers all see *wrapper*. Always add it."
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · Stacking: applied bottom-up, run top-down

    ```python
    @bold
    @italic
    def hi(): ...
    ```
    is `hi = bold(italic(hi))`: the decorator **nearest the `def` is applied first**, but at call time the **outermost wrapper runs first**. Order changes behaviour. Try it:
    """)
    return


@app.cell
def _(functools, itertools, mo):
    def make_tag_decorator(name, transform, trace):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                trace.append(f"enter {name}")
                result = transform(func(*args, **kwargs))
                trace.append(f"exit {name}")
                return result
            return wrapper
        return decorator

    STACK_PARTS = {
        "bold": lambda s: f"<b>{s}</b>",
        "italic": lambda s: f"<i>{s}</i>",
        "shout": lambda s: s.upper(),
    }
    stack_order = mo.ui.dropdown(
        options=[" → ".join(p) for p in itertools.permutations(STACK_PARTS)],
        value="bold → italic → shout",
        label="Decorators, top to bottom",
    )
    stack_order
    return STACK_PARTS, make_tag_decorator, stack_order


@app.cell
def _(STACK_PARTS, kv_view, make_tag_decorator, mo, stack_order):
    _names = stack_order.value.split(" → ")
    _trace: list = []

    def _hi():
        _trace.append("run hi")
        return "hi there"

    _func = _hi
    for _name in reversed(_names):  # bottom decorator is applied first
        _func = make_tag_decorator(_name, STACK_PARTS[_name], _trace)(_func)
    _result = _func()
    _source = "\n".join(f"@{n}" for n in _names) + "\ndef hi():\n    return \"hi there\""
    _expression = "hi = " + "(".join(_names) + "(hi" + ")" * len(_names)
    mo.hstack([
        mo.md(f"```python\n{_source}\n```\nis `{_expression}`"),
        kv_view({"result": _result, "call trace": " → ".join(_trace)}),
    ], align="center", gap=2, wrap=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Put `shout` **outermost** and it uppercases the tags too (`<B><I>HI THERE</I></B>`); put it **innermost** and only the text is shouted. The call trace always enters from the top and exits in reverse, like nested function calls, because that's exactly what they are.

    ## 5 · Decorators you'll meet at work

    - **`@functools.cache` / `@lru_cache(maxsize=...)`:** memoisation, the bridge from recursion to DP. Measured below.
    - **Registration:** the decorator records the function and returns it unchanged. That's how `@app.get("/users")` in FastAPI, `@pytest.fixture` and plugin systems work:

    ```python
    ROUTES = {}

    def route(path):
        def register(func):
            ROUTES[path] = func          # side effect at definition time
            return func                  # the function itself is unchanged
        return register

    @route("/health")
    def health():
        return "ok"
    ```

    - **`@property`, `@classmethod`, `@staticmethod`:** decorators that build *descriptors* (the OOP notebook will open that box).
    - **`@dataclass`:** a **class** decorator: it takes a class and returns it with `__init__`, `__repr__` and `__eq__` generated.
    """)
    return


@app.cell
def _(mo):
    fib_n = mo.ui.slider(5, 22, value=20, label="n", show_value=True)
    fib_n
    return (fib_n,)


@app.cell
def _(fib_n, functools, kv_view):
    _calls = {"naive": 0, "cached": 0}

    def _fib_naive(k):
        _calls["naive"] += 1
        return k if k < 2 else _fib_naive(k - 1) + _fib_naive(k - 2)

    @functools.cache
    def _fib_cached(k):
        _calls["cached"] += 1
        return k if k < 2 else _fib_cached(k - 1) + _fib_cached(k - 2)

    _v1, _v2 = _fib_naive(fib_n.value), _fib_cached(fib_n.value)
    kv_view({
        f"fib({fib_n.value})": _v1,
        "calls without a cache": f"{_calls['naive']:,}",
        "calls with @functools.cache": _calls["cached"],
        "same answer?": _v1 == _v2,
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    Exponential to linear with one line: each `fib(k)` is computed once and then looked up. That's **top-down dynamic programming**, and it's why "memoise the recursion" is the first move on a DP problem. (Arguments must be hashable, because they become dict keys.)
    """)
    return


@app.cell
def _():
    PITFALLS = [
        ("1 · The decorator forgets to return the wrapper", "Then `f = deco(f)` binds f to None.",
         "def deco(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n\n@deco\ndef f():\n    return 42\n\nresult = f()\n",
         "def deco(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef f():\n    return 42\n\nresult = f()\n"),
        ("2 · The wrapper drops the return value", "It calls func but never returns what func returned.",
         "def deco(func):\n    def wrapper(*args, **kwargs):\n        func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef f():\n    return 42\n\nresult = f()\n",
         "def deco(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef f():\n    return 42\n\nresult = f()\n"),
        ("3 · A wrapper with no *args, **kwargs", "It only fits functions that take no arguments.",
         "def deco(func):\n    def wrapper():\n        return func()\n    return wrapper\n\n@deco\ndef add(a, b):\n    return a + b\n\nresult = add(2, 3)\n",
         "def deco(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef add(a, b):\n    return a + b\n\nresult = add(2, 3)\n"),
        ("4 · A factory used without parentheses", "`@repeat` passes the function in as `times`, so the 'decorator' is the inner function.",
         "def repeat(times):\n    def decorator(func):\n        def wrapper(*args, **kwargs):\n            for _ in range(times):\n                out = func(*args, **kwargs)\n            return out\n        return wrapper\n    return decorator\n\n@repeat\ndef f():\n    return 'hi'\n\nresult = f()\n",
         "def repeat(times):\n    def decorator(func):\n        def wrapper(*args, **kwargs):\n            for _ in range(times):\n                out = func(*args, **kwargs)\n            return out\n        return wrapper\n    return decorator\n\n@repeat(3)\ndef f():\n    return 'hi'\n\nresult = f()\n"),
        ("5 · Missing functools.wraps", "The function now reports the wrapper's identity.",
         "def deco(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef area():\n    return 1\n\nresult = area.__name__\n",
         "import functools\n\ndef deco(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef area():\n    return 1\n\nresult = area.__name__\n"),
        ("6 · Decorators run at import time", "The body of the decorator runs when the `def` is executed, not when the function is called.",
         "log = []\n\ndef deco(func):\n    log.append(f'decorating {func.__name__}')\n    return func\n\n@deco\ndef f():\n    return 1\n\nresult = log   # f was never called\n",
         "log = []\n\ndef deco(func):\n    def wrapper(*args, **kwargs):\n        log.append(f'calling {func.__name__}')\n        return func(*args, **kwargs)\n    return wrapper\n\n@deco\ndef f():\n    return 1\n\nresult = log   # still empty until f() runs\n"),
    ]

    def run_program(code: str) -> str:
        _ns: dict = {}
        try:
            exec(code, _ns)
            return repr(_ns.get("result"))
        except Exception as _exc:
            return f"{type(_exc).__name__}: {_exc}"

    return PITFALLS, run_program


@app.cell
def _(PITFALLS, mo, run_program):
    _rows = ["| Pitfall | Buggy result | Fixed result |", "| :--- | :--- | :--- |"]
    _details = {}
    for _title, _why, _bad, _good in PITFALLS:
        _rows.append(f"| {_title} | `{run_program(_bad)}` | `{run_program(_good)}` |")
        _details[_title] = mo.md(f"{_why}\n\n```python\n{_bad}```")
    mo.vstack([mo.md("## 6 · Pitfalls, run live"), mo.md("\n".join(_rows)), mo.accordion(_details)])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7 · Practice: worked → faded → solo

    Your decorator is tested by decorating real functions with it and checking what happens.
    """)
    return


@app.cell
def _(Case):
    HARNESS_COUNT = '''

    def _judge(n):
        @count_calls
        def add(a, b):
            """Add two numbers."""
            return a + b
        results = [add(i, i) for i in range(n)]
        return add.calls, results, add.__name__, add.__doc__
    '''
    CASES_COUNT = [
        Case((3,), (3, [0, 2, 4], "add", "Add two numbers.")),
        Case((0,), (0, [], "add", "Add two numbers."), label="never called"),
        Case((1,), (1, [0], "add", "Add two numbers.")),
    ]
    SOLUTION_COUNT = '''
    import functools

    def count_calls(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wrapper.calls += 1
            return func(*args, **kwargs)
        wrapper.calls = 0
        return wrapper
    '''
    STUB_COUNT = '''import functools

    def count_calls(func):
        # Count how many times func is called, in an attribute `calls` on the wrapper.
        # Keep func's return value, name and docstring.
        ...
    '''
    HARNESS_RETRY = '''

    def _judge(times, failures):
        attempts = {"n": 0}

        @retry(times)
        def flaky():
            """Fails `failures` times, then works."""
            attempts["n"] += 1
            if attempts["n"] <= failures:
                raise ValueError("boom")
            return "ok"

        try:
            outcome = flaky()
        except ValueError:
            outcome = "raised"
        return outcome, attempts["n"], flaky.__name__
    '''
    CASES_RETRY = [
        Case((3, 2), ("ok", 3, "flaky"), label="succeeds on the third try"),
        Case((3, 0), ("ok", 1, "flaky"), label="works first time: no retries"),
        Case((2, 2), ("raised", 2, "flaky"), label="gives up after 2 attempts and re-raises"),
        Case((1, 1), ("raised", 1, "flaky")),
    ]
    SOLUTION_RETRY = '''
    import functools

    def retry(times):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(times):
                    try:
                        return func(*args, **kwargs)
                    except Exception:
                        if attempt == times - 1:
                            raise
            return wrapper
        return decorator
    '''
    STUB_RETRY = '''import functools

    def retry(times):
        # A factory: retry(3) returns a decorator. Try func up to `times` attempts in total;
        # return the first success; if every attempt raises, re-raise the last exception.
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(times):
                    ...
            return wrapper
        return ...
    '''
    HARNESS_MEMO = '''

    def _judge(n):
        calls = {"n": 0}

        @memoize
        def fib(k):
            calls["n"] += 1
            return k if k < 2 else fib(k - 1) + fib(k - 2)

        return fib(n), calls["n"], fib.__name__
    '''
    CASES_MEMO = [
        Case((10,), (55, 11, "fib")), Case((0,), (0, 1, "fib")), Case((1,), (1, 1, "fib")),
        Case((30,), (832040, 31, "fib"), label="fib(30): 31 calls, not 2.7 million"),
    ]
    SOLUTION_MEMO = '''
    import functools

    def memoize(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args):
            if args not in cache:
                cache[args] = func(*args)
            return cache[args]
        return wrapper
    '''
    STUB_MEMO = '''import functools

    def memoize(func):
        # Cache results by the positional arguments (they are hashable).
        ...
    '''
    return (
        CASES_COUNT,
        CASES_MEMO,
        CASES_RETRY,
        HARNESS_COUNT,
        HARNESS_MEMO,
        HARNESS_RETRY,
        SOLUTION_COUNT,
        SOLUTION_MEMO,
        SOLUTION_RETRY,
        STUB_COUNT,
        STUB_MEMO,
        STUB_RETRY,
    )


@app.cell
def _(SOLUTION_COUNT, STUB_COUNT, mo, solution):
    count_editor = mo.ui.code_editor(value=STUB_COUNT, language="python", min_height=190)
    count_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Worked: `@count_calls`\n\nCount calls in `wrapper.calls`, return what the function returns, and keep its name and docstring. Read the solution, close it, write it."),
        solution(SOLUTION_COUNT, "Show the worked solution"), count_editor, count_run,
    ])
    return count_editor, count_run


@app.cell
def _(CASES_COUNT, HARNESS_COUNT, check, count_editor, count_run, mo):
    mo.stop(not count_run.value, mo.md("_Write your decorator, then press **Run tests**._"))
    check(count_editor.value + HARNESS_COUNT, "_judge", CASES_COUNT)
    return


@app.cell
def _(SOLUTION_RETRY, STUB_RETRY, mo, solution):
    retry_editor = mo.ui.code_editor(value=STUB_RETRY, language="python", min_height=250)
    retry_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Faded: `@retry(times)`\n\nA decorator **factory**. Fill in the blanks: the loop body and what the factory returns."),
        retry_editor, retry_run, solution(SOLUTION_RETRY),
    ])
    return retry_editor, retry_run


@app.cell
def _(CASES_RETRY, HARNESS_RETRY, check, mo, retry_editor, retry_run):
    mo.stop(not retry_run.value, mo.md("_Fill in the blanks, then press **Run tests**._"))
    check(retry_editor.value + HARNESS_RETRY, "_judge", CASES_RETRY)
    return


@app.cell
def _(SOLUTION_MEMO, STUB_MEMO, mo, solution):
    memo_editor = mo.ui.code_editor(value=STUB_MEMO, language="python", min_height=190)
    memo_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Solo: `@memoize`\n\nFrom scratch, without `functools.cache`. The `fib(30)` test doubles as a time limit: an uncached version makes 2.7 million calls and runs out of budget."),
        memo_editor, memo_run, solution(SOLUTION_MEMO),
    ])
    return memo_editor, memo_run


@app.cell
def _(CASES_MEMO, HARNESS_MEMO, check, memo_editor, memo_run, mo):
    mo.stop(not memo_run.value, mo.md("_Write it, then press **Run tests**._"))
    check(memo_editor.value + HARNESS_MEMO, "_judge", CASES_MEMO)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8 · Recall: close everything and answer from memory
    """)
    return


@app.cell
def _(mo):
    mo.accordion({
        "1. What does `@deco` above `def f` do, exactly?": mo.md("Runs `f = deco(f)` right after the `def`: the name `f` is rebound to whatever `deco` returns."),
        "2. How does the wrapper still reach the original function?": mo.md("Through its **closure**: `func` is a free variable captured when `deco` ran (`wrapper.__closure__`)."),
        "3. What do `*args, **kwargs` and `functools.wraps` each fix?": mo.md("`*args, **kwargs`: the wrapper fits any signature. `wraps`: the wrapper keeps `__name__`, `__doc__` and gains `__wrapped__`."),
        "4. How many layers does a decorator with arguments have, and why?": mo.md("Three: the factory takes the arguments and returns a decorator, which takes func and returns a wrapper."),
        "5. With `@a` above `@b`, which is applied first and which runs first?": mo.md("`b` is applied first (`f = a(b(f))`); at call time `a`'s wrapper runs first."),
        "6. When does a decorator's own body run?": mo.md("At definition (usually import) time, once per decorated function. Only the wrapper runs per call."),
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 9 · Go deeper

    - **Lab in this folder:** [Rebinding say_whee](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/python/01-decorators/rebinding-say-whee.html)
    - [Real Python: Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/): the `say_whee` examples come from here
    - [PEP 318](https://peps.python.org/pep-0318/): why the `@` syntax exists
    - [functools docs](https://docs.python.org/3/library/functools.html): `wraps`, `cache`, `lru_cache`, `singledispatch`
    - *Fluent Python* (Ramalho), ch. 9: decorators and closures, the definitive treatment

    **Next:** OOP, where `@property`, `@classmethod` and descriptors open up.
    """)
    return


@app.cell
def _(
    CASES_COUNT,
    CASES_MEMO,
    CASES_RETRY,
    HARNESS_COUNT,
    HARNESS_MEMO,
    HARNESS_RETRY,
    PITFALLS,
    QUIET_NIGHT,
    REBIND_STEPS,
    SOLUTION_COUNT,
    SOLUTION_MEMO,
    SOLUTION_RETRY,
    STUB_COUNT,
    STUB_MEMO,
    STUB_RETRY,
    assert_cases,
    line_of,
    run_cases,
    run_program,
):
    def test_answer_keys_pass():
        assert_cases(SOLUTION_COUNT + HARNESS_COUNT, "_judge", CASES_COUNT)
        assert_cases(SOLUTION_RETRY + HARNESS_RETRY, "_judge", CASES_RETRY)
        assert_cases(SOLUTION_MEMO + HARNESS_MEMO, "_judge", CASES_MEMO)

    def test_stubs_do_not_pass_yet():
        for stub, harness, cases in ((STUB_COUNT, HARNESS_COUNT, CASES_COUNT), (STUB_RETRY, HARNESS_RETRY, CASES_RETRY), (STUB_MEMO, HARNESS_MEMO, CASES_MEMO)):
            assert not all(r.passed for r in run_cases(stub + harness, "_judge", cases))

    def test_an_uncached_fib_hits_the_budget():
        slow = "import functools\n\ndef memoize(func):\n    return func\n"
        results = run_cases(slow + HARNESS_MEMO, "_judge", CASES_MEMO)
        assert not results[-1].passed and "too slow" in results[-1].error

    def test_every_pitfall_differs_from_its_fix():
        for title, _why, bad, good in PITFALLS:
            assert run_program(bad) != run_program(good), title

    def test_rebinding_steps_point_at_real_lines():
        for _show, snippets, _caption in REBIND_STEPS:
            for snippet in snippets:
                line_of(QUIET_NIGHT, snippet)

    return


if __name__ == "__main__":
    app.run()
