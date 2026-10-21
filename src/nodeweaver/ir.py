"""Intermediate representation (IR) of the structure of one Python file.

Conventions (decided in issue #5):

- Paths are relative to the scan root and use "/" on every operating system.
- Line numbers are 1-based. tree-sitter rows are 0-based: convert them only
  with `line_from_row`.
- Lists are in source order.
- Only definitions that are not inside another function or class are listed.
  Methods are listed under their class. Nested functions, lambdas and nested
  classes are not listed.
- `parse_error=True` means the file had syntax errors. The lists then hold
  best-effort results taken from the intact parts of the syntax tree.
"""

import re
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "0.1"

Line = Annotated[int, Field(ge=1)]  # 1-based
Name = Annotated[str, Field(min_length=1)]


def line_from_row(row: int) -> int:
    """Convert a 0-based tree-sitter row into a 1-based line number.

    This is the only place where the conversion happens.
    """
    return row + 1


class IRModel(BaseModel):
    """Base class: unknown fields are rejected, so typos are caught early."""

    model_config = ConfigDict(extra="forbid")


class ImportIR(IRModel):
    """One imported name. `from a import b, c` becomes two entries.

    | code                   | module | name | alias | relative_level |
    |------------------------|--------|------|-------|----------------|
    | import a.b             | a.b    | None | None  | 0              |
    | import a as x          | a      | None | x     | 0              |
    | from a import b as c   | a      | b    | c     | 0              |
    | from a import *        | a      | *    | None  | 0              |
    | from . import x        | None   | x    | None  | 1              |
    | from ..p import y      | p      | y    | None  | 2              |
    """

    module: str | None = None
    name: str | None = None
    alias: str | None = None
    relative_level: Annotated[int, Field(ge=0)] = 0  # number of leading dots
    line: Line

    @model_validator(mode="after")
    def _check_form(self) -> Self:
        if self.module is None and self.name is None:
            raise ValueError("an import needs a module or a name")
        if self.module is None and self.relative_level == 0:
            raise ValueError("an import without a module must be relative (relative_level >= 1)")
        if self.name is None and self.relative_level != 0:
            raise ValueError("a plain `import` statement cannot be relative")
        return self


class FunctionIR(IRModel):
    """A function or method. `qualname` is e.g. "login_user" or "User.save".

    The same qualname may appear twice, for example a property getter and its
    setter. They are told apart by `line`.
    """

    name: Name
    qualname: Name
    line: Line  # the `def` line, not the decorator line

    @model_validator(mode="after")
    def _qualname_ends_with_name(self) -> Self:
        if self.qualname != self.name and not self.qualname.endswith("." + self.name):
            raise ValueError("qualname must end with the function name")
        return self


class ClassIR(IRModel):
    name: Name
    line: Line  # the `class` line, not the decorator line
    methods: list[FunctionIR] = Field(default_factory=list)


class CallIR(IRModel):
    """A call, as written in the source (e.g. "self.save", "a.b().c").

    `receiver` is the source text of the object in front of the last dot:
    "self" for `self.save()`, "super()" for `super().__init__()`, "a.b()" for
    `a.b().c()`. It is None for bare calls such as `f()` and for callees that
    are not an attribute access, such as `handlers[0]()`.

    `caller` is the qualname of the nearest enclosing listed function or
    method. It is None outside any listed function (module level, class body).
    """

    name: Name
    receiver: str | None = None
    line: Line
    caller: str | None = None

    @model_validator(mode="after")
    def _receiver_is_the_prefix_of_name(self) -> Self:
        if self.receiver is not None:
            prefix = self.receiver + "."
            if not self.receiver or not self.name.startswith(prefix) or self.name == prefix:
                raise ValueError("name must be receiver + '.' + attribute")
        return self


class FileIR(IRModel):
    schema_version: str = SCHEMA_VERSION
    file: Name  # relative to the scan root, "/" separators
    language: str = "python"
    parse_error: bool = False
    imports: list[ImportIR] = Field(default_factory=list)
    classes: list[ClassIR] = Field(default_factory=list)
    functions: list[FunctionIR] = Field(default_factory=list)
    calls: list[CallIR] = Field(default_factory=list)

    @field_validator("file")
    @classmethod
    def _relative_posix_path(cls, value: str) -> str:
        if "\\" in value:
            raise ValueError("use '/' as the path separator")
        if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
            raise ValueError("the path must be relative to the scan root")
        if ".." in value.split("/"):
            raise ValueError("the path must not leave the scan root")
        return value

    @model_validator(mode="after")
    def _check_references(self) -> Self:
        for func in self.functions:
            if func.qualname != func.name:
                raise ValueError(f"top-level function {func.name!r} must have qualname == name")
        for cls in self.classes:
            for method in cls.methods:
                if method.qualname != f"{cls.name}.{method.name}":
                    raise ValueError(
                        f"method {method.name!r} of class {cls.name!r} must have "
                        f"qualname {cls.name}.{method.name}"
                    )
        # With syntax errors the results are best-effort, so references are not enforced.
        if not self.parse_error:
            known = {f.qualname for f in self.functions}
            known |= {m.qualname for c in self.classes for m in c.methods}
            for call in self.calls:
                if call.caller is not None and call.caller not in known:
                    raise ValueError(f"call {call.name!r} has an unknown caller {call.caller!r}")
        return self