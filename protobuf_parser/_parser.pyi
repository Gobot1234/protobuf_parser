from collections.abc import Sequence
from . import SupportsRead


class Error:
    file: str
    line: int
    column: int
    message: str


class SyntaxError(Error): ...
class Warning(Error): ...


def parse(*files: SupportsRead) -> tuple[bytes, Sequence[Error]]: ...
def run(*args: str, **kwargs: str) -> Sequence[Error]: ...
