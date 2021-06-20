from ._types import SupportsParse


class Error:
    filename: str
    line: int
    column: int
    message: str


def parse(*files: SupportsParse) -> tuple[list[bytes], list[Error]]: ...
# def run(*args: str, **kwargs: str) -> list[Error]: ...
