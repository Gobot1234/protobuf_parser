import pytest

from protobuf_parser import parse



def test_valid_parse() -> None:
    input = "message hello {};"
    output, errors = parse(input)
    assert not errors
    assert output
