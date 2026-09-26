import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", app_title="Object-oriented Python · python")


@app.cell
def _():
    import contextlib
    import dataclasses
    import io
    import random
    import re
    import textwrap
    from collections import OrderedDict, UserDict

    import marimo as mo

    from learnkit import (
        Case,
        assert_cases,
        check,
        code_view,
        kv_view,
        line_of,
        lookup_view,
        recursion_guard,
        run_cases,
        solution,
    )

    return (
        Case,
        OrderedDict,
        UserDict,
        assert_cases,
        check,
        code_view,
        dataclasses,
        kv_view,
        line_of,
        lookup_view,
        mo,
        random,
        re,
        recursion_guard,
        run_cases,
        solution,
        textwrap,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Object-oriented Python

    **Concept 02 · Python.** A class bundles **data** with the **rules for changing it**, so one place owns the invariant ("a balance never goes negative", "a cache never exceeds its capacity"). You already live on top of classes: `list`, `dict` and `str` are classes; `class Net(nn.Module)` with `super().__init__()` is inheritance; a Pydantic `BaseModel` is a class whose `__init__` validates; `len(df)` works because pandas wrote `DataFrame.__len__`.

    **The one idea:** an object is **a dict of its own data plus a link to its class**. `obj.name` searches a short chain: the object, then its class, then the parent classes. Methods, `self`, properties, inheritance, `super()` and dunder methods are all rules about that one search.
    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md("**How to use this notebook.** Online it runs in your browser; locally, `marimo edit python/02-oop/oop.py`. "
              "Order: **why classes → mental model (lookup) → prove it live → dunder lab → build it up → composition vs inheritance → pitfalls → practice → recall.**"),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1 · Why classes: start with a dict and some functions

    The simplest thing that works: keep the account in a dict and write functions that take it. Run it and look at what the dict ends up holding.
    """)
    return


@app.cell
def _(textwrap):
    DICT_VERSION = textwrap.dedent('''
    def open_account(owner):
        return {"owner": owner, "balance": 0}

    def deposit(account, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        account["balance"] += amount

    acct = open_account("Asha")
    deposit(acct, 100)
    acct["balnce"] = 500       # a typo: silently adds a new key
    acct["balance"] -= 1000    # any line can skip the rules
    ''').strip()
    return (DICT_VERSION,)


@app.cell
def _(DICT_VERSION, code_view, kv_view, mo):
    _ns: dict = {}
    exec(DICT_VERSION, _ns)
    mo.hstack([
        code_view(DICT_VERSION, title="accounts as dicts"),
        kv_view({k: repr(v) for k, v in _ns["acct"].items()}, title="acct after running it"),
    ], align="start", gap=2, wrap=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    **The bottleneck, named exactly:** the *rule* (positive deposits, no overdraft) lives in `deposit()`, but the *data* is open to every line of the program. Nothing owns the invariant, so a typo creates a second balance and a direct edit takes the account to −900 without any check running.

    **The fix, as pseudo code:** *put the data and the functions that change it in one place → keep the data behind those functions → let only listed attributes exist → expose read-only views where nobody should write.* That place is a class:
    """)
    return


@app.cell
def _(textwrap):
    CLASS_VERSION = textwrap.dedent('''
    class Account:
        __slots__ = ("owner", "_balance")      # only these attributes may exist

        def __init__(self, owner):
            self.owner = owner
            self._balance = 0                    # "_" means internal: use the methods

        @property
        def balance(self):                       # read like an attribute; no setter
            return self._balance

        def deposit(self, amount):
            if amount <= 0:
                raise ValueError("deposit must be positive")
            self._balance += amount

        def withdraw(self, amount):
            if amount > self._balance:
                raise ValueError("insufficient funds")
            self._balance -= amount
    ''').strip()
    CLASS_ATTEMPTS = [
        ("acct.deposit(100)", "the normal path"),
        ('acct.balnce = 500', "the same typo"),
        ("acct.balance = -900", "writing past the rules"),
        ("acct.withdraw(1000)", "overdraft through the method"),
        ("acct.deposit(-5)", "a negative deposit"),
        ("acct._balance = -5", "deliberately reaching inside"),
    ]
    return CLASS_ATTEMPTS, CLASS_VERSION


@app.cell
def _(CLASS_ATTEMPTS, CLASS_VERSION, code_view, mo):
    def run_attempts(source, attempts):
        ns: dict = {}
        exec(source + "\nacct = Account('Asha')\n", ns)
        rows = []
        for statement, what in attempts:
            try:
                exec(statement, ns)
                outcome = "ok"
            except Exception as exc:
                outcome = f"{type(exc).__name__}: {exc}"
            rows.append((statement, what, outcome, ns["acct"].balance))
        return rows

    _rows = run_attempts(CLASS_VERSION, CLASS_ATTEMPTS)
    _table = ["| Statement | Trying to… | What happened | balance after |", "| :--- | :--- | :--- | :--- |"]
    _table += [f"| `{s}` | {w} | `{o}` | {b} |" for s, w, o, b in _rows]
    mo.vstack([
        code_view(CLASS_VERSION, title="the same account as a class"),
        mo.md("\n".join(_table)),
        mo.md(
            "Every rule now runs, because every change goes through a method. The last row is honest about Python: "
            "`_balance` is a **convention**, not a lock. Python trusts you not to reach inside; the underscore tells readers they shouldn't. "
            "`__slots__` is optional (most classes skip it; `@dataclass(slots=True)` gives it for free); it's here to show the typo can be stopped."
        ),
    ])
    return (run_attempts,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 2 · Mental model: `obj.name` searches a chain of namespaces

    A **namespace** is a dict of names. Every object has one (`vars(obj)`), and so does every class. Looking up `acct.name` searches, in order:

    1. the **object's own dict**: data you set with `self.x = ...` in `__init__`
    2. its **class**: methods and class attributes, stored once and shared by every instance
    3. the **parent classes**, in the order `type(acct).__mro__` lists them (the *method resolution order*), ending at `object`

    The first hit wins. Nothing found → `AttributeError`. Pick a name and step through the search; everything below is read from real objects built from this code.
    """)
    return


@app.cell
def _(textwrap):
    LOOKUP_CODE = textwrap.dedent('''
    class Account:
        bank = "Chai Bank"                  # class attribute: one copy, shared

        def __init__(self, owner, balance=0):
            self.owner = owner              # instance attributes: one copy per object
            self.balance = balance

        def deposit(self, amount):
            self.balance += amount

    class Savings(Account):
        rate = 0.04

        def add_interest(self):
            self.deposit(self.balance * self.rate)

    acct = Savings("Asha", 100)
    ''').strip()

    def build_lookup_world(shadow_rate: bool) -> dict:
        ns: dict = {}
        exec(LOOKUP_CODE, ns)
        if shadow_rate:
            ns["acct"].rate = 0.10
        return ns

    def namespace_chain(obj) -> list:
        def shown(value):
            return "function" if callable(value) else repr(value)

        chain = [("acct", "the object · vars(acct)", {k: shown(v) for k, v in vars(obj).items()})]
        for cls in type(obj).__mro__:
            if cls is object:
                chain.append(("object", f"root of every class · {len(vars(object))} built-in names", {"__init__": "function", "__repr__": "function", "…": "…"}))
                continue
            own = {k: shown(v) for k, v in vars(cls).items() if not k.startswith("__") or k == "__init__"}
            chain.append((cls.__name__, "class · vars(" + cls.__name__ + ")", own))
        return chain

    LOOKUP_NAMES = ["owner", "rate", "bank", "deposit", "add_interest", "__init__", "overdraft"]
    return LOOKUP_CODE, LOOKUP_NAMES, build_lookup_world, namespace_chain


@app.cell
def _(LOOKUP_NAMES, mo):
    lookup_name = mo.ui.dropdown(options=LOOKUP_NAMES, value="deposit", label="Look up acct.")
    shadow = mo.ui.checkbox(label="first run `acct.rate = 0.10` (set it on the object)")
    mo.hstack([lookup_name, shadow], justify="start", gap=2, wrap=True)
    return lookup_name, shadow


@app.cell
def _(build_lookup_world, lookup_name, mo, namespace_chain, shadow):
    lookup_world = build_lookup_world(shadow.value)
    lookup_chain = namespace_chain(lookup_world["acct"])
    _hit = next((k for k, (_t, _s, entries) in enumerate(lookup_chain) if lookup_name.value in entries), None)
    lookup_steps = (_hit + 1) if _hit is not None else len(lookup_chain)
    lookup_step = mo.ui.slider(0, lookup_steps, value=0, label="Boxes searched", show_value=True, full_width=True)
    lookup_step
    return lookup_chain, lookup_step, lookup_steps, lookup_world


@app.cell
def _(
    LOOKUP_CODE,
    code_view,
    line_of,
    lookup_chain,
    lookup_name,
    lookup_step,
    lookup_steps,
    lookup_view,
    lookup_world,
    mo,
):
    def describe_lookup(world: dict, name: str) -> str:
        obj = world["acct"]
        try:
            value = getattr(obj, name)
        except AttributeError as exc:
            return f"Searched every box: `AttributeError: {exc}`."
        if callable(value) and hasattr(value, "__self__"):
            owner = next(c.__name__ for c in type(obj).__mro__ if name in vars(c))
            return (f"Found a **function** on `{owner}`. Reading it through the object returns a **bound method**: "
                    f"that function with `self` already filled in as `acct`. So `acct.{name}(...)` runs `{owner}.{name}(acct, ...)`.")
        where = "the object's own dict" if name in vars(obj) else "the class, shared by every account"
        return f"Found `{value!r}` in {where}."

    _done = lookup_step.value == lookup_steps
    _caption = describe_lookup(lookup_world, lookup_name.value) if _done else "Keep going: move the slider."
    _defined = {"owner": "self.owner", "rate": "rate = 0.04", "bank": "bank =", "deposit": "def deposit",
                "add_interest": "def add_interest", "__init__": "def __init__"}.get(lookup_name.value)
    mo.vstack([
        lookup_view(lookup_chain, lookup_name.value, searched=lookup_step.value),
        mo.md(f"**Step {lookup_step.value} of {lookup_steps}.** {_caption}"),
        code_view(LOOKUP_CODE, active=line_of(LOOKUP_CODE, _defined) if _defined else None, title="the code (highlight: where the name is defined)"),
    ])
    return (describe_lookup,)


@app.cell
def _(mo):
    mo.md(r"""
    Tick the checkbox with `rate` selected: now the object's own dict has `rate = 0.1`, the search stops there, and the class's `0.04` is **shadowed** (still there for every other account). That's all "overriding" is, whether an object shadows its class or a subclass shadows its parent.

    One refinement for later: a `@property` on the class is checked **before** the object's dict, which is how a property can intercept `acct.balance = ...`. The full order is in the Descriptor HowTo (section 10).

    ## 3 · Prove it, live
    """)
    return


@app.cell
def _(LOOKUP_CODE, mo):
    def evidence_rows() -> list:
        ns: dict = {}
        exec(LOOKUP_CODE, ns)
        acct, Account, Savings = ns["acct"], ns["Account"], ns["Savings"]
        rows = []

        def row(expr, value, meaning):
            rows.append((expr, value, meaning))

        acct.deposit(50)
        after_method = acct.balance
        Account.deposit(acct, 50)
        row("acct.deposit(50), then Account.deposit(acct, 50)", f"balance {after_method} → {acct.balance}",
            "the same function; the dot just passes acct as self")
        row("acct.deposit.__self__ is acct", acct.deposit.__self__ is acct, "a bound method remembers its object")
        row("acct.deposit.__func__ is Account.deposit", acct.deposit.__func__ is Account.deposit, "…and the plain function stored on the class")
        row("acct.deposit is acct.deposit", acct.deposit is acct.deposit, "a fresh bound method is built on every access")
        row("vars(acct)", vars(acct), "the object really is a dict of its own data")
        row("'rate' in vars(acct), acct.rate", ("rate" in vars(acct), acct.rate), "not on the object, found on the class")
        row("[c.__name__ for c in Savings.__mro__]", [c.__name__ for c in Savings.__mro__], "the search order for everything")
        row("type(acct).__name__, type(Savings).__name__", (type(acct).__name__, type(Savings).__name__), "classes are objects too; their type is `type`")

        acct.__len__ = lambda: 99
        try:
            length = len(acct)
        except TypeError as exc:
            length = f"TypeError: {exc}"
        row("acct.__len__ = lambda: 99; acct.__len__()", acct.__len__(), "you can call it by hand…")
        row("len(acct)", length, "…but syntax looks dunders up on the class, never on the object")
        return rows

    _rows = ["| Expression | Value (computed now) | What it shows |", "| :--- | :--- | :--- |"]
    _rows += [f"| `{e}` | `{v}` | {m} |" for e, v, m in evidence_rows()]
    mo.md("\n".join(_rows))
    return


@app.cell
def _(mo, textwrap):
    DIAMOND = textwrap.dedent('''
    log = []

    class Base:
        def hello(self):
            log.append("Base")

    class Left(Base):
        def hello(self):
            log.append("Left")
            super().hello()

    class Right(Base):
        def hello(self):
            log.append("Right")
            super().hello()

    class Child(Left, Right):
        def hello(self):
            log.append("Child")
            super().hello()

    Child().hello()
    ''').strip()
    _ns: dict = {}
    exec(DIAMOND, _ns)
    DIAMOND_TRACE = " → ".join(_ns["log"])
    DIAMOND_MRO = " → ".join(c.__name__ for c in _ns["Child"].__mro__)
    mo.accordion({
        "Go further: multiple inheritance and what super() really calls": mo.md(
            f"```python\n{DIAMOND}\n```\n\n"
            f"`Child.__mro__`: **{DIAMOND_MRO}**. Calls that ran: **{DIAMOND_TRACE}**.\n\n"
            "`super()` doesn't mean *my parent*: it means **the next class in `type(self).__mro__`** after the current one. "
            "Inside `Left`, on a `Child` object, that's `Right`, a class `Left` has never heard of. That's what makes cooperative "
            "multiple inheritance work, and why every `hello` must call `super()` for the chain to reach `Base` exactly once."
        )
    })
    return DIAMOND_MRO, DIAMOND_TRACE


@app.cell
def _(mo):
    mo.md(r"""
    ## 4 · The data model: your class, plugged into Python's syntax

    `len(x)`, `x[0]`, `a == b`, `for v in x`, `a + b`: each piece of syntax is Python calling a **dunder** (double-underscore) method on `type(x)`. Implement the method and your object joins in. Below, a `Bag` holding `[3, 1, 2]` implements the dunders you tick; every row is run live and shows which dunders actually ran.

    Try: untick `__contains__`, then `__iter__` (watch `2 in bag` fall back); untick `__bool__` (watch `bool` fall back to `__len__`); tick `__eq__` without `__hash__`.
    """)
    return


@app.cell
def _():
    DUNDERS = {
        "__len__": lambda self: len(self.items),
        "__bool__": lambda self: bool(self.items),
        "__getitem__": lambda self, i: self.items[i],
        "__contains__": lambda self, x: x in self.items,
        "__iter__": lambda self: iter(self.items),
        "__eq__": lambda self, other: self.items == other.items,
        "__lt__": lambda self, other: len(self.items) < len(other.items),
        "__repr__": lambda self: f"Bag({self.items})",
        "__add__": lambda self, other: type(self)(self.items + other.items),
        "__call__": lambda self: sum(self.items),
        "__hash__": lambda self: hash(tuple(self.items)),
    }
    BAG_EXPRESSIONS = [
        "len(bag)", "bool(bag)", "bag[0]", "2 in bag", "list(bag)", "bag == twin",
        "bag < bigger", "repr(bag)", "bag + twin", "bag()", "hash(bag)",
    ]

    def make_bag_class(chosen, log):
        def traced(name, fn):
            def method(*args):
                log.append(name)
                return fn(*args)
            return method

        def __init__(self, items):
            self.items = list(items)

        namespace = {"__init__": __init__}
        for name in chosen:
            namespace[name] = traced(name, DUNDERS[name])
        return type("Bag", (), namespace)

    return BAG_EXPRESSIONS, DUNDERS, make_bag_class


@app.cell
def _(DUNDERS, mo):
    chosen_dunders = mo.ui.multiselect(
        options=list(DUNDERS), value=[d for d in DUNDERS if d != "__hash__"], label="Bag implements", full_width=True,
    )
    chosen_dunders
    return (chosen_dunders,)


@app.cell
def _(BAG_EXPRESSIONS, make_bag_class, re):
    def run_bag_lab(chosen) -> tuple[list, bool]:
        log: list = []
        Bag = make_bag_class(chosen, log)
        env = {"bag": Bag([3, 1, 2]), "twin": Bag([3, 1, 2]), "bigger": Bag([1, 2, 3, 4])}
        rows = []
        for expr in BAG_EXPRESSIONS:
            log.clear()
            try:
                value = eval(expr, {}, env)
                ran = list(log)
                shown = "an int" if expr.startswith("hash") else re.sub(r"0x[0-9a-fA-F]+", "0x…", repr(value))
            except Exception as exc:
                ran = list(log)
                shown = f"{type(exc).__name__}: {exc}"
            collapsed = []
            for name in ran:
                if collapsed and collapsed[-1][0] == name:
                    collapsed[-1][1] += 1
                else:
                    collapsed.append([name, 1])
            calls = ", ".join(f"`{n}`" if c == 1 else f"`{n}` ×{c}" for n, c in collapsed) or "none (a default)"
            rows.append((expr, calls, shown))
        return rows, Bag.__hash__ is None

    return (run_bag_lab,)


@app.cell
def _(chosen_dunders, mo, run_bag_lab):
    _rows, _unhashable = run_bag_lab(chosen_dunders.value)
    _table = ["| Syntax | Dunders that ran | Result |", "| :--- | :--- | :--- |"]
    _table += [f"| `{e}` | {c} | `{r}` |" for e, c, r in _rows]
    _note = (
        "**`Bag.__hash__ is None`**: defining `__eq__` without `__hash__` makes the class unhashable on purpose, "
        "because the default hash (identity) would break the rule *equal objects must have equal hashes*."
        if _unhashable else
        "`Bag.__hash__` is set, so bags can go in sets and be dict keys."
    )
    mo.vstack([mo.md("\n".join(_table)), mo.callout(mo.md(_note), kind="warn" if _unhashable else "neutral")])
    return


@app.cell
def _(mo):
    mo.md(r"""
    **The fallbacks worth knowing** (each one is visible in the table above if you untick the right boxes):

    - `bool(x)`: `__bool__`, else `__len__() != 0`, else **always true**.
    - `v in x`: `__contains__`, else a scan with `__iter__`, else `__getitem__(0)`, `(1)`, … until `IndexError`.
    - `for v in x` / `list(x)`: `__iter__`, else the same `__getitem__` loop. (`list()` also calls `__len__`, just to size the list.)
    - `a == b`: `__eq__`, else **identity** (`a is b`). Two equal-looking bags are not equal until you say what equal means.
    - `repr(x)`: `__repr__`, else `<Bag object at 0x…>`. Always write `__repr__`: it's what you'll see in logs, debuggers and test failures.

    **In an interview:** "objects that compare equal must have equal hashes; hash only what can't change." Section 7 shows what goes wrong otherwise.

    ## 5 · Build it up

    | Need | Pattern |
    | :--- | :--- |
    | data plus the rules for it | `class` with `__init__` for state, methods that keep the invariant |
    | readable in logs, tests and the REPL | `__repr__` |
    | compare by value, use in sets / as dict keys | `__eq__` **and** `__hash__` on immutable fields (or `@dataclass(frozen=True)`) |
    | `sorted()`, `min()`, `heapq` | `__lt__` (or `@dataclass(order=True)`) |
    | act like a container: `len`, `in`, `for`, `[i]` | `__len__`, `__contains__`, `__iter__`, `__getitem__` |
    | a computed or read-only attribute with attribute syntax | `@property` (add `@x.setter` to validate writes) |
    | another way to construct (from a row, a dict, a file) | `@classmethod` that receives `cls` |
    | a helper that needs neither the object nor the class | a module-level function (or `@staticmethod`) |
    | reuse behaviour from another class | **hold** an instance of it (composition); inherit only for a true *is-a* |

    **The template, pseudo code first:** *class attributes (shared constants) → `__init__` stores per-object state (never a mutable default) → methods check the rule, then change state → properties for read-only views → a classmethod for each alternative constructor → `__repr__`.*

    ```python
    class Account:
        bank = "Chai Bank"                            # shared by every account

        def __init__(self, owner: str, balance: int = 0):
            self.owner = owner
            self._balance = balance

        @property
        def balance(self) -> int:                      # acct.balance, read-only
            return self._balance

        def deposit(self, amount: int) -> None:
            if amount <= 0:
                raise ValueError("deposit must be positive")
            self._balance += amount

        @classmethod
        def from_row(cls, row: str) -> "Account":     # cls is whichever class you called it on
            owner, balance = row.split(",")
            return cls(owner, int(balance))

        def __repr__(self) -> str:
            return f"{type(self).__name__}({self.owner!r}, {self._balance})"
    ```

    Why `@classmethod` and not `@staticmethod` for constructors, measured:
    """)
    return


@app.cell
def _(mo, textwrap):
    CONSTRUCTORS = textwrap.dedent('''
    class Account:
        def __init__(self, owner, balance=0):
            self.owner, self.balance = owner, balance

        @classmethod
        def from_row(cls, row):
            owner, balance = row.split(",")
            return cls(owner, int(balance))

        @staticmethod
        def parse(row):
            owner, balance = row.split(",")
            return Account(owner, int(balance))

    class Savings(Account):
        rate = 0.04
    ''').strip()
    _ns: dict = {}
    exec(CONSTRUCTORS, _ns)
    _Savings = _ns["Savings"]
    CONSTRUCTOR_RESULTS = {
        'type(Savings.from_row("Asha,100")).__name__': type(_Savings.from_row("Asha,100")).__name__,
        'type(Savings.parse("Asha,100")).__name__': type(_Savings.parse("Asha,100")).__name__,
    }
    mo.vstack([
        mo.md(f"```python\n{CONSTRUCTORS}\n```"),
        mo.md("\n".join(f"- `{k}` → **{v}**" for k, v in CONSTRUCTOR_RESULTS.items())
              + "\n\nThe classmethod builds whatever class it was called on, so subclasses inherit a working constructor. "
                "The staticmethod hard-codes `Account`, and a `Savings` caller silently gets the wrong type."),
    ])
    return (CONSTRUCTOR_RESULTS,)


@app.cell
def _(mo):
    mo.md(r"""
    ### `@dataclass` writes the boring dunders for you

    For classes that are mostly data (records, value objects, configs), `@dataclass` reads the annotated fields and generates the methods. What each variant gives you, checked by introspection and by trying it:
    """)
    return


@app.cell
def _(dataclasses, mo):
    def dataclass_report() -> list:
        class PlainPoint:
            def __init__(self, x, y):
                self.x, self.y = x, y

        @dataclasses.dataclass
        class Point:
            x: int
            y: int

        @dataclasses.dataclass(frozen=True)
        class FrozenPoint:
            x: int
            y: int

        @dataclasses.dataclass(order=True)
        class OrderedPoint:
            x: int
            y: int

        def attempt(fn):
            try:
                return fn()
            except Exception as exc:
                return type(exc).__name__

        def mutate(p):
            p.x = 9
            return "ok"

        rows = []
        for label, cls in (("plain class", PlainPoint), ("@dataclass", Point),
                           ("@dataclass(frozen=True)", FrozenPoint), ("@dataclass(order=True)", OrderedPoint)):
            p, same = cls(1, 2), cls(1, 2)
            rows.append((
                label,
                repr(p).split(".")[-1] if " object at " not in repr(p) else "<PlainPoint object at 0x…>",
                p == same,
                attempt(lambda: len({p, same})),
                attempt(lambda: [q.x for q in sorted([cls(3, 0), cls(1, 0)])]),
                attempt(lambda: mutate(cls(1, 2))),
            ))
        return rows

    _table = ["| Variant | `repr(p)` | `p == same` | `len({p, same})` | `sorted(...)` | `p.x = 9` |", "| :--- | :--- | :--- | :--- | :--- | :--- |"]
    _table += [f"| {a} | `{b}` | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in dataclass_report()]
    mo.vstack([
        mo.md("\n".join(_table)),
        mo.md("Read the rows as rules: plain `@dataclass` compares by value but is **unhashable** (it's mutable, see section 4); "
              "`frozen=True` makes it immutable **and** hashable, the right default for value objects and dict keys; "
              "`order=True` adds `<`, so lists of them sort field by field. Pydantic's `BaseModel` is the same idea plus validation."),
    ])
    return (dataclass_report,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 6 · Inheritance or composition?

    **Inheritance** says *a `Savings` **is an** `Account`*: it gets every attribute of the parent through the lookup chain, and must be usable anywhere an `Account` is. It's the right tool when a library is **designed** to be subclassed: `nn.Module`, `Exception`, `unittest.TestCase`, `ABC`s.

    **Composition** says *a `Retriever` **has an** embedder*: it stores another object and calls it. It's the default for everything else, for two reasons you can measure.

    **Cost 1: you inherit the parent's API and its internals.** Built-in `dict` methods are written in C and don't call your overrides; and everything the parent can do, callers can do to your object:
    """)
    return


@app.cell
def _(OrderedDict, UserDict, mo, textwrap):
    FRAGILE = [
        ("Override `__setitem__` on a `dict` subclass",
         textwrap.dedent('''
         class LowerDict(dict):
             def __setitem__(self, key, value):
                 super().__setitem__(key.lower(), value)

         d = LowerDict(A=1)       # __init__ doesn't call __setitem__
         d.update(B=2)            # neither does update
         d["C"] = 3
         result = sorted(d)
         ''').strip(),
         textwrap.dedent('''
         from collections import UserDict

         class LowerDict(UserDict):      # written in Python, on top of __setitem__
             def __setitem__(self, key, value):
                 super().__setitem__(key.lower(), value)

         d = LowerDict(A=1)
         d.update(B=2)
         d["C"] = 3
         result = sorted(d)
         ''').strip()),
        ("An LRU cache that *is an* OrderedDict",
         textwrap.dedent('''
         from collections import OrderedDict

         class LRU(OrderedDict):
             def __init__(self, capacity):
                 super().__init__()
                 self.capacity = capacity

             def put(self, key, value):
                 self[key] = value
                 self.move_to_end(key)
                 if len(self) > self.capacity:
                     self.popitem(last=False)

         cache = LRU(2)
         cache.update({"a": 1, "b": 2, "c": 3})   # a dict method: no eviction
         result = (len(cache), hasattr(cache, "update"))
         ''').strip(),
         textwrap.dedent('''
         from collections import OrderedDict

         class LRU:
             def __init__(self, capacity):
                 self.capacity = capacity
                 self._data = OrderedDict()         # has an OrderedDict

             def put(self, key, value):
                 self._data[key] = value
                 self._data.move_to_end(key)
                 if len(self._data) > self.capacity:
                     self._data.popitem(last=False)

             def __len__(self):
                 return len(self._data)

         cache = LRU(2)
         for key, value in {"a": 1, "b": 2, "c": 3}.items():
             cache.put(key, value)                  # put() is the only way in
         result = (len(cache), hasattr(cache, "update"))
         ''').strip()),
    ]

    def run_result(code: str):
        ns: dict = {"OrderedDict": OrderedDict, "UserDict": UserDict}
        exec(code, ns)
        return ns["result"]

    _parts = []
    for _title, _bad, _good in FRAGILE:
        _parts.append(mo.md(f"**{_title}.**"))
        _parts.append(mo.hstack([
            mo.md(f"*Inherit* → `result = {run_result(_bad)!r}`\n\n```python\n{_bad}\n```"),
            mo.md(f"*Fix* → `result = {run_result(_good)!r}`\n\n```python\n{_good}\n```"),
        ], align="start", gap=1, widths="equal"))
    mo.vstack(_parts)
    return FRAGILE, run_result


@app.cell
def _(mo):
    mo.md(r"""
    The capacity-2 cache holds 3 items: the invariant broke through a door (`update`) the subclass never meant to open. The composed version exposes exactly `put` and `__len__`, so there's no door. (This is the classic *fragile base class* problem.)

    **Cost 2: combinations multiply.** A retriever varies along two axes: how text becomes a vector, and how two vectors are scored. With inheritance, every **combination** is its own subclass. With composition, each **option** is one small piece, combined at runtime. Pick the options:
    """)
    return


@app.cell
def _(mo):
    embed_options = mo.ui.multiselect(options=["Words", "Trigrams", "Hashed", "Dense"], value=["Words", "Trigrams", "Hashed"], label="embedders")
    score_options = mo.ui.multiselect(options=["Cosine", "Dot", "Jaccard", "BM25"], value=["Cosine", "Dot"], label="scorers")
    mo.hstack([embed_options, score_options], justify="start", gap=2, wrap=True)
    return embed_options, score_options


@app.cell
def _(embed_options, mo, score_options):
    _e, _s = embed_options.value, score_options.value
    _cells = "".join(
        "<tr>" + "".join(
            f'<td style="border:1px solid rgba(127,127,127,.45);border-radius:6px;padding:4px 8px;font:12px ui-monospace,monospace">{e}{s}Retriever</td>'
            for s in _s) + "</tr>"
        for e in _e
    )
    _grid = f'<table style="border-collapse:separate;border-spacing:4px">{_cells}</table>' if _e and _s else "<em>pick at least one of each</em>"
    _pieces = ", ".join(f"`{x.lower()}`" for x in [*_e, *_s]) or "–"
    mo.hstack([
        mo.vstack([mo.md(f"**Inheritance: {len(_e)} × {len(_s)} = {len(_e) * len(_s)} subclasses**"), mo.Html(_grid)]),
        mo.vstack([mo.md(f"**Composition: 1 class + {len(_e)} + {len(_s)} = {1 + len(_e) + len(_s)} pieces**"),
                   mo.md(f"`Retriever(embed=..., score=...)` with any of: {_pieces}")]),
    ], align="start", gap=3, wrap=True)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Add a third axis (say, re-rankers) and inheritance multiplies again while composition just adds. Here's the composed version, running. The embedders and scorers are **plain functions**: in Python a "strategy" rarely needs its own class. (A class with one method and no state is a function.)
    """)
    return


@app.cell
def _(textwrap):
    RETRIEVER_CODE = textwrap.dedent('''
    import math
    from collections import Counter

    def words(text):
        return Counter(text.lower().replace(",", " ").replace(".", " ").split())

    def trigrams(text):
        padded = f"  {text.lower()} "
        return Counter(padded[i:i + 3] for i in range(len(padded) - 2))

    def dot(a, b):
        return sum(a[k] * b[k] for k in a.keys() & b.keys())

    def cosine(a, b):
        norm = math.sqrt(dot(a, a)) * math.sqrt(dot(b, b))
        return dot(a, b) / norm if norm else 0.0

    def jaccard(a, b):
        union = a.keys() | b.keys()
        return len(a.keys() & b.keys()) / len(union) if union else 0.0

    class Retriever:
        """Stores documents. HOW to embed and score is passed in."""

        def __init__(self, embed, score):
            self.embed = embed        # has an embedder: text -> Counter
            self.score = score        # has a scorer: (Counter, Counter) -> float
            self._docs = []           # (text, vector) pairs

        def add(self, text):
            self._docs.append((text, self.embed(text)))

        def search(self, query, k=3):
            q = self.embed(query)
            scored = [(round(self.score(q, vec), 3), text) for text, vec in self._docs]
            return sorted(scored, reverse=True)[:k]

        def __len__(self):
            return len(self._docs)

        def __contains__(self, text):
            return any(text == doc for doc, _vec in self._docs)
    ''').strip()
    CORPUS = [
        "In Python a dict lookup is O(1) on average.",
        "A set answers membership questions in O(1) on average.",
        "Two pointers walk a sorted array from both ends.",
        "A sliding window keeps a running sum over a contiguous range.",
        "Python notes: a long page about Python lists, dict comprehensions, lookup tables, sorting, recursion, generators, classes, decorators, testing, packaging, typing, logging and profiling in real projects.",
        "A class bundles data with the methods that keep it valid.",
        "Composition means an object holds other objects and delegates to them.",
        "Binary search halves a sorted range each step.",
    ]
    return CORPUS, RETRIEVER_CODE


@app.cell
def _(mo):
    query = mo.ui.text(value="python dict lookup", label="query", full_width=True)
    embedder = mo.ui.dropdown(options=["words", "trigrams"], value="words", label="embed")
    scorer = mo.ui.dropdown(options=["cosine", "dot", "jaccard"], value="cosine", label="score")
    mo.vstack([query, mo.hstack([embedder, scorer], justify="start", gap=2)])
    return embedder, query, scorer


@app.cell
def _(CORPUS, RETRIEVER_CODE, code_view, embedder, mo, query, scorer):
    def build_retriever(embed_name: str, score_name: str) -> object:
        ns: dict = {}
        exec(RETRIEVER_CODE, ns)
        store = ns["Retriever"](embed=ns[embed_name], score=ns[score_name])
        for doc in CORPUS:
            store.add(doc)
        return store

    _store = build_retriever(embedder.value, scorer.value)
    _hits = _store.search(query.value or " ", k=3)
    _table = ["| Score | Document |", "| :--- | :--- |"] + [f"| {s} | {t} |" for s, t in _hits]
    mo.vstack([
        mo.md(f"`Retriever(embed={embedder.value}, score={scorer.value})` · `len(store)` = {len(_store)} · top 3:"),
        mo.md("\n".join(_table)),
        mo.md("Switch **score** from `cosine` to `dot`: the long *Python notes* page jumps to the top, because a raw dot product rewards a document for being long (more words, more chances to match). "
              "Cosine divides by both lengths, which is why embedding search normalises vectors. Same class, different behaviour, no new subclass."),
        mo.accordion({"The code behind this search": code_view(RETRIEVER_CODE)}),
    ])
    return (build_retriever,)


@app.cell
def _(mo):
    mo.md(r"""
    When a collaborator has **several** methods, or holds state (a loaded model, a client), make it an object and describe what you need with a `typing.Protocol`. Any class with matching methods fits, no inheritance required (duck typing, checked by your type checker):

    ```python
    from typing import Protocol

    class Embedder(Protocol):
        def embed(self, text: str) -> list[float]: ...
        def dimensions(self) -> int: ...

    class Retriever:
        def __init__(self, embedder: Embedder): ...   # OpenAI, a local model, a fake in tests
    ```

    That last comment is the payoff for an engineer: the fake embedder in your tests is just another object with the same two methods.

    **Rule of thumb:** inherit when the parent was designed for it and *is-a* holds everywhere; otherwise pass the collaborator in.
    """)
    return


@app.cell
def _(recursion_guard):
    PITFALLS = [
        ("1 · A mutable class attribute is shared", "`members = []` runs once, when the class is created: every team appends to the same list.",
         "class Team:\n    members = []\n\n    def add(self, name):\n        self.members.append(name)\n\na, b = Team(), Team()\na.add('asha')\nresult = b.members\n",
         "class Team:\n    def __init__(self):\n        self.members = []\n\n    def add(self, name):\n        self.members.append(name)\n\na, b = Team(), Team()\na.add('asha')\nresult = b.members\n"),
        ("2 · A mutable default argument", "The default list is built once, when `def` runs, and shared by every call that doesn't pass one.",
         "class Basket:\n    def __init__(self, items=[]):\n        self.items = items\n\na, b = Basket(), Basket()\na.items.append('apple')\nresult = b.items\n",
         "class Basket:\n    def __init__(self, items=None):\n        self.items = list(items) if items is not None else []\n\na, b = Basket(), Basket()\na.items.append('apple')\nresult = b.items\n"),
        ("3 · `self.issued += 1` never touches the class counter", "It reads the class value, then **writes an instance attribute** that shadows it.",
         "class Ticket:\n    issued = 0\n\n    def __init__(self):\n        self.issued += 1\n\nTicket(); Ticket(); Ticket()\nresult = Ticket.issued\n",
         "class Ticket:\n    issued = 0\n\n    def __init__(self):\n        type(self).issued += 1\n\nTicket(); Ticket(); Ticket()\nresult = Ticket.issued\n"),
        ("4 · `__eq__` without `__hash__`", "Python sets `__hash__ = None`, so the objects can't go in a set or be dict keys.",
         "class Point:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\n    def __eq__(self, other):\n        return (self.x, self.y) == (other.x, other.y)\n\nresult = len({Point(1, 2), Point(1, 2)})\n",
         "class Point:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\n    def __eq__(self, other):\n        return (self.x, self.y) == (other.x, other.y)\n\n    def __hash__(self):\n        return hash((self.x, self.y))\n\nresult = len({Point(1, 2), Point(1, 2)})\n"),
        ("5 · Hashing fields that change", "The set filed `p` under its old hash; after the change it looks in the wrong bucket.",
         "class Point:\n    def __init__(self, x, y):\n        self.x, self.y = x, y\n\n    def __eq__(self, other):\n        return (self.x, self.y) == (other.x, other.y)\n\n    def __hash__(self):\n        return hash((self.x, self.y))\n\np = Point(1, 2)\nseen = {p}\np.x = 99\nresult = p in seen\n",
         "from dataclasses import dataclass, replace\n\n@dataclass(frozen=True)\nclass Point:\n    x: int\n    y: int\n\np = Point(1, 2)\nseen = {p}\nmoved = replace(p, x=99)   # a new point; p can't change\nresult = p in seen\n"),
        ("6 · A property setter that assigns to itself", "`self.celsius = value` inside the setter calls the setter again, forever.",
         "class Temperature:\n    def __init__(self, celsius):\n        self.celsius = celsius\n\n    @property\n    def celsius(self):\n        return self._celsius\n\n    @celsius.setter\n    def celsius(self, value):\n        self.celsius = value\n\nresult = Temperature(20).celsius\n",
         "class Temperature:\n    def __init__(self, celsius):\n        self.celsius = celsius\n\n    @property\n    def celsius(self):\n        return self._celsius\n\n    @celsius.setter\n    def celsius(self, value):\n        if value < -273.15:\n            raise ValueError('below absolute zero')\n        self._celsius = value\n\nresult = Temperature(20).celsius\n"),
        ("7 · A subclass that skips `super().__init__()`", "The parent's `__init__` never runs, so its attributes never exist. (`nn.Module` refuses to work without it.)",
         "class Account:\n    def __init__(self, owner):\n        self.owner = owner\n\nclass Savings(Account):\n    def __init__(self, owner, rate):\n        self.rate = rate\n\nresult = Savings('Asha', 0.04).owner\n",
         "class Account:\n    def __init__(self, owner):\n        self.owner = owner\n\nclass Savings(Account):\n    def __init__(self, owner, rate):\n        super().__init__(owner)\n        self.rate = rate\n\nresult = Savings('Asha', 0.04).owner\n"),
    ]

    def run_program(code: str) -> str:
        _ns: dict = {}
        try:
            with recursion_guard():
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
        _details[_title] = mo.md(f"{_why}\n\n**Buggy:**\n```python\n{_bad}```\n**Fixed:**\n```python\n{_good}```")
    mo.vstack([mo.md("## 7 · Pitfalls, run live"), mo.md("\n".join(_rows)), mo.accordion(_details)])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8 · Practice: worked → faded → solo

    Interview "design" problems are class-design problems: choose the state, keep the invariant in the methods. Your class is tested the way LeetCode does it: a list of operations and their arguments, and the list of what each call returned.
    """)
    return


@app.cell
def _(Case, random):
    HARNESS_OPS = '''

    def _judge(ops, args):
        out, obj = [], None
        for op, a in zip(ops, args):
            if obj is None:
                obj = globals()[op](*a)
                out.append(None)
            else:
                out.append(getattr(obj, op)(*a))
        return out
    '''

    CASES_MIN = [
        Case((["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"], [[], [-2], [0], [-3], [], [], [], []]),
             [None, None, None, None, -3, None, 0, -2], label="LeetCode example"),
        Case((["MinStack", "push", "push", "push", "getMin", "pop", "getMin"], [[], [1], [1], [2], [], [], []]),
             [None, None, None, None, 1, None, 1], label="duplicate minimum survives one pop"),
        Case((["MinStack", "push", "push", "pop", "getMin", "top"], [[], [5], [3], [], [], []]),
             [None, None, None, None, 5, 5], label="min goes back up after a pop"),
        Case((["MinStack", "push", "getMin", "top"], [[], [-7], [], []]), [None, None, -7, -7], label="single element"),
    ]
    SOLUTION_MIN = '''
    class MinStack:
        def __init__(self):
            self.stack = []                       # (value, min of everything up to here)

        def push(self, val: int) -> None:
            smallest = min(val, self.stack[-1][1]) if self.stack else val
            self.stack.append((val, smallest))

        def pop(self) -> None:
            self.stack.pop()                      # the previous min comes back for free

        def top(self) -> int:
            return self.stack[-1][0]

        def getMin(self) -> int:
            return self.stack[-1][1]
    '''
    STUB_MIN = '''class MinStack:
        def __init__(self):
            self.stack = []   # what should each entry hold so getMin is O(1)?

        def push(self, val: int) -> None:
            ...

        def pop(self) -> None:
            ...

        def top(self) -> int:
            ...

        def getMin(self) -> int:
            ...
    '''

    HARNESS_VEC = '''

    def _judge(check, x, y):
        v, w = Vector2(x, y), Vector2(1, 1)
        checks = {
            "repr(v)": lambda: repr(v),
            "v == Vector2(x, y)": lambda: v == Vector2(x, y),
            "v == w": lambda: v == w,
            "v == 'text'": lambda: v == "text",
            "len({v, Vector2(x, y)})": lambda: len({v, Vector2(x, y)}),
            "tuple(v + w)": lambda: tuple(v + w),
            "tuple(v * 3)": lambda: tuple(v * 3),
            "tuple(3 * v)": lambda: tuple(3 * v),
            "abs(v)": lambda: abs(v),
            "bool(v)": lambda: bool(v),
        }
        return checks[check]()
    '''
    _vec = [
        ("repr(v)", 3, 4, "Vector2(3, 4)"), ("v == Vector2(x, y)", 3, 4, True), ("v == w", 3, 4, False),
        ("v == 'text'", 3, 4, False), ("len({v, Vector2(x, y)})", 3, 4, 1), ("tuple(v + w)", 3, 4, (4, 5)),
        ("tuple(v * 3)", 3, 4, (9, 12)), ("tuple(3 * v)", 3, 4, (9, 12)), ("abs(v)", 3, 4, 5.0),
        ("bool(v)", 3, 4, True), ("bool(v)", 0, 0, False), ("abs(v)", 0, 0, 0.0),
    ]
    CASES_VEC = [Case((c, x, y), want, label=f"{c}  with v = Vector2({x}, {y})") for c, x, y, want in _vec]
    SOLUTION_VEC = '''
    import math

    class Vector2:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __repr__(self):
            return f"Vector2({self.x!r}, {self.y!r})"

        def __iter__(self):                  # lets you write x, y = v
            return iter((self.x, self.y))

        def __eq__(self, other):
            if not isinstance(other, Vector2):
                return NotImplemented        # "I don't know": Python tries the other side, then identity
            return (self.x, self.y) == (other.x, other.y)

        def __hash__(self):
            return hash((self.x, self.y))    # equal vectors -> equal hashes

        def __add__(self, other):
            return Vector2(self.x + other.x, self.y + other.y)

        def __mul__(self, scalar):
            return Vector2(self.x * scalar, self.y * scalar)

        def __rmul__(self, scalar):          # 3 * v: int.__mul__ gives up, Python tries this
            return self * scalar

        def __abs__(self):
            return math.hypot(self.x, self.y)

        def __bool__(self):
            return bool(abs(self))
    '''
    STUB_VEC = '''import math

    class Vector2:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __repr__(self):
            return f"Vector2({self.x!r}, {self.y!r})"

        def __iter__(self):                  # lets you write x, y = v
            return iter((self.x, self.y))

        def __eq__(self, other):
            # equal when both coordinates match; for a non-Vector2 return NotImplemented
            ...

        def __hash__(self):
            # equal vectors must hash equal
            ...

        def __add__(self, other):
            ...

        def __mul__(self, scalar):
            ...

        def __rmul__(self, scalar):          # 3 * v
            ...

        def __abs__(self):
            # the length: math.hypot
            ...

        def __bool__(self):
            # the zero vector is falsy
            ...
    '''

    def lru_oracle(ops, args):
        """Obviously-correct (and slow) LRU: a list in recency order."""
        out, capacity, order, data = [], 0, [], {}
        for op, a in zip(ops, args):
            if op == "LRUCache":
                capacity = a[0]
                out.append(None)
            elif op == "get":
                if a[0] in data:
                    order.remove(a[0])
                    order.append(a[0])
                    out.append(data[a[0]])
                else:
                    out.append(-1)
            else:
                key, value = a
                if key in data:
                    order.remove(key)
                elif len(data) == capacity:
                    del data[order.pop(0)]
                data[key] = value
                order.append(key)
                out.append(None)
        return out

    def random_lru_ops(n_ops, capacity, n_keys, seed):
        rng = random.Random(seed)
        ops, args = ["LRUCache"], [[capacity]]
        for _ in range(n_ops):
            key = rng.randrange(n_keys)
            if rng.random() < 0.5:
                ops.append("get")
                args.append([key])
            else:
                ops.append("put")
                args.append([key, rng.randrange(1000)])
        return ops, args

    _big = random_lru_ops(8000, 100, 300, seed=146)
    CASES_LRU = [
        Case((["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"],
              [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]),
             [None, None, None, 1, None, -1, None, -1, 3, 4], label="LeetCode example"),
        Case((["LRUCache", "put", "get", "put", "get", "get"], [[1], [2, 1], [2], [3, 2], [2], [3]]),
             [None, None, 1, None, -1, 2], label="capacity 1"),
        Case((["LRUCache", "put", "put", "put", "put", "get", "get"], [[2], [1, 1], [2, 2], [1, 10], [3, 3], [2], [1]]),
             [None, None, None, None, None, -1, 10], label="updating a key refreshes it (and doesn't evict)"),
        Case((["LRUCache", "put", "put", "get", "put", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [1]]),
             [None, None, None, 1, None, -1, 1], label="get refreshes a key"),
        Case(_big, lru_oracle(*_big), label="8,000 random operations, capacity 100 (a pure-Python scan per call runs out of budget)"),
    ]
    SOLUTION_LRU = '''
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.data = OrderedDict()            # has an OrderedDict: oldest first

        def get(self, key: int) -> int:
            if key not in self.data:
                return -1
            self.data.move_to_end(key)           # now the most recent
            return self.data[key]

        def put(self, key: int, value: int) -> None:
            if key in self.data:
                self.data.move_to_end(key)
            self.data[key] = value
            if len(self.data) > self.capacity:
                self.data.popitem(last=False)    # evict the least recent
    '''
    STUB_LRU = '''class LRUCache:
        def __init__(self, capacity: int):
            ...

        def get(self, key: int) -> int:
            ...

        def put(self, key: int, value: int) -> None:
            ...
    '''
    SCAN_LRU = '''
    class LRUCache:
        def __init__(self, capacity):
            self.capacity, self.keys, self.values = capacity, [], {}

        def _touch(self, key):
            for i in range(len(self.keys)):          # a Python-level scan: O(capacity) per call
                if self.keys[i] == key:
                    del self.keys[i]
                    break
            self.keys.append(key)

        def get(self, key):
            if key not in self.values:
                return -1
            self._touch(key)
            return self.values[key]

        def put(self, key, value):
            if key not in self.values and len(self.values) == self.capacity:
                del self.values[self.keys.pop(0)]
            self.values[key] = value
            self._touch(key)
    '''
    return (
        CASES_LRU,
        CASES_MIN,
        CASES_VEC,
        HARNESS_OPS,
        HARNESS_VEC,
        SCAN_LRU,
        SOLUTION_LRU,
        SOLUTION_MIN,
        SOLUTION_VEC,
        STUB_LRU,
        STUB_MIN,
        STUB_VEC,
        lru_oracle,
        random_lru_ops,
    )


@app.cell
def _(SOLUTION_MIN, STUB_MIN, mo, solution):
    min_editor = mo.ui.code_editor(value=STUB_MIN, language="python", min_height=260)
    min_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md(r"""
    ### Worked: LC 155 · Min Stack

    `push`, `pop`, `top` and `getMin`, **each O(1)**.

    - **Brute force:** a plain list, and `getMin` returns `min(self.stack)`. Correct, but O(n) per call.
    - **Bottleneck:** every `getMin` rescans the whole stack, although only the top ever changes.
    - **Insight (first principles):** a stack only changes at the top, so *the minimum of everything below an entry never changes while that entry is on the stack*. Store it **with** each entry: `(value, min so far)`. Popping restores the previous minimum for free.
    - **Pseudo code:** push → `smallest = min(val, top's smallest)` (or `val` if empty), append the pair; pop → pop; top → `stack[-1][0]`; getMin → `stack[-1][1]`.
    - **Edge cases:** duplicate minimums, a pop that removes the minimum, a single element.

    Read the solution, close it, write it from memory."""),
        solution(SOLUTION_MIN, "Show the worked solution"), min_editor, min_run,
    ])
    return min_editor, min_run


@app.cell
def _(CASES_MIN, HARNESS_OPS, check, min_editor, min_run, mo):
    mo.stop(not min_run.value, mo.md("_Write your class, then press **Run tests**._"))
    check(min_editor.value + HARNESS_OPS, "_judge", CASES_MIN)
    return


@app.cell
def _(SOLUTION_VEC, STUB_VEC, mo, solution):
    vec_editor = mo.ui.code_editor(value=STUB_VEC, language="python", min_height=420)
    vec_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Faded: a `Vector2` value object\n\n`__init__`, `__repr__` and `__iter__` are done. Fill in the other dunders so vectors compare, hash, add, scale (from both sides), measure and test as false when zero. "
              "The `v == 'text'` case is the edge that breaks first attempts."),
        vec_editor, vec_run, solution(SOLUTION_VEC),
    ])
    return vec_editor, vec_run


@app.cell
def _(CASES_VEC, HARNESS_VEC, check, mo, vec_editor, vec_run):
    mo.stop(not vec_run.value, mo.md("_Fill in the dunders, then press **Run tests**._"))
    check(vec_editor.value + HARNESS_VEC, "_judge", CASES_VEC)
    return


@app.cell
def _(SOLUTION_LRU, STUB_LRU, mo, solution):
    lru_editor = mo.ui.code_editor(value=STUB_LRU, language="python", min_height=200)
    lru_run = mo.ui.run_button(label="Run tests")
    mo.vstack([
        mo.md("### Solo: LC 146 · LRU Cache\n\n`get(key)` returns the value or `-1`; `put(key, value)` inserts or updates, and when the cache is over capacity it evicts the **least recently used** key. Both O(1). "
              "Every `get` and `put` counts as a use. Section 6 already showed you which design to pick. The last test is 8,000 operations and doubles as a time limit.\n\n"
              "After it passes, the interview follow-up: build it without `OrderedDict`, from a dict plus a doubly linked list."),
        lru_editor, lru_run, solution(SOLUTION_LRU),
    ])
    return lru_editor, lru_run


@app.cell
def _(CASES_LRU, HARNESS_OPS, check, lru_editor, lru_run, mo):
    mo.stop(not lru_run.value, mo.md("_Write it, then press **Run tests**._"))
    check(lru_editor.value + HARNESS_OPS, "_judge", CASES_LRU)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 9 · Recall: close everything and answer from memory
    """)
    return


@app.cell
def _(mo):
    mo.accordion({
        "1. What is an object, in one sentence, and where do its methods live?": mo.md("A dict of its own data (`vars(obj)`) plus a link to its class (`type(obj)`). Methods live once, on the class."),
        "2. In what order does `obj.name` search, and what ends the search?": mo.md("The object's dict, then each class in `type(obj).__mro__` (its class, parents, … `object`). The first hit wins; no hit → `AttributeError`. (A property on the class is checked before the object's dict.)"),
        "3. What does `acct.deposit(50)` turn into?": mo.md("`Account.deposit(acct, 50)`: the function is found on the class and bound to the object, which becomes `self`."),
        "4. Why does `len(x)` ignore an `__len__` set on the object?": mo.md("Syntax looks special methods up on the **type**, skipping the instance dict."),
        "5. Defining `__eq__` did what to hashing, why, and what's the safe fix?": mo.md("It set `__hash__` to `None` (unhashable), because the identity hash would break *equal ⇒ same hash*. Add `__hash__` over the same **immutable** fields, or use `@dataclass(frozen=True)`."),
        "6. `@classmethod` vs `@staticmethod` for an alternative constructor?": mo.md("Classmethod: it receives `cls`, so `Savings.from_row(...)` builds a `Savings`. A staticmethod hard-codes the class."),
        "7. Give two concrete reasons to prefer composition.": mo.md("A subclass inherits the parent's whole API and internals (the `dict.update` / `LRU(OrderedDict)` leaks), and combinations multiply (m × n subclasses vs m + n pieces)."),
        "8. What does `super()` call?": mo.md("The next class after the current one in `type(self).__mro__`, not necessarily the parent."),
        "9. Name three class-level traps.": mo.md("A mutable class attribute or default argument (shared), `self.count += 1` (creates an instance attribute), a setter assigning to its own property (infinite recursion), skipping `super().__init__()`."),
    })
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 10 · Go deeper

    - **Watch first:** Raymond Hettinger, [Object Oriented Programming from scratch (four times)](https://www.youtube.com/watch?v=8moWQ1561FY) (PyCon Estonia 2020). It builds OOP out of dicts and namespaces, exactly this notebook's model; then [Python's Class Development Toolkit](https://www.youtube.com/watch?v=HTLu2DFOdTg) (PyCon 2013) grows one class through every tool in section 5. More in [this curated list of his OOP talks](https://death.andgravity.com/hettinger).
    - **Composition:** Brandon Rhodes, [The Composition Over Inheritance Principle](https://python-patterns.guide/gang-of-four/composition-over-inheritance/): the same m × n argument with a `Logger`, solved with Adapter, Bridge and Decorator. Then Jack Diederich, [Stop Writing Classes](https://www.youtube.com/watch?v=o9pEzgHorH0) (PyCon 2012), for when *not* to write one.
    - **Reference:** [Data model](https://docs.python.org/3/reference/datamodel.html) (every dunder; see *Special method lookup*), [Descriptor HowTo](https://docs.python.org/3/howto/descriptor.html) (how methods, properties and `classmethod` really work), [dataclasses](https://docs.python.org/3/library/dataclasses.html), [super() considered super!](https://rhettinger.wordpress.com/2011/05/26/super-considered-super/).
    - **Read:** [Real Python: Inheritance and Composition](https://realpython.com/inheritance-composition-python/); *Fluent Python*, 2nd ed. (Ramalho): ch. 1 (data model), 5 (data classes), 11 (a Pythonic object), 14 (inheritance: for better or for worse).
    - **Reps:** LC [705 Design HashSet](https://leetcode.com/problems/design-hashset/), [232 Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/), [707 Design Linked List](https://leetcode.com/problems/design-linked-list/), [155 Min Stack](https://leetcode.com/problems/min-stack/), [146 LRU Cache](https://leetcode.com/problems/lru-cache/).

    **Previous:** [Decorators](https://himanshubhardwaj2398.github.io/Learning-Exploration-Random/notebooks/decorators.html), where `@property` and `@classmethod` come from.
    """)
    return


@app.cell
def _(
    BAG_EXPRESSIONS,
    CASES_LRU,
    CASES_MIN,
    CASES_VEC,
    CLASS_ATTEMPTS,
    CLASS_VERSION,
    CONSTRUCTOR_RESULTS,
    CORPUS,
    Case,
    DIAMOND_MRO,
    DIAMOND_TRACE,
    DUNDERS,
    FRAGILE,
    HARNESS_OPS,
    HARNESS_VEC,
    LOOKUP_NAMES,
    PITFALLS,
    SCAN_LRU,
    SOLUTION_LRU,
    SOLUTION_MIN,
    SOLUTION_VEC,
    STUB_LRU,
    STUB_MIN,
    STUB_VEC,
    assert_cases,
    build_lookup_world,
    build_retriever,
    dataclass_report,
    describe_lookup,
    lru_oracle,
    namespace_chain,
    random_lru_ops,
    run_attempts,
    run_bag_lab,
    run_cases,
    run_program,
    run_result,
):
    def test_answer_keys_pass():
        assert_cases(SOLUTION_MIN + HARNESS_OPS, "_judge", CASES_MIN)
        assert_cases(SOLUTION_VEC + HARNESS_VEC, "_judge", CASES_VEC)
        assert_cases(SOLUTION_LRU + HARNESS_OPS, "_judge", CASES_LRU)

    def test_stubs_do_not_pass_yet():
        for stub, harness, cases in ((STUB_MIN, HARNESS_OPS, CASES_MIN), (STUB_VEC, HARNESS_VEC, CASES_VEC), (STUB_LRU, HARNESS_OPS, CASES_LRU)):
            assert not all(r.passed for r in run_cases(stub + harness, "_judge", cases))

    def test_lru_answer_key_matches_the_oracle_on_random_runs():
        for seed in range(5):
            ops, args = random_lru_ops(300, capacity=1 + seed * 3, n_keys=20, seed=seed)
            assert_cases(SOLUTION_LRU + HARNESS_OPS, "_judge", [Case((ops, args), lru_oracle(ops, args))])

    def test_a_python_scan_lru_is_right_but_hits_the_budget():
        results = run_cases(SCAN_LRU + HARNESS_OPS, "_judge", CASES_LRU)
        assert all(r.passed for r in results[:-1])
        assert not results[-1].passed and "too slow" in results[-1].error

    def test_class_version_enforces_the_rules():
        outcome = {s: o for s, _w, o, _b in run_attempts(CLASS_VERSION, CLASS_ATTEMPTS)}
        assert outcome["acct.deposit(100)"] == "ok"
        assert outcome["acct.balnce = 500"].startswith("AttributeError")
        assert outcome["acct.balance = -900"].startswith("AttributeError")
        assert outcome["acct.withdraw(1000)"].startswith("ValueError")

    def test_lookup_chain_finds_each_name_where_the_text_says():
        world = build_lookup_world(False)
        titles = [t for t, _s, _e in namespace_chain(world["acct"])]
        assert titles == ["acct", "Savings", "Account", "object"]
        for name in LOOKUP_NAMES:
            describe_lookup(world, name)
        assert "AttributeError" in describe_lookup(world, "overdraft")
        shadowed = build_lookup_world(True)
        assert "own dict" in describe_lookup(shadowed, "rate") and shadowed["Savings"].rate == 0.04

    def test_bag_lab_fallbacks():
        everything = [d for d in DUNDERS if d != "__hash__"]
        rows, unhashable = run_bag_lab(everything)
        assert unhashable
        by_expr = {e: (c, r) for e, c, r in rows}
        assert by_expr["2 in bag"][0] == "`__contains__`"
        no_contains = {e: (c, r) for e, c, r in run_bag_lab([d for d in everything if d != "__contains__"])[0]}
        assert no_contains["2 in bag"] == ("`__iter__`", "True")
        no_iter = {e: (c, r) for e, c, r in run_bag_lab([d for d in everything if d not in ("__contains__", "__iter__")])[0]}
        assert no_iter["2 in bag"][0].startswith("`__getitem__`")
        no_bool = {e: (c, r) for e, c, r in run_bag_lab([d for d in everything if d != "__bool__"])[0]}
        assert no_bool["bool(bag)"][0] == "`__len__`"
        bare, bare_unhashable = run_bag_lab([])
        assert not bare_unhashable and dict((e, r) for e, _c, r in bare)["bag == twin"] == "False"
        assert len(BAG_EXPRESSIONS) == len(rows)

    def test_constructor_claims():
        assert list(CONSTRUCTOR_RESULTS.values()) == ["Savings", "Account"]

    def test_dataclass_claims():
        rows = {r[0]: r for r in dataclass_report()}
        assert rows["@dataclass"][3] == "TypeError"                     # unhashable
        assert rows["@dataclass(frozen=True)"][3] == 1 and rows["@dataclass(frozen=True)"][5] == "FrozenInstanceError"
        assert rows["@dataclass(order=True)"][4] == [1, 3]
        assert rows["plain class"][2] is False

    def test_fragile_base_class_claims():
        (_t1, bad1, good1), (_t2, bad2, good2) = FRAGILE
        assert run_result(bad1) == ["A", "B", "c"] and run_result(good1) == ["a", "b", "c"]
        assert run_result(bad2) == (3, True) and run_result(good2) == (2, False)

    def test_dot_rewards_the_long_document_and_cosine_does_not():
        long_doc = next(d for d in CORPUS if d.startswith("Python notes"))
        by_dot = [t for _s, t in build_retriever("words", "dot").search("python dict lookup", k=3)]
        by_cos = [t for _s, t in build_retriever("words", "cosine").search("python dict lookup", k=3)]
        assert by_dot[0] == long_doc and by_cos[0] != long_doc

    def test_every_pitfall_differs_from_its_fix():
        for title, _why, bad, good in PITFALLS:
            assert run_program(bad) != run_program(good), title
        assert run_program(PITFALLS[5][2]).startswith("RecursionError")

    def test_super_follows_the_mro():
        assert DIAMOND_MRO == "Child → Left → Right → Base → object"
        assert DIAMOND_TRACE == "Child → Left → Right → Base"

    return


if __name__ == "__main__":
    app.run()
