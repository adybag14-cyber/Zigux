#!/usr/bin/env python3
"""Fail-close the dedicated Phase 3 xarray-slot slice note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-xarray-slot-slice.md")

REQUIRED_FILES = (
    Path("zigux/helpers/err_ptr.zig"),
    Path("zigux/helpers/xa_value.zig"),
    Path("zigux/helpers/xarray_slot_view.zig"),
    Path("zigux/tests/phase3_xarray_slot_starter_packet.zig"),
    Path("zigux/tests/phase3_xarray_slot_starter_packet_build.zig"),
    Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase3_xarray_slot_dump.zig"),
    Path("zigux/tests/phase3_xarray_slot_dump_build.zig"),
    Path("zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c"),
    Path("zigux/tests/fixtures/phase3_xarray_slot/expected.json"),
    Path("zigux/tests/fixtures/phase3_xarray_slot_manifest.json"),
    Path("scripts/zigux/check-phase3-xarray-slot.py"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("scripts/zigux/validate-phase3.py"),
)

REQUIRED_NOTE_MARKERS = (
    "This note records one bounded Phase 3 helper-side xarray-slot packet on current `master`.",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot/phase3_xarray_slot_c_harness.c",
    "zigux/tests/fixtures/phase3_xarray_slot/expected.json",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "scripts/zigux/check-phase3-xarray-slot.py",
    "`zigux/helpers/xarray_slot_view.zig` only classifies one raw slot word into four bounded lanes: `null`, tagged `xa_value`, tagged `err_ptr`, and pointer-like.",
    "it does not claim ownership, dereference, traversal, or broader xarray semantics.",
    "The current helper-local packet now has two bounded replay layers:",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
    "The docs-root xarray-slot slice note is now landed, and `zigux/tests/fixtures/phase3_xarray_slot_manifest.json` keeps the remaining nearby repo-reality follow-up narrowed to `Documentation/zigux/phase3-validator-support-surface.md` and `scripts/zigux/validate-phase3.py`.",
    "This note should not be used to imply that the broader Phase 3 export/UAPI survey, shared replay packet, catalog wiring, IDR family, or IDA family has returned.",
    "This note is limited to the helper-local `xarray_slot_view` classifier layered on the already-landed `err_ptr` and `xa_value` helpers, together with one starter packet and one fixture-backed dump parity replay.",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    note_path = repo_root / NOTE_PATH
    try:
        note_text = _read(note_path)
    except FileNotFoundError:
        return issues + [f"missing repo file: {NOTE_PATH.as_posix()}"]

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, rel_path.as_posix() + "\n")
    _write(root / NOTE_PATH, "\n".join(REQUIRED_NOTE_MARKERS) + "\n")


def _remove_marker(path: Path, marker: str) -> None:
    path.write_text(_read(path).replace(marker, ""), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_xarray_slot_slice_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_XARRAY_SLOT_SLICE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker in REQUIRED_NOTE_MARKERS:
            _populate_repo(root)
            _remove_marker(root / NOTE_PATH, marker)
            issues = validate_repo(root)
            expected = f"missing {NOTE_PATH.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_XARRAY_SLOT_SLICE_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        for rel_path in REQUIRED_FILES:
            _populate_repo(root)
            (root / rel_path).unlink()
            issues = validate_repo(root)
            expected = f"missing repo file: {rel_path.as_posix()}"
            if expected not in issues:
                print("PHASE3_XARRAY_SLOT_SLICE_SELF_TEST=fail")
                print(f"expected missing file was not reported: {expected}")
                return 1

    print("PHASE3_XARRAY_SLOT_SLICE_SELF_TEST=pass")
    print(
        "PHASE3_XARRAY_SLOT_SLICE_SELF_TEST_CASE_COUNT="
        f"{1 + len(REQUIRED_NOTE_MARKERS) + len(REQUIRED_FILES)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated Phase 3 xarray-slot slice note."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains Documentation/zigux/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_XARRAY_SLOT_SLICE=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
