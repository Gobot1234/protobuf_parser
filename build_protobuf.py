import tarfile
from io import BytesIO

import requests

# get most recent tag
r = requests.get("https://github.com/protocolbuffers/protobuf/releases/download/v3.19.4/protobuf-cpp-3.19.4.tar.gz")
with tarfile.open(name="protobuf", fileobj=BytesIO(r.content)) as file:
    file.extractall()
