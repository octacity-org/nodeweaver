"""Smoke test: the package can be imported and exposes its CLI."""


def test_package_imports():
    import nodeweaver
    from nodeweaver.cli import app

    assert nodeweaver.__doc__
    assert app is not None
