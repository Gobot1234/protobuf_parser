import os
import subprocess
import sys
import tarfile
from collections.abc import Generator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

from urllib.request import urlopen

VERSION = "3.19.4"


def download() -> None:
    protobuf = Path("protobuf")
    if protobuf.exists():
        return print("already exists")

    # get most recent tag
    r = urlopen(
        f"https://github.com/protocolbuffers/protobuf/releases/download/v{VERSION}/protobuf-cpp-{VERSION}.tar.gz"
    )
    with tarfile.open(fileobj=BytesIO(r.read())) as file:
        file.extractall()

    folder = Path(f"protobuf-{VERSION}")
    folder.rename(protobuf)
    print("extracted and renamed")


@contextmanager
def cd(path: str) -> Generator[None, None, None]:
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


def build() -> None:
    with cd("protobuf"):
        if Path("src/.libs").exists():  # no point rebuilding
            return print("its already there?")

        print("running configure")
        subprocess.run(["./configure"])
        print("running make")
        subprocess.run(["make -j"])
        print("running make install")
        subprocess.run(["make install"])


def main() -> int:
    print("about to download")
    download()
    build()
    print("finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
