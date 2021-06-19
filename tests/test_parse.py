from protobuf_parser import parse, Error
from io import StringIO
import sys


class InputIO(StringIO):
    def __init__(self, input: str):
        super().__init__(input)
        self.name = f"{sys._getframe(1).f_code.co_name}.proto"  # noqa


def test_valid_parse() -> None:
    # input = InputIO("message hello {};")
    output, errors = parse("test.proto")
    assert not errors
    print(output)


def test_invalid_parse() -> None:
    input = InputIO("""\
message hello {};

fdfdfdfd
""")
    output, errors = parse(input)
    assert not output
    assert errors
    assert all(isinstance(error, SyntaxError) for error in errors)
