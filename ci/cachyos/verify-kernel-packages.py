#!/usr/bin/env python3
"""Reject mixed-source or unverified kernel artifacts before media assembly."""
import hashlib
import json
import re
import sys
from pathlib import Path

PROFILES = ("allmodconfig", "allyesconfig")


def verify(directory, expected_sha):
    directory = Path(directory)
    if not re.fullmatch(r"[0-9a-f]{40}", expected_sha):
        raise ValueError("expected a full Linux source SHA")
    packages = set(directory.glob("linux-zigux-*.pkg.tar.zst"))
    verified = set()
    for profile in PROFILES:
        record = json.loads((directory / f"kernel-source-{profile}.json").read_text())
        if record["source_sha"] != expected_sha or record["profile"] != profile:
            raise ValueError(f"{profile}: kernel artifact source does not match this run")
        name = record["package"]
        if Path(name).name != name or not re.fullmatch(rf"linux-zigux-{profile}-[A-Za-z0-9.+_-]+\.pkg\.tar\.zst", name):
            raise ValueError(f"{profile}: invalid package filename")
        package = directory / name
        if package.is_symlink():
            raise ValueError("kernel package must be a regular artifact file")
        with package.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != record["package_sha256"]:
            raise ValueError(f"{profile}: kernel package checksum mismatch")
        release = (directory / f"kernel-release-{profile}.txt").read_text().strip()
        if release != record["kernel_release"] or f"-zigux-{profile}-g{expected_sha[:12]}" not in release:
            raise ValueError(f"{profile}: kernel release does not identify the requested source")
        if not record["direct_boot_passed"] or (directory / f"QEMU_KERNEL_RESULT-{profile}").read_text().strip() != "success":
            raise ValueError(f"{profile}: direct kernel boot has not passed")
        verified.add(package)
    if packages != verified:
        raise ValueError("expected exactly the two verified kernel packages")
    return sorted(path.name for path in verified)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify-kernel-packages.py <directory> <source-sha>")
    try:
        print(json.dumps({"source_sha": sys.argv[2], "verified_packages": verify(*sys.argv[1:])}, indent=2))
    except (OSError, KeyError, ValueError) as error:
        raise SystemExit(f"kernel artifact validation failed: {error}") from None
