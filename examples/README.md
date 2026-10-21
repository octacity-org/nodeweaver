# Examples

Small Python projects used as input for NodeWeaver's parser, the `scan` command, and their tests (including the golden-file tests in #14). Keep them small: each file exists to show specific constructs.

| Sample | What it covers |
| --- | --- |
| `sample_basic/` | Every import form, classes with methods, every call case from #12, nested functions, lambdas, a decorator, and async code. |
| `sample_package/` | A package with `__init__.py` files and relative imports at different depths. |
| `sample_broken/` | A file with an intentional syntax error, to check that the parser does not crash. |

## sample_basic

- `main.py`: the import forms `import x`, `import x.y`, `import x as y`, `from x import a, b`, `from x import a as b`, and `from x import *`, plus most call forms.
- `models.py`: `Item` and its subclass `DiscountedItem`, with calls on `self` and `super()` and a call in the class body.
- `helpers.py`: plain functions, including one with a nested function. `main.py` imports it with `import *`, so it defines `__all__`.
- `routes.py`: a decorator that is a call, `async` functions, and `await`.

Run them with `cd examples/sample_basic`, then `python main.py` or `python routes.py`.

### Call cases from #12

| Case | Where |
| --- | --- |
| Simple call `f()` | `main.py`: `build_items()` |
| Method call `obj.m()` | `main.py`: `items[0].describe()` |
| Call on self `self.save()` | `models.py`: `Item.update_price` |
| Module call `mod.f()` | `main.py`: `json.dumps(summary)` |
| Chained call `a.b().c()` | `main.py`: `col.Counter(...).most_common(1)` |
| Nested call `f(g(x))` | `main.py`: `make_label(str(cheapest.name))` |
| Call inside a lambda | `main.py`: `lambda item: item.total(1)` |
| Call inside an inner function | `main.py`: `summarize`; `helpers.py`: `clean` |
| Call inside a comprehension | `main.py`: `[summarize(item) for item in items]` |
| Module-level call (`caller` is `null`) | `main.py`: `main()`; `routes.py`: `app = App()` |
| Call in a class body, outside a method | `models.py`: `frozenset(["food", "drink"])` |
| Await on a call `await foo()` | `routes.py`: `await load_items()` |
| Call on a non-name expression | `main.py`: `handlers[0](3.14159)`; `models.py`: `super().__init__(name, price)` |
| Decorator that is a call | `routes.py`: `@app.route("/items")` |

## sample_package

```text
pkg/
  __init__.py         from .core import run
  core.py             from . import utils, from .utils.strings import shout
  utils/
    __init__.py       from .strings import greet, shout
    strings.py        from .. import VERSION
```

Run it with `cd examples/sample_package && python -c "import pkg; print(pkg.run('octacity'))"`.

## sample_broken

`broken.py` has valid functions before and after an invalid one. A parser should flag the file as having an error and still read the valid parts. **Do not fix this file.** Your editor will underline it; that is expected.

## Tests

`tests/test_examples.py` checks that the valid samples compile and that `broken.py` still raises a `SyntaxError`, so a sample cannot change its purpose by accident.

If you change a sample, update the tables above. The golden files from #14 will also need to be updated and their diffs reviewed.
