#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 13 devres NP-wrapper summary gap."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase13-devres-np-wrapper-gap.md")
HELPER_PATH = Path("lib/devres.zig")
REPLAY_PATH = Path("zigux/tests/phase13_devres.zig")
SLICE_PATH = Path("Documentation/zigux/phase13-devres-slice.md")
ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-packet-alignment.py")

HELPER_MARKERS = [
    "planManagedIoremapAcquireNp(",
]

REPLAY_MARKERS = [
    "phase13 devres non-posted ioremap wrapper forces the NP lifetime path",
]

SLICE_MARKERS = [
    "switching plain managed ioremap requests to the non-posted variant",
]

ALIGNMENT_REQUIRED_MARKERS = [
    'SLICE_MARKERS = [',
    '"devm_ioremap_wc()"',
]

ALIGNMENT_FORBIDDEN_MARKERS = [
    '"devm_ioremap_np()"',
]

NOTE_MARKERS = [
    "`PHASE13_LANE=P13-L06`",
    "`lib/devres.zig` carries `planManagedIoremapAcquireNp(`",
    "`zigux/tests/phase13_devres.zig` keeps the direct replay `phase13 devres non-posted ioremap wrapper forces the NP lifetime path`",
    "`Documentation/zigux/phase13-devres-slice.md` already records the same behavior",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py` still pins the slice summary through `devm_ioremap_uc()` and `devm_ioremap_wc()` without an explicit `devm_ioremap_np()` marker",
    "Refresh `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_reviewability.zig`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` together",
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
    helper_text = read_text(root, HELPER_PATH)
    replay_text = read_text(root, REPLAY_PATH)
    slice_text = read_text(root, SLICE_PATH)
    alignment_text = read_text(root, ALIGNMENT_CHECKER_PATH)
    note_text = read_text(root, NOTE_PATH)

    require_markers(helper_text, HELPER_MARKERS, "helper")
    require_markers(replay_text, REPLAY_MARKERS, "replay")
    require_markers(slice_text, SLICE_MARKERS, "slice")
    require_markers(alignment_text, ALIGNMENT_REQUIRED_MARKERS, "alignment checker")
    forbid_markers(alignment_text, ALIGNMENT_FORBIDDEN_MARKERS, "alignment checker")
    require_markers(note_text, NOTE_MARKERS, "note")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / HELPER_PATH, "pub fn planManagedIoremapAcquireNp() void {}\n")
    write(
        root / REPLAY_PATH,
        'test "phase13 devres non-posted ioremap wrapper forces the NP lifetime path" {}\n',
    )
    write(
        root / SLICE_PATH,
        "switching plain managed ioremap requests to the non-posted variant when resource flags demand it\n",
    )
    write(
        root / ALIGNMENT_CHECKER_PATH,
        'SLICE_MARKERS = [\n    "devm_ioremap_wc()",\n]\n',
    )
    write(
        root / NOTE_PATH,
        "\n".join(
            [
                "# note",
                "`PHASE13_LANE=P13-L06`",
                "`lib/devres.zig` carries `planManagedIoremapAcquireNp(`",
                "`zigux/tests/phase13_devres.zig` keeps the direct replay `phase13 devres non-posted ioremap wrapper forces the NP lifetime path`",
                "`Documentation/zigux/phase13-devres-slice.md` already records the same behavior",
                "`scripts/zigux/check-phase13-devres-packet-alignment.py` still pins the slice summary through `devm_ioremap_uc()` and `devm_ioremap_wc()` without an explicit `devm_ioremap_np()` marker",
                "Refresh `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_reviewability.zig`, and `scripts/zigux/check-phase13-devres-packet-alignment.py` together",
            ]
        )
        + "\n",
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase13-devres-np-gap-"))
    try:
        build_fixture(tmpdir)
        run(tmpdir)
        expect_failure(tmpdir, HELPER_PATH, "pub fn somethingElse() void {}\n")
        expect_failure(tmpdir, ALIGNMENT_CHECKER_PATH, 'SLICE_MARKERS = [\n    "devm_ioremap_wc()",\n    "devm_ioremap_np()",\n]\n')
        expect_failure(tmpdir, NOTE_PATH, "# missing\n")
    finally:
        shutil.rmtree(tmpdir)

    print("PHASE13_DEVRES_NP_WRAPPER_GAP_SELF_TEST=pass")
    print("PHASE13_DEVRES_NP_WRAPPER_GAP_SELF_TEST_CASES=4")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    run(Path(args.root))
    print("PHASE13_DEVRES_NP_WRAPPER_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
