"""Smoke test: the package can be imported and exposes its entry point."""


def test_package_imports():
    import nodeweaver

    assert callable(nodeweaver.main)
