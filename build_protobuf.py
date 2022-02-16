import os
import subprocess
import sys
import tarfile
from collections.abc import Generator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

import requests

VERSION = "3.19.4"


def download() -> None:
    protobuf = Path("protobuf")
    if protobuf.exists():
        return

    # get most recent tag
    r = requests.get(
        f"https://github.com/protocolbuffers/protobuf/releases/download/v{VERSION}/protobuf-cpp-{VERSION}.tar.gz"
    )
    with tarfile.open(fileobj=BytesIO(r.content)) as file:
        file.extractall()

    folder = Path(f"protobuf-{VERSION}")
    folder.rename(protobuf)


@contextmanager
def cd(path: str) -> Generator[None, None, None]:
    cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


def build() -> None:
    with cd("protobuf"):
        if Path("src/.libs").exists():  # no point rebuilding
            return

        subprocess.run(["./configure"])
        subprocess.run(["make -j"])
        subprocess.run(["make install"])


def main() -> int:
    download()
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
