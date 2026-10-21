import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from nodeweaver.ir import (
    CallIR,
    ClassIR,
    FileIR,
    FunctionIR,
    ImportIR,
    line_from_row,
)

EXAMPLE = Path(__file__).parent.parent / "examples" / "ir-example.json"


# --- the hand-written example -------------------------------------------------


def test_example_validates_and_round_trips():
    ir = FileIR.model_validate_json(EXAMPLE.read_text(encoding="utf-8"))
    assert ir.file == "src/auth/login.py"
    assert FileIR.model_validate_json(ir.model_dump_json()) == ir


# --- Q1: one entry per imported name ------------------------------------------


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(module="a.b", line=1),  # import a.b
        dict(module="a", alias="x", line=1),  # import a as x
        dict(module="a", name="b", alias="c", line=1),  # from a import b as c
        dict(module="a", name="*", line=1),  # from a import *
        dict(module=None, name="x", relative_level=1, line=1),  # from . import x
        dict(module="p", name="y", relative_level=2, line=1),  # from ..p import y
    ],
)
def test_valid_import_forms(kwargs):
    ImportIR(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(line=1),  # nothing is imported
        dict(module=None, name="x", line=1),  # "from import x" has no dots
        dict(module="a", relative_level=1, line=1),  # plain `import` cannot be relative
        dict(module="a", relative_level=-1, line=1),
    ],
)
def test_invalid_import_forms(kwargs):
    with pytest.raises(ValidationError):
        ImportIR(**kwargs)


# --- Q2: qualified caller names -----------------------------------------------


def test_caller_must_point_to_a_listed_function():
    ok = FileIR(
        file="a.py",
        functions=[FunctionIR(name="f", qualname="f", line=1)],
        calls=[CallIR(name="g", line=2, caller="f")],
    )
    assert ok.calls[0].caller == "f"
    with pytest.raises(ValidationError):
        FileIR(file="a.py", calls=[CallIR(name="g", line=2, caller="missing")])


def test_call_at_module_level_has_no_caller():
    ir = FileIR(file="a.py", calls=[CallIR(name="print", line=1)])
    assert ir.calls[0].caller is None


def test_method_qualname_includes_the_class():
    save = FunctionIR(name="save", qualname="User.save", line=2)
    ir = FileIR(
        file="a.py",
        classes=[ClassIR(name="User", line=1, methods=[save])],
        calls=[CallIR(name="x", line=3, caller="User.save")],
    )
    assert ir.calls[0].caller == "User.save"
    wrong = FunctionIR(name="save", qualname="save", line=2)
    with pytest.raises(ValidationError):
        FileIR(file="a.py", classes=[ClassIR(name="User", line=1, methods=[wrong])])


def test_top_level_function_qualname_equals_name():
    with pytest.raises(ValidationError):
        FileIR(file="a.py", functions=[FunctionIR(name="f", qualname="x.f", line=1)])


def test_qualname_must_end_with_name():
    with pytest.raises(ValidationError):
        FunctionIR(name="f", qualname="g", line=1)


def test_same_qualname_twice_is_allowed():
    # a property getter and its setter share the same qualname
    methods = [
        FunctionIR(name="x", qualname="C.x", line=3),
        FunctionIR(name="x", qualname="C.x", line=6),
    ]
    FileIR(file="a.py", classes=[ClassIR(name="C", line=1, methods=methods)])

# --- Q2: receiver of a call ------------------------------------------------------


@pytest.mark.parametrize(
    "name, receiver",
    [
        ("self.save", "self"),  # self.save()
        ("super().__init__", "super()"),  # super().__init__()
        ("mod.func", "mod"),  # mod.func()
        ("a.b().c", "a.b()"),  # a.b().c()
        ("col.Counter(i.name for i in items).most_common", "col.Counter(i.name for i in items)"),
        ("a .b().c", "a .b()"),  # chain on three lines: whitespace collapsed to one space
        ("f", None),  # bare call
        ("handlers[0]", None),  # not an attribute access
    ],
)
def test_valid_receivers(name, receiver):
    assert CallIR(name=name, receiver=receiver, line=1).receiver == receiver


@pytest.mark.parametrize(
    "name, receiver",
    [
        ("save", "self"),  # name does not contain the receiver
        ("self.", "self"),  # no attribute after the dot
        ("other.save", "self"),  # receiver is not the prefix of name
        ("self.save", ""),  # empty receiver
        ("a .b() .c", "a .b()"),  # name must be built as receiver + "." + attribute
    ],
)
def test_invalid_receivers(name, receiver):
    with pytest.raises(ValidationError):
        CallIR(name=name, receiver=receiver, line=1)

# --- Q4: relative paths with "/" ----------------------------------------------


@pytest.mark.parametrize("path", ["a.py", "pkg/mod.py", "src/auth/login.py"])
def test_valid_paths(path):
    assert FileIR(file=path).file == path


@pytest.mark.parametrize(
    "path",
    ["src\\a.py", "/abs/a.py", "C:/x/a.py", "c:\\x\\a.py", "../a.py", "a/../b.py", ""],
)
def test_paths_must_be_relative_and_use_slashes(path):
    with pytest.raises(ValidationError):
        FileIR(file=path)


# --- Q5: 1-based line numbers --------------------------------------------------


def test_line_numbers_are_one_based():
    assert line_from_row(0) == 1
    with pytest.raises(ValidationError):
        FunctionIR(name="f", qualname="f", line=0)
    with pytest.raises(ValidationError):
        CallIR(name="f", line=0)
    with pytest.raises(ValidationError):
        ClassIR(name="C", line=0)
    with pytest.raises(ValidationError):
        ImportIR(module="a", line=0)


# --- Q6: syntax errors ----------------------------------------------------------


def test_parse_error_files_keep_partial_results_and_skip_reference_checks():
    ir = FileIR(
        file="a.py",
        parse_error=True,
        functions=[FunctionIR(name="f", qualname="f", line=1)],
        calls=[CallIR(name="g", line=2, caller="missing")],
    )
    assert ir.parse_error
    assert len(ir.functions) == 1


# --- general --------------------------------------------------------------------


def test_defaults():
    ir = FileIR(file="a.py")
    assert ir.schema_version == "0.1"
    assert ir.language == "python"
    assert ir.parse_error is False
    assert ir.imports == ir.classes == ir.functions == ir.calls == []


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        FileIR(file="a.py", imprts=[])


def test_json_shape_is_stable():
    data = json.loads(FileIR(file="a.py").model_dump_json())
    assert list(data) == [
        "schema_version",
        "file",
        "language",
        "parse_error",
        "imports",
        "classes",
        "functions",
        "calls",
    ]
    imp = json.loads(ImportIR(module="a", line=1).model_dump_json())
    assert list(imp) == ["module", "name", "alias", "relative_level", "line"]
    call = json.loads(CallIR(name="f", line=1).model_dump_json())
    assert list(call) == ["name", "receiver", "line", "caller"]