import sys
from io import StringIO
from textwrap import dedent

from betterproto.lib.google.protobuf import FileDescriptorProto

from protobuf_parser import parse


class InputIO(StringIO):
    def __init__(self, input: str) -> None:
        super().__init__(dedent(input))
        self.name = f"{sys._getframe(1).f_code.co_name}.proto"  # noqa


def test_valid_parse() -> None:
    # language=proto
    input = """
    syntax = "proto3";

    message Test {};
    """

    output, errors = parse(InputIO(input))
    assert not errors
    assert output
    test = FileDescriptorProto().parse(output[0])
    assert test.name == "test_valid_parse.proto"
    assert test.message_type[0].name == "Test"
    assert not test._unknown_fields


def test_invalid_parse() -> None:
    # language=proto
    input = """
    syntax = "proto3";

    message Test {};

    error please
    """

    output, errors = parse(InputIO(input))
    assert not output
    assert errors
    assert errors[0].line == 6


def test_parse_warnings() -> None:
    # language=proto
    input = """
    message test {};
    """

    output, warnings = parse(InputIO(input))
    assert output
    assert warnings

    assert all(isinstance(error, Warning) for error in warnings)


def test_file_parse() -> None:
    output, errors = parse("test.proto")
    assert not errors
    assert output

    file = FileDescriptorProto().parse(output[0])

    assert file.name == "test.proto"
    assert file.message_type[0].name == "Test"
    assert file.message_type[1].name == "Foo"


def test_multiple_files() -> None:
    # language=proto
    file_1 = InputIO(
        """
    syntax = "proto3";

    message Foo {};
    """
    )
    # language=proto
    file_2 = InputIO(
        """
    syntax = "proto3";

    message Bar {};
    """
    )
    # language=proto
    file_3 = InputIO(
        """
    syntax = "proto3";

    message Baz {};
    """
    )

    file_1.name = "file_1.proto"
    file_2.name = "file_2.proto"
    file_3.name = "file_3.proto"

    outputs, errors = parse(file_1, file_2, file_3)

    assert not errors
    files = [FileDescriptorProto().parse(data) for data in outputs]
    assert [file.name for file in files] == [file_1.name, file_2.name, file_3.name]
