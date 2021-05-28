import pytest

from protobuf_parser import parse, Error



def test_valid_parse() -> None:
    input = "message hello {};"
    output, errors = parse(input)
    assert not errors
    assert output


def test_invalid_parse() -> None:
    input = """\
message hello {};

fdfdfdfd
"""
    output, errors = parse(input)
    assert not output
    assert errors
    assert all(isinstance(error, SyntaxError) for error in errors)
