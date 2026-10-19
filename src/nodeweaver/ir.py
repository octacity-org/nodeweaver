"""Intermediate representation (IR) of the structure of one source file."""

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.1"


class IRModel(BaseModel):
    """Base class: unknown fields are rejected, so typos are caught early."""

    model_config = ConfigDict(extra="forbid")


class ImportIR(IRModel):
    module: str | None  # "a.b"; None for "from . import x"
    names: list[str] = Field(default_factory=list)  # imported names
    alias: str | None = None  # "import a as b" -> "b"
    relative_level: int = 0  # number of leading dots in a relative import
    line: int  # 1-based


class FunctionIR(IRModel):
    name: str
    line: int  # 1-based


class ClassIR(IRModel):
    name: str
    line: int  # 1-based
    methods: list[FunctionIR] = Field(default_factory=list)


class CallIR(IRModel):
    name: str  # callee as written, e.g. "obj.method"
    line: int  # 1-based
    caller: str | None = None  # enclosing function, None at module level


class FileIR(IRModel):
    schema_version: str = SCHEMA_VERSION
    file: str  # relative to the scan root, "/" separators
    language: str = "python"
    parse_error: bool = False
    imports: list[ImportIR] = Field(default_factory=list)
    classes: list[ClassIR] = Field(default_factory=list)
    functions: list[FunctionIR] = Field(default_factory=list)
    calls: list[CallIR] = Field(default_factory=list)