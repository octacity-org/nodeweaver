"""Tests for file discovery and the `nodeweaver scan` command."""

import pytest
from typer.testing import CliRunner

from nodeweaver.cli import app
from nodeweaver.discovery import EXCLUDED_DIRS, find_python_files

runner = CliRunner()


def make_files(root, *paths):
    for path in paths:
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("", encoding="utf-8")


# --- find_python_files -------------------------------------------------------


def test_lists_sample_package_relative_and_sorted(examples_dir):
    assert find_python_files(examples_dir / "sample_package") == [
        "pkg/__init__.py",
        "pkg/core.py",
        "pkg/utils/__init__.py",
        "pkg/utils/strings.py",
    ]


def test_lists_every_sample(examples_dir):
    assert find_python_files(examples_dir) == [
        "sample_basic/helpers.py",
        "sample_basic/main.py",
        "sample_basic/models.py",
        "sample_basic/routes.py",
        "sample_broken/broken.py",
        "sample_package/pkg/__init__.py",
        "sample_package/pkg/core.py",
        "sample_package/pkg/utils/__init__.py",
        "sample_package/pkg/utils/strings.py",
    ]


def test_only_py_files(tmp_path):
    make_files(tmp_path, "a.py", "b.txt", "c.pyc", "d.pyi", "e.py.bak")
    assert find_python_files(tmp_path) == ["a.py"]


@pytest.mark.parametrize("excluded", sorted(EXCLUDED_DIRS))
def test_skips_excluded_dir(tmp_path, excluded):
    make_files(tmp_path, "keep.py", f"{excluded}/skip.py", f"src/{excluded}/deep.py")
    assert find_python_files(tmp_path) == ["keep.py"]


def test_paths_use_forward_slashes(tmp_path):
    make_files(tmp_path, "a/b/c.py")
    assert find_python_files(tmp_path) == ["a/b/c.py"]


def test_does_not_follow_directory_symlinks(tmp_path):
    make_files(tmp_path, "real/a.py")
    try:
        (tmp_path / "link").symlink_to(tmp_path / "real", target_is_directory=True)
    except OSError:
        pytest.skip("creating symlinks is not allowed here (e.g. Windows without developer mode)")
    assert find_python_files(tmp_path) == ["real/a.py"]


# --- nodeweaver scan -----------------------------------------------------------


def test_scan_prints_one_path_per_line(examples_dir):
    result = runner.invoke(app, ["scan", str(examples_dir / "sample_package")])
    assert result.exit_code == 0
    assert result.stdout.splitlines() == [
        "pkg/__init__.py",
        "pkg/core.py",
        "pkg/utils/__init__.py",
        "pkg/utils/strings.py",
    ]


def test_scan_missing_path_fails(tmp_path):
    missing = tmp_path / "missing"
    result = runner.invoke(app, ["scan", str(missing)])
    assert result.exit_code == 1
    assert "path does not exist" in result.stderr
    assert result.stdout == ""


def test_scan_file_instead_of_directory_fails(tmp_path):
    make_files(tmp_path, "a.py")
    result = runner.invoke(app, ["scan", str(tmp_path / "a.py")])
    assert result.exit_code == 1
    assert "not a directory" in result.stderr


def test_scan_without_python_files_succeeds_with_a_message(tmp_path):
    make_files(tmp_path, "notes.txt")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert result.stdout == ""
    assert "No Python files found" in result.stderr


def test_no_command_shows_help():
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "scan" in result.stdout


def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Directory to scan" in result.stdout
