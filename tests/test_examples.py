"""Guard the sample projects so they keep doing their job.

Valid samples must stay valid Python, and the broken sample must stay broken.
"""

import pytest

VALID_SAMPLES = ["sample_basic", "sample_package"]


@pytest.mark.parametrize("sample", VALID_SAMPLES)
def test_valid_samples_compile(examples_dir, sample):
    files = sorted((examples_dir / sample).rglob("*.py"))
    assert files, f"{sample} has no .py files"
    for path in files:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_broken_sample_has_syntax_error(examples_dir):
    path = examples_dir / "sample_broken" / "broken.py"
    with pytest.raises(SyntaxError):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
