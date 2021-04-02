from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    from _typeshed import SupportsRead


class Error(Exception):
    file: Path
    line: int
    column: int
    message: str


class SyntaxError(Error): ...


class Warning(Error, Warning): ...


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


def invoke_protoc(*args: str, **kwargs: str) -> list[Error]:
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
    # encode strs
