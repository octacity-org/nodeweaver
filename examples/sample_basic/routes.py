"""Decorators and async code for sample_basic.

Run it from this folder with: python routes.py
"""

import asyncio


class App:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def register(func):
            self.routes[path] = func
            return func

        return register


app = App()  # module-level call


async def load_items():
    await asyncio.sleep(0)
    return ["apple", "bread"]


@app.route("/items")  # decorator that is a call
async def list_items():
    items = await load_items()  # await on a call
    return sorted(items)


def run():
    return asyncio.run(app.routes["/items"]())


if __name__ == "__main__":
    print(run())
