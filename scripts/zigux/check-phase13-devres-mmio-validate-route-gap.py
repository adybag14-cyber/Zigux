#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 13 devres MMIO validate-route gap."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase13-devres-mmio-validate-route-gap.md")
README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
MMIO_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-mmio-packet.py")

README_MARKERS = [
    "`scripts/zigux/check-phase13-devres-mmio-packet.py`",
    "current `master` still does not materialize the older validator-first helper names `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`",
]

MAKEFILE_REQUIRED_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet-alignment.py",
]

MAKEFILE_FORBIDDEN_MARKERS = [
    "scripts/zigux/check-phase13-devres-mmio-packet.py",
]

MMIO_CHECKER_MARKERS = [
    'REQUIRED_FILES = [',
    '"Documentation/zigux/phase13-devres-slice.md",',
    '"zigux/tests/phase13_devres.zig",',
    "PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass",
]

NOTE_MARKERS = [
    "`PHASE13_LANE=P13-L02`",
    "`scripts/zigux/check-phase13-devres-mmio-packet.py` as shipped Phase 13 evidence",
    "`scripts/zigux/validate-phase13-release.py` and `scripts/zigux/check-phase13-devres-packet-alignment.py` names as repo-reality gaps",
    "`zigux/Makefile` still routes `phase13-validate` through `scripts/zigux/validate-phase13-release.py` and `scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "Refresh `zigux/Makefile` so `phase13-validate` points at the shipped devres MMIO packet guard",
]


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {relpath}") from exc


def require_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"missing {label} marker: {marker}")


def forbid_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise SystemExit(f"unexpected {label} marker: {marker}")


def run(root: Path) -> None:
    readme_text = read_text(root, README_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    mmio_checker_text = read_text(root, MMIO_CHECKER_PATH)
    note_text = read_text(root, NOTE_PATH)

    require_markers(readme_text, README_MARKERS, "scripts README")
    require_markers(makefile_text, MAKEFILE_REQUIRED_MARKERS, "Makefile")
    forbid_markers(makefile_text, MAKEFILE_FORBIDDEN_MARKERS, "Makefile")
    require_markers(mmio_checker_text, MMIO_CHECKER_MARKERS, "MMIO checker")
    require_markers(note_text, NOTE_MARKERS, "note")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / README_PATH,
        "\n".join(README_MARKERS)
        + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                "phase13-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase13-release.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-packet-alignment.py",
            ]
        )
        + "\n",
    )
    write(
        root / MMIO_CHECKER_PATH,
        "\n".join(MMIO_CHECKER_MARKERS) + "\n",
    )
    write(
        root / NOTE_PATH,
        "\n".join(["# note", *NOTE_MARKERS]) + "\n",
    )


def expect_failure(root: Path, relpath: Path, replacement: str) -> None:
    original = (root / relpath).read_text(encoding="utf-8")
    try:
        (root / relpath).write_text(replacement, encoding="utf-8")
        try:
            run(root)
        except SystemExit:
            return
        raise SystemExit(f"self-test expected failure for {relpath}")
    finally:
        (root / relpath).write_text(original, encoding="utf-8")


def self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase13-devres-mmio-route-gap-"))
    try:
        build_fixture(tmpdir)
        run(tmpdir)
        expect_failure(tmpdir, README_PATH, "`scripts/zigux/check-phase13-devres-mmio-packet.py`\n")
        expect_failure(
            tmpdir,
            MAKEFILE_PATH,
            "\n".join(
                [
                    "phase13-validate:",
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase13-devres-mmio-packet.py",
                ]
            )
            + "\n",
        )
        expect_failure(tmpdir, NOTE_PATH, "# missing\n")
    finally:
        shutil.rmtree(tmpdir)

    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_SELF_TEST=pass")
    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_SELF_TEST_CASES=4")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    run(Path(args.root))
    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
