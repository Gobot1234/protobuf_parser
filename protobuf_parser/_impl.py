# Copyright (c) James Hilton-Balfe under the MIT License see LICENSE

from __future__ import annotations

import os
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, TypeVar

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
RunableFileT = TypeVar("RunableFileT", bound=StrPath)


class Error(Exception):
    def __new__(cls, c_error: _Error) -> Error | Warning:
        return super().__new__(Warning if c_error.warning else Error)

    def __init__(self, c_error: _Error) -> None:
        self.filename = c_error.filename
        self.line = c_error.line
        self.column = c_error.column
        self.message = c_error.message
        super().__init__(c_error.message)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.filename}:{self.line}:{self.column}: {self.message!r}>"


class Warning(Error, Warning):
    ...


@dataclass
class ParseResult(Generic[ParseableFileT]):
    input: ParseableFileT
    """The inputted file, `tell`, if applicable will be set to the end."""
    parsed: bytes
    """The parsed contents of a ``FileDescriptor`` representing this file."""
    errors: Sequence[Error]
    """Any errors encountered when parsing the file."""


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
    A sequence of results containing the original file, the FileDescriptor's bytes and any errors that were encountered when
    parsing.
    """
    files: list[SupportsParse] = []
    for file in files_:
        if isinstance(file, SupportsParse):
            files.append(file)
        elif isinstance(file, (os.PathLike, str, bytes)):
            files.append(FPWithName(open(file, "r", encoding="UTF-8"), os.fspath(file)))
        elif isinstance(file, FileDescriptorLike):  # type: ignore
            files.append(FPWithName(open_fileno(file), f"fd-{file!r}.proto"))
        else:
            raise TypeError(
                f"file was excepted to be of type {ParseableFileT.__constraints__} "
                f"not {file.__class__!r}"  # type: ignore
            )

    parsed, errors = _parse(files)
    error_map: "defaultdict[str | bytes, list[Error]]" = defaultdict(list)
    for error in errors:
        error_map[error.filename].append(Error(error))

    return [
        ParseResult(file, parsed, error_map[supports_parse.name])
        for file, parsed, supports_parse in zip(files_, parsed, files)
    ]


@dataclass
class RunResult(Generic[RunableFileT]):
    input: RunableFileT
    output: Path | None
    errors: Sequence[Error]


SENTINEL = object()
FILLER = (SENTINEL, SENTINEL)


def run(*filenames: RunableFileT) -> Sequence[RunResult[RunableFileT]]:
    """Run the python code generator on ``filenames``.

    Returns
    -------
    A sequence of results containing the original filename, the outputted file and any errors that were encountered
    when parsing.
    """
    results: list[RunResult[RunableFileT]] = []

    paths = [Path(file).resolve(strict=True) for file in filenames]
    include = paths[0].parent
    assert all((path.parent == include for path in paths))

    files, errors = _run([str(path.relative_to(include)) for path in paths], [str(include)])

    error_map: "defaultdict[str | bytes, list[Error]]" = defaultdict(list)
    for error in errors:
        error_map[error.filename].append(Error(error))

    for input, (filename, contents) in zip(filenames, files):
        if contents:
            output = include.joinpath(filename)
            output.write_text(contents)
        else:
            output = None
        results.append(RunResult(input, output, error_map[filename]))

    return results


def protoc(*args: Any, **kwargs: Any) -> Sequence[Error]:
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
    >>> protoc("this", "that", I="hello")
    # would be equivalent to
    # protoc -I=hello this that
    ```

    Returns
    -------
    list[`Error`]
        The errors that were encountered when invoking protoc.
    """
    raise NotImplementedError()
