from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, AnyStr, Protocol

from _protobuf_parser import run as _run, parse as _parse

if TYPE_CHECKING:
    from _typeshed import SupportsRead

__all__ = (
    "Error",
    "SyntaxError",
    "Warning",
    "parse",
    "run",
)


class _SupportsStr(Protocol):
    def __str__(self) -> str:
        ...


class Error(Exception):
    file: Path
    line: int
    column: int
    message: str


class SyntaxError(Error):
    ...


class Warning(Error, Warning):
    ...


def parse(*files: SupportsRead[AnyStr]) -> tuple[bytes, list[Error]]:
    """Parse files using protoc.

    Parameters
    ----------
    files: `SupportsRead`
        An object that has a read method.

    Returns
    -------
    tuple[`bytes`, list[`Error`]]
        A tuple of the FileDescriptor's bytes and any errors that were encountered when parsing.
    """
    output, errors = _parse(*files)
    return output, [Error(error) for error in errors]


def run(*args: _SupportsStr, **kwargs: _SupportsStr) -> list[Error]:
    """Manually invoke protoc.

    Parameters
    ----------
    *args: `str`
        Any arguments to pass to protoc.
    **kwargs: `str`
        Any keyword arguments to pass to protoc.

    Example
    -------
    .. code-block:: python

        invoke_protoc("this", "that", I="hello")
        # would be equivalent to
        # protoc -I=hello this that

    Returns
    -------
    list[`Error`]
        The errors that were encountered when invoking protoc.
    """

    return [
        Error(error)
        for error in _run(
            *[str(arg) for arg in args],
            **{str(k): str(v) for k, v in kwargs}
        )
    ]
