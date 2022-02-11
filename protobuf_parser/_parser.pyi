from typing import final
from ._types import SupportsParse

@final
class Error:
    filename: str
    line: int
    column: int
    message: str
    warning: bool

def parse(*files: SupportsParse) -> tuple[list[bytes], list[Error]]: ...
def run(protobuf_path: str, include_paths: list[str], files_out: list[tuple[str, str]]) -> list[Error]: ...
