#!/usr/bin/env python3
"""Fail-close the current Phase 3 rbtree starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-rbtree-slice.md")
HELPER_PATH = Path("zigux/helpers/rbtree_view.zig")
TEST_PATH = Path("zigux/tests/phase3_rbtree_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_rbtree_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_rbtree_manifest.json")

CURRENT_NEXT_SAFE_STEP = (
    "keep the helper-local rbtree starter packet aligned with its checker and "
    "focused build replay without widening into mutation or shared ABI catalog work"
)

REQUIRED_MARKERS = {
    DOC_PATH: (
        "# Phase 3 rbtree Slice",
        "- `zigux/helpers/rbtree_view.zig`",
        "- `zigux/tests/phase3_rbtree_starter_packet.zig`",
        "This packet stays intentionally small:",
    ),
    HELPER_PATH: (
        "pub const Color = enum(u1) {",
        "pub const RBNode = extern struct {",
        "pub fn parent(self: *const RBNode) ?*const RBNode {",
        "pub fn color(self: *const RBNode) Color {",
        "pub fn parentTagBits(self: *const RBNode) usize {",
        "pub const RBTreeView = struct {",
        "pub fn leftmost(self: RBTreeView) ?*const RBNode {",
        "pub fn rightmost(self: RBTreeView) ?*const RBNode {",
        'test "rbtree view treats a null root as empty" {',
        'test "rbtree view decodes parent pointers without losing the color bit" {',
    ),
    TEST_PATH: (
        'test "rbtree view keeps empty roots explicit" {',
        'test "rbtree view preserves root color without inventing a parent" {',
        'test "rbtree view keeps parent pointers and black color bits aligned" {',
        'test "rbtree view keeps leftmost and rightmost traversal reviewable" {',
        "try testing.expectEqual(@as(usize, 0x1), child.parentTagBits());",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/rbtree_view.zig"),',
        '.root_source_file = b.path("phase3_rbtree_starter_packet.zig"),',
        'root_module.addImport("rbtree_view", rbtree_view);',
        '"phase3-rbtree-starter-packet-test"',
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-rbtree-starter-packet",
    "status": "helper_local_rbtree_boundary_surface_present",
    "scope": "helper-local rbtree root and parent-color decoding with one focused starter replay packet",
    "next_safe_step": CURRENT_NEXT_SAFE_STEP,
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-rbtree-slice.md",
    "zigux/helpers/rbtree_view.zig",
    "zigux/tests/phase3_rbtree_starter_packet.zig",
    "zigux/tests/phase3_rbtree_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_rbtree_manifest.json",
    "scripts/zigux/check-phase3-rbtree-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-rbtree-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-rbtree-starter-packet.py --repo-root .",
    "zig build phase3-rbtree-starter-packet-test --build-file zigux/tests/phase3_rbtree_starter_packet_build.zig",
)

SAMPLE_FILES = {
    DOC_PATH: "\n".join(REQUIRED_MARKERS[DOC_PATH]) + "\n",
    HELPER_PATH: "\n".join(REQUIRED_MARKERS[HELPER_PATH]) + "\n",
    TEST_PATH: "\n".join(REQUIRED_MARKERS[TEST_PATH]) + "\n",
    BUILD_PATH: "\n".join(REQUIRED_MARKERS[BUILD_PATH]) + "\n",
    MANIFEST_PATH: json.dumps(
        {
            **REQUIRED_MANIFEST_FIELDS,
            "packet_files": list(REQUIRED_PACKET_FILES),
            "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        },
        indent=2,
    )
    + "\n",
}

SELF_TEST_CASES = (
    (HELPER_PATH, "pub const RBTreeView = struct {"),
    (TEST_PATH, 'test "rbtree view keeps empty roots explicit" {'),
    (BUILD_PATH, '"phase3-rbtree-starter-packet-test"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    try:
        manifest = json.loads(_read(manifest_path))
    except FileNotFoundError:
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues

    for key, expected in REQUIRED_MANIFEST_FIELDS.items():
        if manifest.get(key) != expected:
            issues.append(
                f"wrong {MANIFEST_PATH.as_posix()} field {key}: {manifest.get(key)!r}"
            )

    packet_files = manifest.get("packet_files")
    if packet_files != list(REQUIRED_PACKET_FILES):
        issues.append(f"{MANIFEST_PATH.as_posix()} packet_files drifted from the expected starter packet")

    replay_routes = manifest.get("replay_routes")
    if replay_routes != list(REQUIRED_REPLAY_ROUTES):
        issues.append(f"{MANIFEST_PATH.as_posix()} replay_routes drifted from the expected starter packet")

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_RBTREE_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_RBTREE_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = f"{MANIFEST_PATH.as_posix()} replay_routes drifted from the expected starter packet"
        if expected not in issues:
            print("PHASE3_RBTREE_STARTER_PACKET_SELF_TEST=fail")
            print("expected replay-route drift was not reported")
            return 1

    print("PHASE3_RBTREE_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_RBTREE_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 rbtree starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 rbtree starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_RBTREE_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / HELPER_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
