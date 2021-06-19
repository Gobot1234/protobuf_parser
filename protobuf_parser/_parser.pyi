from ._types import SupportsRead


class Error:
    filename: str
    line: int
    column: int
    message: str


def parse(*files: SupportsRead) -> tuple[list[bytes], list[Error]]: ...
# def run(*args: str, **kwargs: str) -> list[Error]: ...
