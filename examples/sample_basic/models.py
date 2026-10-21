"""Data models for sample_basic: classes, methods, and calls on self and super()."""

DEFAULT_PRICE = 10.0


class Item:
    # Call in the class body, outside any method
    CATEGORIES = frozenset(["food", "drink"])

    def __init__(self, name, price=DEFAULT_PRICE):
        self.name = name
        self.price = price
        self.history = []

    def total(self, quantity):
        return self.price * quantity

    def describe(self):
        return f"{self.name}: {self.price}"

    def save(self):
        self.history.append(self.describe())

    def update_price(self, price):
        self.price = price
        self.save()  # call on self


class DiscountedItem(Item):
    def __init__(self, name, price, discount):
        super().__init__(name, price)  # call on a non-name expression
        self.discount = discount

    def total(self, quantity):
        return super().total(quantity) * (1 - self.discount)
