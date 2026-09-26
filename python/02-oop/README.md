# Object-oriented Python

> An object is a dict of its own data plus a link to its class; `obj.name` searches the object, then its class, then the parents (the MRO). Methods, `self`, properties, `super()` and dunder methods are all rules about that one search.

Kind: concept · Status: new

**Notebook:** [oop.py](oop.py) covers:
- dict-and-functions vs a class, with the rules run live
- an attribute-lookup stepper over the MRO
- evidence that `acct.deposit(50)` is `Account.deposit(acct, 50)`
- a dunder lab that shows which special method each piece of syntax calls, and the fallbacks
- what `@dataclass` generates
- composition vs inheritance, measured
- live pitfalls
- Min Stack, `Vector2` and LRU Cache exercises

Run `marimo edit python/02-oop/oop.py` locally, or open it on the site.

## Spot it
- **State plus a rule that must always hold** (a balance ≥ 0, a cache ≤ capacity): use a class that owns both, and every change goes through a method.
- **You want `len`, `in`, `for`, `==`, `sorted`, `{}` to work on your objects:** write dunder methods, or use `@dataclass`.
- **Value objects used as dict keys or in sets** (points, money, IDs): use `@dataclass(frozen=True)`.
- **Inheritance or composition:** inherit only when *is-a* holds everywhere and the parent was built for it (`nn.Module`, `Exception`). Otherwise hold the collaborator and pass it in.
- **A class with one method and no state** is a function.
- **Interview "design" problems** (Min Stack, LRU Cache, Design HashMap) are class design: pick the state, then keep the invariant inside the methods.

## Template
```python
class Account:
    bank = "Chai Bank"                          # class attribute: shared, treat as constant

    def __init__(self, owner, balance=0, tags=None):
        self.owner = owner                       # per-object state
        self._balance = balance                  # "_" = internal, use the methods
        self.tags = list(tags) if tags is not None else []   # never a mutable default

    @property
    def balance(self):                           # read-only view
        return self._balance

    def deposit(self, amount):                   # check the rule, then change state
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    @classmethod
    def from_row(cls, row):                      # alternative constructor; subclasses get it too
        owner, balance = row.split(",")
        return cls(owner, int(balance))

    def __repr__(self):
        return f"{type(self).__name__}({self.owner!r}, {self._balance})"


@dataclass(frozen=True)
class Point:                                     # __init__, __repr__, __eq__, __hash__ for free
    x: int
    y: int
```

## Traps (the ones that bite)
- A mutable class attribute (`members = []`) is shared by every instance.
- A mutable default argument in `__init__` is shared by every call.
- `self.count += 1` creates an instance attribute, so the class counter never moves. Use `type(self).count += 1`.
- `__eq__` without `__hash__` makes the class unhashable.
- Hashing fields that change loses objects inside sets.
- A property setter that assigns to its own name recurses forever. Store the value in `self._x`.
- Subclassing `dict` or `list`: `update()` and `__init__` skip your overrides. Use `UserDict` or composition.
- Skipping `super().__init__()` in a subclass means the parent's attributes never exist.

## Ladder
| # | Exercise | Stage | Done |
| :--- | :--- | :--- | :--- |
| 155 | Min Stack | worked | |
| — | `Vector2` value object (dunders) | faded | |
| 146 | LRU Cache | solo | |
| 705, 232, 707 | Design HashSet, Queue using Stacks, Design Linked List | graded | |
| 146 | LRU Cache without `OrderedDict` (dict + doubly linked list) | stretch | |

## Questions
<!-- question notebooks for this topic live in questions/; tools/new_topic.py adds them here -->

## Review log
Counted from the day this topic reaches `Status: solid`:
- [ ] +2 days: LRU Cache from a blank file, then explain out loud why `class LRU(OrderedDict)` leaks
- [ ] +5 days: explain attribute lookup with the MRO, then the `__eq__` / `__hash__` contract
- [ ] +12 days: LC 707 Design Linked List, plus `__len__` and `__iter__` for it
- [ ] +26 days: read how `nn.Module` uses `__setattr__` / `__getattr__` to register layers, and explain it

## Resources
- **Watch:** Raymond Hettinger, [OOP from scratch (four times)](https://www.youtube.com/watch?v=8moWQ1561FY). It builds OOP out of dicts, the same model as the notebook. Then watch [Python's Class Development Toolkit](https://www.youtube.com/watch?v=HTLu2DFOdTg).
- **Composition:** Brandon Rhodes, [Composition Over Inheritance](https://python-patterns.guide/gang-of-four/composition-over-inheritance/). Read up to the Bridge pattern. After that, [Stop Writing Classes](https://www.youtube.com/watch?v=o9pEzgHorH0).
- **Reference:**
  - [Data model](https://docs.python.org/3/reference/datamodel.html): look up a dunder when you need it, don't read it top to bottom.
  - [Descriptor HowTo](https://docs.python.org/3/howto/descriptor.html): how methods and properties bind.
  - [super() considered super!](https://rhettinger.wordpress.com/2011/05/26/super-considered-super/)
- *Fluent Python*, 2nd ed.: chapters 1, 5, 11 and 14.
