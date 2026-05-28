#!/usr/bin/env python3
"""Fail-close the current Phase 3 ida bitmap starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-ida-bitmap-slice.md")
HELPER_PATH = Path("zigux/helpers/ida_bitmap_view.zig")
TEST_PATH = Path("zigux/tests/phase3_ida_bitmap_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_ida_bitmap_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json")

STARTER_BUILD_ROUTE = (
    "zig build phase3-ida-bitmap-starter-packet-test --build-file "
    "zigux/tests/phase3_ida_bitmap_starter_packet_build.zig"
)
CHECKER_ROUTE = "python3 scripts/zigux/check-phase3-ida-bitmap-starter-packet.py --repo-root ."
SELF_TEST_ROUTE = "python3 scripts/zigux/check-phase3-ida-bitmap-starter-packet.py --self-test"

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "zigux/helpers/ida_bitmap_view.zig",
        "zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json",
        "scripts/zigux/check-phase3-ida-bitmap-starter-packet.py",
        SELF_TEST_ROUTE,
        CHECKER_ROUTE,
        STARTER_BUILD_ROUTE,
        "fixed 128-byte IDA bitmap chunk",
        "The landed `ida_bitmap` helper-local starter packet is real repo evidence",
    ),
    HELPER_PATH: (
        "pub const chunk_size_bytes: usize = 128;",
        "pub const bitmap_bits: usize = bitmap_longs * word_bits;",
        "pub fn isFull(self: BitmapView) bool {",
        "pub fn weight(self: BitmapView) usize {",
        "pub fn firstZero(self: BitmapView) ?usize {",
        'test "ida bitmap constants keep the fixed chunk geometry" {',
        'test "full ida bitmap chunk reports no zero bits left" {',
    ),
    TEST_PATH: (
        'test "ida bitmap starter packet keeps the fixed chunk geometry explicit" {',
        'test "ida bitmap starter packet keeps an empty chunk reviewable" {',
        'test "ida bitmap starter packet keeps sparse words explicit across chunk boundaries" {',
        'test "ida bitmap starter packet keeps full chunks and first-zero exhaustion distinct" {',
        'test "ida bitmap starter packet keeps the first clear position visible inside a partially used word" {',
        "try testing.expectEqual(@as(?usize, 2), view.firstZero());",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/ida_bitmap_view.zig"),',
        '.root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),',
        'root_module.addImport("ida_bitmap_view", ida_bitmap_view);',
        '"phase3-ida-bitmap-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-ida-bitmap-starter-packet"',
        '"status": "starter_packet_present"',
        '"Documentation/zigux/phase3-ida-bitmap-slice.md"',
        '"zigux/helpers/ida_bitmap_view.zig"',
        '"zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json"',
        f'"{SELF_TEST_ROUTE}"',
        f'"{CHECKER_ROUTE}"',
        STARTER_BUILD_ROUTE,
        '"repo_reality_gaps": []',
        '"next_safe_step": "keep the helper-local ida bitmap packet honest with manifest-backed replay before widening into broader ida allocation or range semantics"',
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-ida-bitmap-slice.md",
    "zigux/helpers/ida_bitmap_view.zig",
    "zigux/tests/phase3_ida_bitmap_starter_packet.zig",
    "zigux/tests/phase3_ida_bitmap_starter_packet_build.zig",
    "zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-ida-bitmap-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    SELF_TEST_ROUTE,
    CHECKER_ROUTE,
    STARTER_BUILD_ROUTE,
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append(
                    "phase3_ida_bitmap_starter_packet_manifest.json packet_files is not a list"
                )
            if not isinstance(replay_routes, list):
                issues.append(
                    "phase3_ida_bitmap_starter_packet_manifest.json replay_routes is not a list"
                )
            if not isinstance(repo_reality_gaps, list):
                issues.append(
                    "phase3_ida_bitmap_starter_packet_manifest.json repo_reality_gaps is not a list"
                )
            elif repo_reality_gaps:
                issues.append(
                    "phase3_ida_bitmap_starter_packet_manifest.json repo_reality_gaps should stay empty once the helper-local starter packet is present"
                )
            if isinstance(packet_files, list):
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_ida_bitmap_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_ida_bitmap_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    files = {
        path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()
    }
    files[MANIFEST_PATH] = f"""{{
  \"phase\": \"Phase 3\",
  \"lane\": \"helper-interop\",
  \"slug\": \"phase3-ida-bitmap-starter-packet\",
  \"status\": \"starter_packet_present\",
  \"scope\": \"helper-local ida bitmap chunk geometry and first-set/first-zero replay\",
  \"packet_files\": [
    \"Documentation/zigux/phase3-ida-bitmap-slice.md\",
    \"zigux/helpers/ida_bitmap_view.zig\",
    \"zigux/tests/phase3_ida_bitmap_starter_packet.zig\",
    \"zigux/tests/phase3_ida_bitmap_starter_packet_build.zig\",
    \"zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json\",
    \"scripts/zigux/check-phase3-ida-bitmap-starter-packet.py\"
  ],
  \"replay_routes\": [
    \"{SELF_TEST_ROUTE}\",
    \"{CHECKER_ROUTE}\",
    \"{STARTER_BUILD_ROUTE}\"
  ],
  \"repo_reality_gaps\": [],
  \"next_safe_step\": \"keep the helper-local ida bitmap packet honest with manifest-backed replay before widening into broader ida allocation or range semantics\"
}}
"""
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


SELF_TEST_CASES = (
    (SLICE_PATH, "zigux/tests/phase3_ida_bitmap_starter_packet_manifest.json"),
    (SLICE_PATH, STARTER_BUILD_ROUTE),
    (MANIFEST_PATH, f'"{CHECKER_ROUTE}"'),
    (HELPER_PATH, "pub fn firstZero(self: BitmapView) ?usize {"),
    (TEST_PATH, 'test "ida bitmap starter packet keeps sparse words explicit across chunk boundaries" {'),
    (BUILD_PATH, '"phase3-ida-bitmap-starter-packet-test"'),
    (MANIFEST_PATH, '"status": "starter_packet_present"'),
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_ida_bitmap_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_IDA_BITMAP_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_IDA_BITMAP_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["zigux/tests/phase3_ida_bitmap_starter_packet.zig"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = validate_repo(root)
        expected = (
            "phase3_ida_bitmap_starter_packet_manifest.json repo_reality_gaps should stay empty once the helper-local starter packet is present"
        )
        if expected not in issues:
            print("PHASE3_IDA_BITMAP_STARTER_PACKET_SELF_TEST=fail")
            print("expected non-empty repo_reality_gaps issue was not reported")
            return 1

    print("PHASE3_IDA_BITMAP_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_IDA_BITMAP_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 ida bitmap starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ida bitmap starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_IDA_BITMAP_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
