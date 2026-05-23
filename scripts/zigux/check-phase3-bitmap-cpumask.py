#!/usr/bin/env python3
"""Fail-close the bounded Phase 3 bitmap/cpumask starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
BITMAP_VIEW_PATH = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_VIEW_PATH = Path("zigux/helpers/cpumask_view.zig")
TEST_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-bitmap-cpumask-starter-packet",
    "status": "helper_local_bitmap_cpumask_slice_present",
    "scope": "helper-local bitmap range and cpumask membership/subset replay",
    "next_safe_step": (
        "if this slice needs parity expansion later, add the narrow C harness and "
        "expected fixture without widening beyond helper-local bitmap and cpumask semantics"
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
)

REQUIRED_REPO_REALITY_GAPS = (
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
)

REQUIRED_MARKERS = {
    DOC_PATH: (
        "This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.",
        "`zigux/helpers/bitmap_view.zig`",
        "`zigux/helpers/cpumask_view.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`",
        "`zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`",
        "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask.py",
        "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
        "It does not yet claim C parity fixtures, exported ABI structs, scheduler-affinity semantics, or wider kernel cpumask traversal behavior.",
        "`zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`",
        "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`",
    ),
    BITMAP_VIEW_PATH: (
        "pub const BitmapView = struct {",
        "pub fn countSetBits(self: BitmapView) usize {",
        "pub fn firstSetBit(self: BitmapView) ?usize {",
        "pub fn firstClearBit(self: BitmapView) ?usize {",
        'test "bitmap view ignores padding bits past the declared range" {',
    ),
    CPUMASK_VIEW_PATH: (
        "pub const CpuMaskView = struct {",
        "pub fn countPresentCpus(self: CpuMaskView) usize {",
        "pub fn firstMissingCpu(self: CpuMaskView) ?usize {",
        "pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {",
        "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {",
    ),
    TEST_PATH: (
        'test "bitmap starter packet keeps set-bit counting bounded to the declared range" {',
        'test "bitmap starter packet keeps a sparse shared bitmap reviewable" {',
        'test "cpumask starter packet keeps cpu membership and missing-cpu discovery explicit" {',
        'test "cpumask starter packet keeps subset and overlap semantics inside the bounded mask" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../helpers/bitmap_view.zig"),',
        '.root_source_file = b.path("../helpers/cpumask_view.zig"),',
        '.root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),',
        'cpumask_view.addImport("bitmap_view", bitmap_view);',
        'root_module.addImport("bitmap_view", bitmap_view);',
        'root_module.addImport("cpumask_view", cpumask_view);',
        '"phase3-bitmap-cpumask-starter-packet"',
        '"Run the shared Phase 3 bitmap/cpumask starter packet"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-bitmap-cpumask-starter-packet"',
        '"status": "helper_local_bitmap_cpumask_slice_present"',
        '"zigux/helpers/bitmap_view.zig"',
        '"zigux/helpers/cpumask_view.zig"',
        '"scripts/zigux/check-phase3-bitmap-cpumask.py"',
        '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test"',
        '"zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json"',
    ),
}

SELF_TEST_CASES = (
    (DOC_PATH, "`zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`"),
    (DOC_PATH, "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test"),
    (DOC_PATH, "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`"),
    (BITMAP_VIEW_PATH, "pub fn firstClearBit(self: BitmapView) ?usize {"),
    (CPUMASK_VIEW_PATH, "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {"),
    (TEST_PATH, 'test "cpumask starter packet keeps subset and overlap semantics inside the bounded mask" {'),
    (BUILD_PATH, '"phase3-bitmap-cpumask-starter-packet"'),
    (MANIFEST_PATH, '"scripts/zigux/check-phase3-bitmap-cpumask.py"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


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

    try:
        manifest = json.loads(_read(repo_root / MANIFEST_PATH))
    except FileNotFoundError:
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in EXPECTED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                f"phase3_bitmap_cpumask_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_bitmap_cpumask_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_bitmap_cpumask_manifest.json packet_files",
            packet_files,
            issues,
        )
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(
                    f"phase3_bitmap_cpumask_manifest.json missing packet_files entry: {entry}"
                )

    if not isinstance(replay_routes, list):
        issues.append("phase3_bitmap_cpumask_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_bitmap_cpumask_manifest.json replay_routes",
            replay_routes,
            issues,
        )
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(
                    f"phase3_bitmap_cpumask_manifest.json missing replay route: {entry}"
                )

    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_bitmap_cpumask_manifest.json repo_reality_gaps is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_bitmap_cpumask_manifest.json repo_reality_gaps",
            repo_reality_gaps,
            issues,
        )
        for entry in REQUIRED_REPO_REALITY_GAPS:
            if entry not in repo_reality_gaps:
                issues.append(
                    f"phase3_bitmap_cpumask_manifest.json missing repo_reality_gaps entry: {entry}"
                )
        for entry in repo_reality_gaps:
            if (repo_root / entry).exists():
                issues.append(
                    "phase3_bitmap_cpumask_manifest.json repo_reality_gaps entry is present on disk: "
                    f"{entry}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")

    manifest = {
        **EXPECTED_MANIFEST_FIELDS,
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        "repo_reality_gaps": list(REQUIRED_REPO_REALITY_GAPS),
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].append(REQUIRED_PACKET_FILES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase3_bitmap_cpumask_manifest.json packet_files duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected duplicate packet_files entry was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase3_bitmap_cpumask_manifest.json replay_routes duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected duplicate replay_routes entry was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = [REQUIRED_REPO_REALITY_GAPS[0]]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_bitmap_cpumask_manifest.json missing repo_reality_gaps entry: "
            + REQUIRED_REPO_REALITY_GAPS[1]
        )
        if expected not in issues:
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected missing repo_reality_gaps entry was not reported")
            return 1

        _populate_repo(root)
        gap_path = root / REQUIRED_REPO_REALITY_GAPS[0]
        _write(gap_path, "// no longer a repo gap\n")
        issues = validate_repo(root)
        expected = (
            "phase3_bitmap_cpumask_manifest.json repo_reality_gaps entry is present on disk: "
            + REQUIRED_REPO_REALITY_GAPS[0]
        )
        if expected not in issues:
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected present-on-disk repo gap was not reported")
            return 1

    print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass")
    print(f"PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 4}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 3 bitmap/cpumask starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 bitmap/cpumask slice",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_BITMAP_CPUMASK_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_BITMAP_CPUMASK_PACKET=pass")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
