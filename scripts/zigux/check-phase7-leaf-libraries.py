#!/usr/bin/env python3
"""Fail-close the bounded Phase 7 leaf-libraries starter packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase7-leaf-libraries.md")
TEST_PATH = Path("zigux/tests/phase7_leaf_libraries_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase7_leaf_libraries_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase7_leaf_libraries_manifest.json")

EXPECTED_MANIFEST = {
    "phase": "Phase 7",
    "lane": "kernel-leaf-libraries",
    "slug": "phase7-leaf-libraries-starter-packet",
    "status": "existing_leaf_ports_now_have_bounded_shared_validation_packet",
    "scope": (
        "bounded shared replay for the existing string_helpers, cmdline, "
        "argv_split, and rbtree Phase 7 ports"
    ),
    "next_safe_step": (
        "wire this packet into the shared tests root only after the standalone "
        "replay path stays stable on master"
    ),
}

REQUIRED_PACKET_FILES = [
    "Documentation/zigux/phase7-leaf-libraries.md",
    "lib/string_helpers.zig",
    "lib/cmdline.zig",
    "lib/argv_split.zig",
    "lib/rbtree.zig",
    "zigux/tests/phase7_leaf_libraries_starter_packet.zig",
    "zigux/tests/phase7_leaf_libraries_starter_packet_build.zig",
    "zigux/tests/fixtures/phase7_leaf_libraries_manifest.json",
    "scripts/zigux/check-phase7-leaf-libraries.py",
]

REQUIRED_REPLAY_ROUTES = [
    "python3 scripts/zigux/check-phase7-leaf-libraries.py --self-test",
    "python3 scripts/zigux/check-phase7-leaf-libraries.py --repo-root . --skip-exec",
    "zig build phase7-leaf-libraries-starter-packet --build-file zigux/tests/phase7_leaf_libraries_starter_packet_build.zig",
]

REQUIRED_MARKERS = {
    DOC_PATH: [
        "This note records one bounded validation packet for the existing Phase 7 in-kernel leaf-library ports.",
        "`lib/string_helpers.zig`",
        "`lib/cmdline.zig`",
        "`lib/argv_split.zig`",
        "`lib/rbtree.zig`",
        "`zigux/tests/phase7_leaf_libraries_starter_packet.zig`",
        "`zigux/tests/phase7_leaf_libraries_starter_packet_build.zig`",
        "`zigux/tests/fixtures/phase7_leaf_libraries_manifest.json`",
        "`scripts/zigux/check-phase7-leaf-libraries.py`",
        "duplicate-key match iteration",
    ],
    TEST_PATH: [
        'test "phase7 packet keeps borrowed cmdline parsing aligned with owned argv splitting" {',
        'test "phase7 packet keeps string helper replacement and cmdline quoting reviewable" {',
        'test "phase7 packet keeps memparse and integer option expansion explicit" {',
        'test "phase7 packet keeps cached rbtree ordering stable for parsed values" {',
        'test "phase7 packet keeps duplicate mode values queryable across argv split cmdline parsing and rbtree matching" {',
    ],
    BUILD_PATH: [
        '.root_source_file = b.path("../../lib/string_helpers.zig"),',
        '.root_source_file = b.path("../../lib/cmdline.zig"),',
        '.root_source_file = b.path("../../lib/argv_split.zig"),',
        '.root_source_file = b.path("../../lib/rbtree.zig"),',
        '"phase7-leaf-libraries-starter-packet"',
    ],
    MANIFEST_PATH: [
        '"slug": "phase7-leaf-libraries-starter-packet"',
        '"lane": "kernel-leaf-libraries"',
        '"lib/string_helpers.zig"',
        '"lib/cmdline.zig"',
        '"lib/argv_split.zig"',
        '"lib/rbtree.zig"',
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(repo_root: Path, *, skip_exec: bool = False, zig: str = "zig") -> list[str]:
    issues: list[str] = []

    for rel_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / rel_path
        if not path.exists():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = read_text(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.exists():
        return issues

    manifest = json.loads(read_text(manifest_path))
    for key, expected in EXPECTED_MANIFEST.items():
        actual = manifest.get(key)
        if actual != expected:
            issues.append(f"wrong manifest {key}: {actual!r} != {expected!r}")

    if manifest.get("packet_files") != REQUIRED_PACKET_FILES:
        issues.append("packet_files does not match the bounded Phase 7 packet inventory")
    if manifest.get("replay_routes") != REQUIRED_REPLAY_ROUTES:
        issues.append("replay_routes does not match the bounded Phase 7 replay routes")

    gaps = manifest.get("repo_reality_gaps")
    if not isinstance(gaps, list) or not gaps:
        issues.append("repo_reality_gaps must stay as a non-empty list until shared tests-root wiring lands")

    if issues or skip_exec:
        return issues

    result = subprocess.run(
        [
            zig,
            "build",
            "phase7-leaf-libraries-starter-packet",
            "--build-file",
            "zigux/tests/phase7_leaf_libraries_starter_packet_build.zig",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        issues.append("zig build replay failed")
        if result.stdout.strip():
            issues.append(result.stdout.strip())
        if result.stderr.strip():
            issues.append(result.stderr.strip())

    return issues


def populate(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")

    manifest = {
        **EXPECTED_MANIFEST,
        "packet_files": REQUIRED_PACKET_FILES,
        "replay_routes": REQUIRED_REPLAY_ROUTES,
        "repo_reality_gaps": [
            "shared top-level zigux/tests/build.zig wiring is still separate work inside the same phase family"
        ],
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_leaf_libraries_") as temp_dir:
        root = Path(temp_dir)
        populate(root)

        issues = validate(root, skip_exec=True)
        if issues:
            print("PHASE7_LEAF_LIBRARIES_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        text = read_text(root / TEST_PATH)
        marker = REQUIRED_MARKERS[TEST_PATH][0]
        write_text(root / TEST_PATH, text.replace(marker, "", 1))
        issues = validate(root, skip_exec=True)
        expected = f"missing {TEST_PATH.as_posix()} marker: {marker}"
        if expected not in issues:
            print("PHASE7_LEAF_LIBRARIES_PACKET_SELF_TEST=fail")
            print("expected missing starter-packet marker was not reported")
            return 1

    print("PHASE7_LEAF_LIBRARIES_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 7 leaf-libraries packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--zig", default="zig")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.repo_root, skip_exec=args.skip_exec, zig=args.zig)
    if issues:
        print("PHASE7_LEAF_LIBRARIES_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE7_LEAF_LIBRARIES_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
