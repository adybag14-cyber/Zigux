#!/usr/bin/env python3
"""Fail-close the bounded Phase 3 bitmap/cpumask starter packet."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
BITMAP_VIEW_PATH = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_VIEW_PATH = Path("zigux/helpers/cpumask_view.zig")
TEST_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig")
C_HARNESS_PATH = Path(
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"
)
EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "helper-interop",
    "slug": "phase3-bitmap-cpumask-starter-packet",
    "status": "helper_local_bitmap_cpumask_fixture_packet_present",
    "scope": "helper-local bitmap range and cpumask membership/subset replay plus narrow C fixture parity",
    "next_safe_step": (
        "keep any future same-lane follow-through narrowed to exported or "
        "scheduler-facing bitmap/cpumask behavior only if current helper-local "
        "fixture packet drifts on master"
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c",
    "zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --repo-root . --cc gcc",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
)

REQUIRED_MARKERS = {
    DOC_PATH: (
        "This note records one bounded shared-subsystems helper packet for the missing bitmap/cpumask Phase 3 slice.",
        "`zigux/helpers/bitmap_view.zig`",
        "`zigux/helpers/cpumask_view.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`",
        "`zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`",
        "`zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`",
        "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`",
        "`zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`",
        "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
        "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --repo-root . --cc gcc",
        "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
        "It does not yet claim exported ABI structs, scheduler-affinity semantics, or wider kernel cpumask traversal behavior.",
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
    C_HARNESS_PATH: (
        'static size_t count_set_bits(const uintptr_t *words, size_t word_count, size_t bit_len) {',
        'static int first_set_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {',
        'static int first_clear_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {',
        '        "      \\"name\\": \\"bitmap_full_range\\",\\n"',
        '        "      \\"name\\": \\"cpumask_subset_overlap\\",\\n"',
    ),
    EXPECTED_PATH: (
        '"word_bits": 64',
        '"name": "bitmap_full_range"',
        '"set_count": 67',
        '"name": "cpumask_presence"',
        '"present_count": 3',
        '"base_intersects_disjoint": false',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-bitmap-cpumask-starter-packet"',
        '"status": "helper_local_bitmap_cpumask_fixture_packet_present"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c"',
        '"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json"',
        '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py --repo-root . --cc gcc"',
    ),
}

SELF_TEST_CASES = (
    (DOC_PATH, "`zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`"),
    (BITMAP_VIEW_PATH, "pub fn firstClearBit(self: BitmapView) ?usize {"),
    (CPUMASK_VIEW_PATH, "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {"),
    (TEST_PATH, 'test "cpumask starter packet keeps subset and overlap semantics inside the bounded mask" {'),
    (BUILD_PATH, '"phase3-bitmap-cpumask-starter-packet"'),
    (C_HARNESS_PATH, '        "      \\"name\\": \\"cpumask_subset_overlap\\",\\n"'),
    (EXPECTED_PATH, '"base_intersects_disjoint": false'),
    (MANIFEST_PATH, '"status": "helper_local_bitmap_cpumask_fixture_packet_present"'),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _load_json(path: Path) -> object:
    return json.loads(_read(path))


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _resolve_tool(explicit: str | None, env_name: str, default: str) -> str:
    if explicit:
        return explicit
    return os.environ.get(env_name, default)


def _diff(label: str, expected: object, actual: object) -> str:
    expected_text = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    actual_text = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    diff = "".join(
        difflib.unified_diff(
            expected_text.splitlines(keepends=True),
            actual_text.splitlines(keepends=True),
            fromfile=f"{label}-expected",
            tofile=f"{label}-actual",
        )
    )
    return diff.strip() or f"{label} JSON differed without a textual diff"


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


def _run_c_harness(repo_root: Path, cc: str) -> object:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_c_") as temp_dir:
        binary = Path(temp_dir) / "phase3_bitmap_cpumask_c_harness"
        compile_result = _run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-pedantic",
                "-o",
                str(binary),
                str(repo_root / C_HARNESS_PATH),
            ],
            cwd=repo_root,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "c harness compile failed:\n"
                f"stdout:\n{compile_result.stdout}\n"
                f"stderr:\n{compile_result.stderr}"
            )
        run_result = _run([str(binary)], cwd=repo_root)
        if run_result.returncode != 0:
            raise RuntimeError(
                "c harness run failed:\n"
                f"stdout:\n{run_result.stdout}\n"
                f"stderr:\n{run_result.stderr}"
            )
        return json.loads(run_result.stdout)


def validate_repo(
    repo_root: Path,
    cc: str,
    *,
    skip_exec: bool = False,
) -> list[str]:
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

    if repo_reality_gaps != []:
        issues.append(
            "phase3_bitmap_cpumask_manifest.json repo_reality_gaps must be an empty list once the fixture packet lands"
        )

    if issues or skip_exec:
        return issues

    expected = _load_json(repo_root / EXPECTED_PATH)
    try:
        c_actual = _run_c_harness(repo_root, cc)
    except Exception as exc:
        issues.append(str(exc))
        return issues

    if c_actual != expected:
        issues.append(_diff("c-harness", expected, c_actual))

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        if relative_path in {EXPECTED_PATH, MANIFEST_PATH}:
            continue
        _write(root / relative_path, "\n".join(markers) + "\n")

    _write(
        root / EXPECTED_PATH,
        json.dumps(
            {
                "word_bits": 64,
                "cases": [
                    {
                        "name": "bitmap_full_range",
                        "capacity": 67,
                        "set_count": 67,
                        "first_set_bit": 0,
                        "first_clear_bit": None,
                    },
                    {
                        "name": "bitmap_sparse",
                        "capacity": 16,
                        "is_set_2": True,
                        "is_set_3": False,
                        "set_count": 2,
                        "first_set_bit": 2,
                        "first_clear_bit": 0,
                    },
                    {
                        "name": "cpumask_presence",
                        "capacity": 8,
                        "has_cpu_0": True,
                        "has_cpu_1": False,
                        "has_cpu_7": True,
                        "present_count": 3,
                        "first_cpu": 0,
                        "first_missing_cpu": 1,
                    },
                    {
                        "name": "cpumask_subset_overlap",
                        "capacity": 8,
                        "base_subset_of_superset": True,
                        "superset_subset_of_base": False,
                        "base_intersects_superset": True,
                        "base_intersects_disjoint": False,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )

    manifest = {
        **EXPECTED_MANIFEST_FIELDS,
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        "repo_reality_gaps": [],
    }
    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_bitmap_cpumask_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root, cc="gcc", skip_exec=True)
        if issues:
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root, cc="gcc", skip_exec=True)
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
        issues = validate_repo(root, cc="gcc", skip_exec=True)
        expected = "phase3_bitmap_cpumask_manifest.json packet_files duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected duplicate packet_files entry was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root, cc="gcc", skip_exec=True)
        expected = "phase3_bitmap_cpumask_manifest.json replay_routes duplicate entry:"
        if not any(issue.startswith(expected) for issue in issues):
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected duplicate replay_routes entry was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["still-open-gap"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root, cc="gcc", skip_exec=True)
        expected = (
            "phase3_bitmap_cpumask_manifest.json repo_reality_gaps must be an empty list "
            "once the fixture packet lands"
        )
        if expected not in issues:
            print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=fail")
            print("expected non-empty repo_reality_gaps was not reported")
            return 1

    print("PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST=pass")
    print(f"PHASE3_BITMAP_CPUMASK_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 3}")
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
    parser.add_argument("--cc", help="path to C compiler")
    parser.add_argument("--skip-exec", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    cc = _resolve_tool(args.cc, "CC", "gcc")
    issues = validate_repo(args.repo_root, cc, skip_exec=args.skip_exec)
    if issues:
        print("PHASE3_BITMAP_CPUMASK_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_BITMAP_CPUMASK_PACKET=pass")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    print(f"validated {args.repo_root / EXPECTED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
