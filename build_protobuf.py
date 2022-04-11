import os
import subprocess
import sys
import tarfile
from collections.abc import Generator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

from urllib.request import urlopen

VERSION = "3.20.0"


def download() -> None:
    protobuf = Path("protobuf")
    if protobuf.exists():
        return

    # get most recent tag
    r = urlopen(
        f"https://github.com/protocolbuffers/protobuf/releases/download/v{VERSION}/protobuf-cpp-{VERSION}.tar.gz"
    )
    with tarfile.open(fileobj=BytesIO(r.read())) as file:
        file.extractall()

    folder = Path(f"protobuf-{VERSION}")
    folder.rename(protobuf)


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
            return

        if sys.platform != "win32":
            subprocess.run(["./configure"])
            subprocess.run(["make"])
            subprocess.run(["make", "install", "-fPIC"])
        else:
            subprocess.run(["git", "clone", "https://github.com/microsoft/vcpkg", "--depth=1"])
            subprocess.run([r".\vcpkg\bootstrap-vcpkg.bat"])
            subprocess.run([r".\vcpkg\vcpkg", "install", "protobuf", "protobuf:x64-windows"])


def main() -> int:
    download()
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
