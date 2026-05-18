#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 13 devres MMIO shared-route gap."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase13-devres-mmio-validate-route-gap.md")
README_PATH = Path("scripts/zigux/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")
MMIO_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-mmio-packet.py")

README_MARKERS = [
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`",
    "current `master` still does not materialize `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "keep helper-local `libfs`, `devres`, and `landlock` ownership explicit",
]

MAKEFILE_REQUIRED_MARKERS = [
    "phase12-smoke:",
    "phase12-test:",
]

MAKEFILE_FORBIDDEN_MARKERS = [
    "phase13-validate:",
    "phase13:",
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet-alignment.py",
    "scripts/zigux/check-phase13-devres-mmio-packet.py",
]

SLICE_MARKERS = [
    "`zigux/tests/phase13_devres_dma_coherent.zig` now materializes one direct replay surface",
    "`Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, and `zigux/tests/phase13_devres_manifest.json` remain repo-reality gaps",
    "The bounded current evidence is the direct DMA-boundary replay plus the planner note",
]

DMA_REPLAY_MARKERS = [
    "phase13 devres dma coherent replay anchors the current slice reality",
    "Documentation/zigux/phase13-devres-slice.md",
    "repo-reality gaps",
]

MMIO_CHECKER_MARKERS = [
    'REQUIRED_FILES = [',
    '"Documentation/zigux/phase13-devres-slice.md",',
    "PHASE13_DEVRES_MMIO_PACKET_SELF_TEST=pass",
]

NOTE_MARKERS = [
    "`PHASE13_LANE=P13-L02`",
    "`PHASE13_SCOPE=iomap-mmio-safety-route-gap`",
    "`Documentation/zigux/phase13-devres-slice.md` and `zigux/tests/phase13_devres_dma_coherent.zig` now keep the surviving devres packet narrow on current `master`",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`",
    "current `master` does not ship a shared Phase 13 rerun hook for the surviving devres MMIO evidence at all",
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
    slice_text = read_text(root, SLICE_PATH)
    dma_replay_text = read_text(root, DMA_REPLAY_PATH)
    mmio_checker_text = read_text(root, MMIO_CHECKER_PATH)
    note_text = read_text(root, NOTE_PATH)

    require_markers(readme_text, README_MARKERS, "scripts README")
    require_markers(makefile_text, MAKEFILE_REQUIRED_MARKERS, "Makefile")
    forbid_markers(makefile_text, MAKEFILE_FORBIDDEN_MARKERS, "Makefile")
    require_markers(slice_text, SLICE_MARKERS, "slice")
    require_markers(dma_replay_text, DMA_REPLAY_MARKERS, "dma replay")
    require_markers(mmio_checker_text, MMIO_CHECKER_MARKERS, "MMIO checker")
    require_markers(note_text, NOTE_MARKERS, "note")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                "phase12-smoke:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build smoke --build-file zigux/tests/phase12_build.zig --summary all",
                "phase12-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
            ]
        )
        + "\n",
    )
    write(root / SLICE_PATH, "\n".join(SLICE_MARKERS) + "\n")
    write(root / DMA_REPLAY_PATH, "\n".join(DMA_REPLAY_MARKERS) + "\n")
    write(root / MMIO_CHECKER_PATH, "\n".join(MMIO_CHECKER_MARKERS) + "\n")
    write(root / NOTE_PATH, "\n".join(["# note", *NOTE_MARKERS]) + "\n")


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
        expect_failure(tmpdir, README_PATH, "keep helper-local `libfs`, `devres`, and `landlock` ownership explicit\n")
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
        expect_failure(tmpdir, SLICE_PATH, "`zigux/tests/phase13_devres_dma_coherent.zig` now materializes one direct replay surface\n")
        expect_failure(tmpdir, NOTE_PATH, "# missing\n")
    finally:
        shutil.rmtree(tmpdir)

    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_SELF_TEST=pass")
    print("PHASE13_DEVRES_MMIO_VALIDATE_ROUTE_GAP_SELF_TEST_CASES=5")


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
