"""Entry point for sample_basic.

Covers every import form and the common call forms the parser should recognize.
Run it from this folder with: python main.py
"""

# Import forms
import json                                 # import x
import os.path                              # import x.y
import collections as col                   # import x as y
from models import Item, DiscountedItem     # from x import a, b
from os.path import join as join_path       # from x import a as b
from helpers import *                       # from x import *


def build_items():
    return [Item("apple", 1.5), Item("bread"), DiscountedItem("cheese", 8.0, 0.25)]


def main():
    items = build_items()

    # Call inside a lambda
    cheapest = min(items, key=lambda item: item.total(1))

    # Call inside a nested function
    def summarize(item):
        return {"name": make_label(item.name), "total": round_price(item.total(3))}

    # Call forms
    summary = [summarize(item) for item in items]             # f(), inside a comprehension
    first = items[0].describe()                               # obj.m()
    text = json.dumps(summary)                                # mod.f()
    top = col.Counter(i.name for i in items).most_common(1)   # a.b().c()
    label = make_label(str(cheapest.name))                    # f(g(x))
    handlers = [round_price, abs]
    rounded = handlers[0](3.14159)                            # call on a subscript

    items[1].update_price(2.0)
    path = join_path("data", os.path.basename("items.json"))
    print(first, label, rounded, top, path)
    print(text)


# Module-level call (no enclosing function)
if __name__ == "__main__":
    main()
