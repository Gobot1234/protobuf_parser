from ._types import SupportsRead


class Error:
    file: str
    line: int
    column: int
    message: str


def parse(*files: SupportsRead) -> tuple[bytes, list[Error]]: ...
def run(*args: str, **kwargs: str) -> list[Error]: ...
