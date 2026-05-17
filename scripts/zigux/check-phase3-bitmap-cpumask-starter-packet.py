#!/usr/bin/env python3
"""Fail-close the current Phase 3 bitmap/cpumask starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SLICE_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
HEADER_PATH = Path("include/zigux/bitmap_cpumask.h")
UAPI_PATH = Path("zigux/uapi/bitmap_cpumask.zig")
BINDING_PATH = Path("zigux/bindings/bitmap_cpumask.zig")
BITMAP_HELPER_PATH = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_HELPER_PATH = Path("zigux/helpers/cpumask_view.zig")
TEST_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json")

REQUIRED_MARKERS = {
    SLICE_PATH: (
        "PHASE3_BITMAP_CPUMASK_SLICE_FILE_COUNT=",
        "PHASE3_BITMAP_CPUMASK_SLICE_SCOPE=",
        "PHASE3_BITMAP_CPUMASK_NEXT_SAFE_STEP=",
        "zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py",
        "zigux/tests/phase3_bitmap_cpumask_dump.zig",
    ),
    VALIDATOR_NOTE_PATH: (
        "## Focused bitmap/cpumask slice present on `master`",
        "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
        "include/zigux/bitmap_cpumask.h",
        "zigux/helpers/bitmap_view.zig",
        "zigux/helpers/cpumask_view.zig",
        "zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py",
        "zigux/bindings/version.zig",
        "zigux/helpers/unsafe_policy.zig",
        "Keep the shared Phase 3 reminder packet anchored to those four current-tree-backed slices",
        "`Documentation/zigux/review-checklist.md` still carries broader shared Phase 3 reminder language",
        "`Documentation/zigux/README.md` and `zigux/tests/README.md` now match the bounded starter-packet-plus-helper-slice posture.",
    ),
    HEADER_PATH: (
        "#define ZIGUX_BITMAP_VIEW_ABI_VERSION 1u",
        "#define ZIGUX_BITMAP_SUMMARY_ABI_VERSION 1u",
        "#define ZIGUX_CPUMASK_VIEW_ABI_VERSION 1u",
        "struct zigux_bitmap_view {",
        "struct zigux_bitmap_summary {",
        "struct zigux_cpumask_view {",
        "static inline struct zigux_cpumask_view zigux_cpumask_view_make(",
    ),
    UAPI_PATH: (
        "pub const bitmap_view_abi_version: u32 = 1;",
        "pub const bitmap_summary_abi_version: u32 = 1;",
        "pub const cpumask_view_abi_version: u32 = 1;",
        "pub const BitmapView = extern struct {",
        "pub const BitmapSummary = extern struct {",
        "pub const CpumaskView = extern struct {",
        "pub fn initCpumaskView(",
    ),
    BINDING_PATH: (
        'const uapi = @import("uapi_bitmap_cpumask");',
        'pub const bitmap_view_words_addr_offset: usize = @offsetOf(uapi.BitmapView, "words_addr");',
        'pub const bitmap_summary_weight_offset: usize = @offsetOf(uapi.BitmapSummary, "weight");',
        'pub const cpumask_view_nr_cpu_ids_offset: usize = @offsetOf(uapi.CpumaskView, "nr_cpu_ids");',
        'pub fn asBitmap(view: CpumaskView) BitmapView {',
    ),
    BITMAP_HELPER_PATH: (
        "pub fn wordCount(nbits: u32) u32 {",
        "pub fn lastWordMask(nbits: u32) Word {",
        "pub fn testBit(view: binding.BitmapView, bit: u32) bool {",
        "pub fn firstSet(view: binding.BitmapView) u32 {",
        "pub fn firstZero(view: binding.BitmapView) u32 {",
        "pub fn weight(view: binding.BitmapView) u32 {",
        "pub fn summarize(view: binding.BitmapView) binding.BitmapSummary {",
    ),
    CPUMASK_HELPER_PATH: (
        'const bitmap = @import("bitmap_view_helper");',
        "pub fn viewFromWords(backing: []const Word, nr_cpu_ids: u32) binding.CpumaskView {",
        "pub fn cpuIsSet(view: binding.CpumaskView, cpu: u32) bool {",
        "pub fn firstCpu(view: binding.CpumaskView) u32 {",
        "pub fn firstAbsentCpu(view: binding.CpumaskView) u32 {",
        "pub fn weight(view: binding.CpumaskView) u32 {",
        "pub fn summarize(view: binding.CpumaskView) binding.BitmapSummary {",
    ),
    TEST_PATH: (
        'test "bitmap cpumask starter binding preserves the helper-local layout" {',
        'test "bitmap starter helpers keep first set first zero and weight aligned" {',
        'test "cpumask starter helpers keep cpu membership reviewable" {',
        'test "starter packet stays aligned with the live Linux-facing header family version" {',
        "binding.cpumask_view_nr_cpu_ids_offset",
        "cpumask_view.cpuIsSet(view, 7)",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../uapi/bitmap_cpumask.zig"),',
        '.root_source_file = b.path("../bindings/bitmap_cpumask.zig"),',
        '.root_source_file = b.path("../helpers/bitmap_view.zig"),',
        '.root_source_file = b.path("../helpers/cpumask_view.zig"),',
        '.root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),',
        'root_module.addImport("cpumask_view_helper", cpumask_view_helper);',
        '"phase3-bitmap-cpumask-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-bitmap-cpumask-starter-packet"',
        '"status": "starter_packet_present"',
        '"Documentation/zigux/phase3-bitmap-cpumask-slice.md"',
        '"zigux/helpers/bitmap_view.zig"',
        '"zigux/helpers/cpumask_view.zig"',
        '"python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test"',
        '"zig build phase3-bitmap-cpumask-starter-packet-test --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig"',
        '"next_safe_step": "keep the bitmap and cpumask helper family bounded to manifest-backed replay and truthful validator-support wording before widening into the older dump-style packet or broader Phase 3 closure claims"',
    ),
}

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}
SAMPLE_FILES[MANIFEST_PATH] = """{
  "phase": "Phase 3",
  "lane": "helper-interop",
  "slug": "phase3-bitmap-cpumask-starter-packet",
  "status": "starter_packet_present",
  "scope": "helper-local bitmap summary and cpumask membership replay",
  "packet_files": [
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/zigux/bitmap_cpumask.h",
    "zigux/uapi/bitmap_cpumask.zig",
    "zigux/bindings/bitmap_cpumask.zig",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py"
  ],
  "replay_routes": [
    "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py",
    "zig build phase3-bitmap-cpumask-starter-packet-test --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig"
  ],
  "repo_reality_gaps": [
    "zigux/tests/phase3_bitmap_cpumask_dump.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/validate-phase3.py"
  ],
  "next_safe_step": "keep the bitmap and cpumask helper family bounded to manifest-backed replay and truthful validator-support wording before widening into the older dump-style packet or broader Phase 3 closure claims"
}
"""

SELF_TEST_CASES = (
    (SLICE_PATH, "PHASE3_BITMAP_CPUMASK_SLICE_FILE_COUNT="),
    (VALIDATOR_NOTE_PATH, "## Focused bitmap/cpumask slice present on `master`"),
    (HEADER_PATH, "#define ZIGUX_CPUMASK_VIEW_ABI_VERSION 1u"),
    (UAPI_PATH, "pub const CpumaskView = extern struct {"),
    (BINDING_PATH, "pub fn asBitmap(view: CpumaskView) BitmapView {"),
    (BITMAP_HELPER_PATH, "pub fn weight(view: binding.BitmapView) u32 {"),
    (CPUMASK_HELPER_PATH, "pub fn summarize(view: binding.CpumaskView) binding.BitmapSummary {"),
    (TEST_PATH, "cpumask_view.cpuIsSet(view, 7)"),
    (BUILD_PATH, '"phase3-bitmap-cpumask-starter-packet-test"'),
    (MANIFEST_PATH, '"status": "starter_packet_present"'),
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
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            if not isinstance(packet_files, list):
                issues.append(
                    "phase3_bitmap_cpumask_starter_packet_manifest.json packet_files is not a list"
                )
            if not isinstance(replay_routes, list):
                issues.append(
                    "phase3_bitmap_cpumask_starter_packet_manifest.json replay_routes is not a list"
                )
            if isinstance(packet_files, list):
                for required_path in (
                    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
                    "Documentation/zigux/phase3-validator-support-surface.md",
                    "include/zigux/bitmap_cpumask.h",
                    "zigux/uapi/bitmap_cpumask.zig",
                    "zigux/bindings/bitmap_cpumask.zig",
                    "zigux/helpers/bitmap_view.zig",
                    "zigux/helpers/cpumask_view.zig",
                    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
                    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
                    "zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json",
                    "scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py",
                ):
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_bitmap_cpumask_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                for route in (
                    "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test",
                    "python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py",
                    "zig build phase3-bitmap-cpumask-starter-packet-test --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
                ):
                    if route not in replay_routes:
                        issues.append(
                            "phase3_bitmap_cpumask_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_BITMAP_CPUMASK_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_BITMAP_CPUMASK_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_BITMAP_CPUMASK_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_BITMAP_CPUMASK_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 bitmap/cpumask starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 bitmap/cpumask starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_BITMAP_CPUMASK_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
