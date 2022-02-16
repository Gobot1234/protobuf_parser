# Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

from __future__ import annotations

import os
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Sequence, TypeVar

from ._parser import Error as _Error, parse as _parse, run as _run
from ._types import *
from ._version import __version__

__all__ = (
    "Error",
    "Warning",
    "parse",
    "ParseResult",
    "run",
    "RunResult",
)

ParseableFileT = TypeVar("ParseableFileT", AnyPath, SupportsParse, FileDescriptorLike)
RunableFileT = TypeVar("RunableFileT", bound=AnyPath)


class Error(Exception):
    def __new__(cls, c_error: _Error) -> Error | Warning:
        return super().__new__(Warning if c_error.warning else Error)

    def __init__(self, c_error: _Error) -> None:
        self.file = Path(c_error.filename)
        self.line = c_error.line
        self.column = c_error.column
        self.message = c_error.message
        super().__init__(c_error.message)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.file}:{self.line}:{self.column}: {self.message!r}>"


class Warning(Error, Warning):
    ...


@dataclass
class ParseResult(Generic[ParseableFileT]):
    file: ParseableFileT  # this will be seeked to the end
    parsed: bytes
    errors: Sequence[Error]


@dataclass
class FPWithName:
    fp: TextIOWrapper
    name: str | bytes

    def read(self) -> str:
        return self.fp.read()


def parse(*files_: ParseableFileT) -> Sequence[ParseResult[ParseableFileT]]:
    """Parse files using protoc.

    Parameters
    ----------
    files
        Something that can be `open`ed or has a name attribute and read method.

    Returns
    -------
    tuple[list[bytes], list[Error]]
        A tuple of the FileDescriptor's bytes and any errors that were encountered when parsing.
    """
    files: list[SupportsParse] = []
    for file in files_:  # TODO make the path actually correct
        if isinstance(file, SupportsParse):
            files.append(file)
        elif isinstance(file, (os.PathLike, str, bytes)):
            files.append(FPWithName(open(file, "r", encoding="UTF-8"), os.fspath(file)))
        elif isinstance(file, FileDescriptorLike):
            files.append(FPWithName(open_fileno(file), f"fd-{file!r}.proto"))
        else:
            raise TypeError()

    parsed, errors = _parse(files)
    error_map: defaultdict[str | bytes, list[Error]] = defaultdict(list)
    for error in errors:
        error_map[error.filename].append(Error(error))

    return [
        ParseResult(file, parsed, error_map[supports_parse.name])
        for file, parsed, supports_parse in zip(files_, parsed, files)
    ]


@dataclass
class RunResult(Generic[RunableFileT]):
    input: RunableFileT
    errors: Sequence[Error]
    output: Path


# TODO this segfaults
# TODO better api like parse
def run(*filenames: RunableFileT, outputs: Iterable[str]) -> Sequence[RunResult[RunableFileT]]:
    """Manually invoke protoc.

    Parameters
    ----------
    *args: `str`
        Any arguments to pass to protoc.
    **kwargs: `str`
        Any keyword arguments to pass to protoc.

    Example
    -------
    ```py
    >>> run("this", "that", I="hello")
    # would be equivalent to
    # protoc -I=hello this that
    ```

    Returns
    -------
    list[`Error`]
        The errors that were encountered when invoking protoc.
    """

    return [Error(error) for error in _run(*[str(arg) for arg in args], **{k: str(v) for k, v in kwargs.items()})]
