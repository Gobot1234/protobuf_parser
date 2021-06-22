from protobuf_parser import parse
from io import StringIO
import sys

from betterproto.lib.google.protobuf import FileDescriptorProto


class InputIO(StringIO):
    def __init__(self, input: str):
        super().__init__(input)
        self.name = f"{sys._getframe(1).f_code.co_name}.proto"  # noqa


def test_valid_parse() -> None:
    # language=proto
    input = """\
    syntax = "proto3";

    message hello {};
    """

    output, errors = parse(InputIO(input))
    assert not errors
    assert output
    test = FileDescriptorProto().parse(output[0])
    assert test.name == "test_valid_parse.proto"
    assert test.message_type[0].name == "hello"
    assert not test._unknown_fields


def test_invalid_parse() -> None:
    # language=proto
    input = """\
    syntax = "proto3";

    message hello {};

    error please
    """

    output, errors = parse(InputIO(input))
    assert not output
    assert errors
    assert all(isinstance(error, SyntaxError) for error in errors)
