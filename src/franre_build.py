from __future__ import annotations

import base64
import hashlib
import tarfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).parent.parent
PACKAGE = ROOT / "src" / "franre"
NAME = "franre"
VERSION = "0.1.0"
DIST_INFO = f"{NAME}-{VERSION}.dist-info"


def _metadata() -> bytes:
    return (
        "Metadata-Version: 2.1\n"
        f"Name: {NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: python library to quick solve franklin-reiter rsa tasks\n"
        "Requires-Python: >=3.10\n\n"
    ).encode()


def _wheel() -> bytes:
    return (
        "Wheel-Version: 1.0\n"
        "Generator: franre-build\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n\n"
    ).encode()


def _metadata_files() -> dict[str, bytes]:
    return {
        f"{DIST_INFO}/METADATA": _metadata(),
        f"{DIST_INFO}/WHEEL": _wheel(),
        f"{DIST_INFO}/top_level.txt": b"franre\n",
    }


def get_requires_for_build_wheel(config_settings=None):
    return []


def get_requires_for_build_sdist(config_settings=None):
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    target = Path(metadata_directory) / DIST_INFO
    target.mkdir(parents=True, exist_ok=True)
    for relative, contents in _metadata_files().items():
        (target / Path(relative).name).write_bytes(contents)
    return DIST_INFO


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    wheel_name = f"{NAME}-{VERSION}-py3-none-any.whl"
    output = Path(wheel_directory) / wheel_name
    files = {
        f"franre/{path.name}": path.read_bytes()
        for path in sorted(PACKAGE.glob("*.py"))
    }
    files.update(_metadata_files())
    rows = []
    for path, contents in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(contents).digest())
        digest = digest.rstrip(b"=").decode("ascii")
        rows.append(f"{path},sha256={digest},{len(contents)}\n")
    rows.append(f"{DIST_INFO}/RECORD,,\n")
    files[f"{DIST_INFO}/RECORD"] = "".join(rows).encode()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path, contents in files.items():
            archive.writestr(path, contents)
    return wheel_name


def build_sdist(sdist_directory, config_settings=None):
    archive_name = f"{NAME}-{VERSION}.tar.gz"
    output = Path(sdist_directory) / archive_name
    files = [ROOT / "pyproject.toml", ROOT / "README.md", Path(__file__)]
    files.extend(sorted(PACKAGE.glob("*.py")))
    with tarfile.open(output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
        for path in files:
            archive.add(path, arcname=f"{NAME}-{VERSION}/{path.relative_to(ROOT)}")
    return archive_name
