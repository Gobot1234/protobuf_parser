# protobuf_parser
A module to programmatically interact with Google's Protocol Buffer Compiler ([protoc](https://developers.google.com/protocol-buffers/docs/downloads)).
It exposes methods to:
- compile `.proto` files to `_pb2.py`s
- parse a file-like objects to a `FileDescriptorProto`

## Installation
```sh
pip install protobuf_parser
```
protobuf_parser provides wheels for all major operating systems.

## Documentation
Documentation can be found at https://protobuf_parser.rtfd.io

## TODO
A method to manually invoke protoc with any given arguments and return the `stdout` and `stderr`.
