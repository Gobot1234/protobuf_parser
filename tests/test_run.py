from pathlib import Path

import protobuf_parser


def test_test():
    test = Path("test.proto")
    (result,) = protobuf_parser.run(test)
    assert not result.errors
    assert result.output == Path("test_pb2.py").resolve()
    assert result.input == test


def test_test_errors():
    test = Path("test_errors.proto")
    (result,) = protobuf_parser.run(test)
    assert result.errors
    assert result.output is None
    assert result.input == test
