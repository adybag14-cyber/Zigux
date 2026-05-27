#!/usr/bin/env python3
"""Fail closed on the landed Phase 4 ownership and lab-matrix rows."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
ATOMIC64_MANIFEST = Path("zigux/tests/phase4_runtime_atomic64_diff_manifest.json")
BITMAP_MANIFEST = Path("zigux/tests/phase4_bitmap_diff_manifest.json")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")

EXPECTED_SELF_TEST_CASES = 15


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_atomic64_matrix_line(atomic64_manifest: dict[str, object]) -> str:
    owner = atomic64_manifest["owner"]
    rollback_owner = atomic64_manifest["rollback_owner"]
    replay = "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig"
    threshold = atomic64_manifest["threshold_posture"]
    return (
        f"`zigux/tests/atomic64_diff.zig` bounded runtime atomic64 rollback-readiness replay "
        f"covering arithmetic, exchange, cmpxchg, add_unless, `inc_not_zero`, "
        f"`dec_if_positive`, bitwise expectations, and the checksum-backed threshold-replay "
        f"route shared with `zigux/tests/runtime_atomic64_diff.zig` `{owner}` "
        f"`{rollback_owner}` `python3 scripts/zigux/validate-phase4.py` then "
        f"`zig build test --build-file zigux/tests/phase4_build.zig` in "
        f"`.github/workflows/zigux-bootstrap.yml` `{replay}` `{threshold}`"
    )


def build_bitmap_matrix_line(bitmap_manifest: dict[str, object]) -> str:
    owner = bitmap_manifest["owner"]
    rollback_owner = bitmap_manifest["rollback_owner"]
    replay = "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig"
    threshold = bitmap_manifest["threshold_posture"]
    return (
        f"`zigux/tests/bitmap_diff.zig` bounded broad bitmap rollback-readiness replay "
        f"covering exact range and prefix cases, zero-length range and prefix no-op rollback "
        f"checks, copy-tail and zero-length copy invariants, exact `find_nth_bit`, "
        f"out-of-bounds rejection, manifest-backed source inventory, and checksum-pinned "
        f"threshold-replay checkpoints `{owner}` `{rollback_owner}` "
        f"`python3 scripts/zigux/validate-phase4.py` then "
        f"`zig build test --build-file zigux/tests/phase4_build.zig` in "
        f"`.github/workflows/zigux-bootstrap.yml` `{replay}` `{threshold}`"
    )


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    matrix_path = root / MATRIX
    atomic64_manifest_path = root / ATOMIC64_MANIFEST
    bitmap_manifest_path = root / BITMAP_MANIFEST
    perf_manifest_path = root / PERF_MANIFEST

    for path in (matrix_path, atomic64_manifest_path, bitmap_manifest_path, perf_manifest_path):
        if not path.is_file():
            issues.append(f"file:{path.relative_to(root).as_posix()}")
    if issues:
        return issues

    try:
        atomic64_manifest = json.loads(read_text(atomic64_manifest_path))
    except json.JSONDecodeError as exc:
        return [f"atomic64_manifest:decode:{exc.msg}"]

    try:
        bitmap_manifest = json.loads(read_text(bitmap_manifest_path))
    except json.JSONDecodeError as exc:
        return [f"bitmap_manifest:decode:{exc.msg}"]

    try:
        perf_manifest = json.loads(read_text(perf_manifest_path))
    except json.JSONDecodeError as exc:
        return [f"perf_manifest:decode:{exc.msg}"]

    matrix_text = read_text(matrix_path)
    atomic64_line = build_atomic64_matrix_line(atomic64_manifest)
    bitmap_line = build_bitmap_matrix_line(bitmap_manifest)

    if atomic64_line not in matrix_text:
        issues.append(f"matrix_line_missing:{atomic64_line}")
    if bitmap_line not in matrix_text:
        issues.append(f"matrix_line_missing:{bitmap_line}")

    perf_gate_surfaces = perf_manifest.get("gate_surfaces")
    if not isinstance(perf_gate_surfaces, list) or len(perf_gate_surfaces) < 2:
        issues.append("perf_manifest:gate_surfaces:missing_or_short")
        return issues

    atomic64_surface = perf_gate_surfaces[0]
    bitmap_surface = perf_gate_surfaces[1]
    if atomic64_surface.get("surface") != "zigux/tests/atomic64_diff.zig":
        issues.append(
            "perf_manifest:gate_surfaces.0.surface:"
            f"expected='zigux/tests/atomic64_diff.zig':actual={atomic64_surface.get('surface')!r}"
        )
    if atomic64_surface.get("gate_owner") != atomic64_manifest["owner"]:
        issues.append(
            "perf_manifest:gate_surfaces.0.gate_owner:"
            f"expected={atomic64_manifest['owner']!r}:actual={atomic64_surface.get('gate_owner')!r}"
        )
    if atomic64_surface.get("gate_rollback_owner") != atomic64_manifest["rollback_owner"]:
        issues.append(
            "perf_manifest:gate_surfaces.0.gate_rollback_owner:"
            f"expected={atomic64_manifest['rollback_owner']!r}:actual={atomic64_surface.get('gate_rollback_owner')!r}"
        )
    if atomic64_surface.get("threshold_posture") != atomic64_manifest["threshold_posture"]:
        issues.append(
            "perf_manifest:gate_surfaces.0.threshold_posture:"
            f"expected={atomic64_manifest['threshold_posture']!r}:actual={atomic64_surface.get('threshold_posture')!r}"
        )

    if bitmap_surface.get("surface") != "zigux/tests/bitmap_diff.zig":
        issues.append(
            "perf_manifest:gate_surfaces.1.surface:"
            f"expected='zigux/tests/bitmap_diff.zig':actual={bitmap_surface.get('surface')!r}"
        )
    if bitmap_surface.get("gate_owner") != bitmap_manifest["owner"]:
        issues.append(
            "perf_manifest:gate_surfaces.1.gate_owner:"
            f"expected={bitmap_manifest['owner']!r}:actual={bitmap_surface.get('gate_owner')!r}"
        )
    if bitmap_surface.get("gate_rollback_owner") != bitmap_manifest["rollback_owner"]:
        issues.append(
            "perf_manifest:gate_surfaces.1.gate_rollback_owner:"
            f"expected={bitmap_manifest['rollback_owner']!r}:actual={bitmap_surface.get('gate_rollback_owner')!r}"
        )
    if bitmap_surface.get("threshold_posture") != bitmap_manifest["threshold_posture"]:
        issues.append(
            "perf_manifest:gate_surfaces.1.threshold_posture:"
            f"expected={bitmap_manifest['threshold_posture']!r}:actual={bitmap_surface.get('threshold_posture')!r}"
        )

    return issues


def build_fixture_tree(root: Path) -> None:
    atomic64_manifest = {
        "owner": "ABI and Runtime Team",
        "rollback_owner": "ABI and Runtime Team",
        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
    }
    bitmap_manifest = {
        "owner": "Shared Subsystems Pod",
        "rollback_owner": "Shared Subsystems Pod",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    }
    perf_manifest = {
        "gate_surfaces": [
            {
                "surface": "zigux/tests/atomic64_diff.zig",
                "gate_owner": atomic64_manifest["owner"],
                "gate_rollback_owner": atomic64_manifest["rollback_owner"],
                "threshold_posture": atomic64_manifest["threshold_posture"],
            },
            {
                "surface": "zigux/tests/bitmap_diff.zig",
                "gate_owner": bitmap_manifest["owner"],
                "gate_rollback_owner": bitmap_manifest["rollback_owner"],
                "threshold_posture": bitmap_manifest["threshold_posture"],
            },
        ]
    }

    write_text(root / ATOMIC64_MANIFEST, json.dumps(atomic64_manifest, indent=2) + "\n")
    write_text(root / BITMAP_MANIFEST, json.dumps(bitmap_manifest, indent=2) + "\n")
    write_text(root / PERF_MANIFEST, json.dumps(perf_manifest, indent=2) + "\n")
    write_text(
        root / MATRIX,
        "\n".join(
            [
                "# Phase 4 Validation Matrix",
                "",
                "## Lab And CI Matrix",
                f"  * {build_atomic64_matrix_line(atomic64_manifest)}",
                f"  * {build_bitmap_matrix_line(bitmap_manifest)}",
                "",
            ]
        ),
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-ownership-matrix-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_OWNERSHIP_MATRIX_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1
        variants = (
            (MATRIX, "`ABI and Runtime Team`", "`Validation and Perf Team`", "matrix_line_missing:`zigux/tests/atomic64_diff.zig`"),
            (MATRIX, "`Shared Subsystems Pod` `Shared Subsystems Pod`", "`Shared Subsystems Pod` `Validation and Perf Team`", "matrix_line_missing:`zigux/tests/bitmap_diff.zig`"),
            (MATRIX, "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`", "`make -C zigux phase4-runtime-atomic64-diff`", "matrix_line_missing:`zigux/tests/atomic64_diff.zig`"),
            (MATRIX, "`zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig`", "`make -C zigux phase4-bitmap-diff`", "matrix_line_missing:`zigux/tests/bitmap_diff.zig`"),
            (ATOMIC64_MANIFEST, "\"rollback_owner\": \"ABI and Runtime Team\"", "\"rollback_owner\": \"Validation and Perf Team\"", "matrix_line_missing:`zigux/tests/atomic64_diff.zig`"),
            (BITMAP_MANIFEST, "\"threshold_posture\": \"threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks\"", "\"threshold_posture\": \"reviewability_only_no_perf_threshold\"", "matrix_line_missing:`zigux/tests/bitmap_diff.zig`"),
            (PERF_MANIFEST, "\"gate_owner\": \"ABI and Runtime Team\"", "\"gate_owner\": \"Validation and Perf Team\"", "perf_manifest:gate_surfaces.0.gate_owner:"),
            (PERF_MANIFEST, "\"gate_rollback_owner\": \"Shared Subsystems Pod\"", "\"gate_rollback_owner\": \"Validation and Perf Team\"", "perf_manifest:gate_surfaces.1.gate_rollback_owner:"),
            (PERF_MANIFEST, "\"surface\": \"zigux/tests/bitmap_diff.zig\"", "\"surface\": \"zigux/tests/phase4_bitmap_diff_survey.zig\"", "perf_manifest:gate_surfaces.1.surface:"),
            (PERF_MANIFEST, "\"threshold_posture\": \"threshold_pending_until_runtime_atomic64_scope_widens\"", "\"threshold_posture\": \"shared_ci_perf_promotion_pending\"", "perf_manifest:gate_surfaces.0.threshold_posture:"),
        )
        for rel, old, new, expected_prefix in variants:
            build_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_OWNERSHIP_MATRIX_SELF_TEST=fail")
                print(f"drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        for rel, label in (
            (ATOMIC64_MANIFEST, "atomic64_manifest"),
            (BITMAP_MANIFEST, "bitmap_manifest"),
            (PERF_MANIFEST, "perf_manifest"),
        ):
            build_fixture_tree(root)
            write_text(root / rel, "{")
            if not expect_failure(root, f"{label}:decode:"):
                print("PHASE4_OWNERSHIP_MATRIX_SELF_TEST=fail")
                print(f"broken JSON case did not fail closed: {label}")
                return 1
            cases += 1

        build_fixture_tree(root)
        (root / MATRIX).unlink()
        if not expect_failure(root, f"file:{MATRIX.as_posix()}"):
            print("PHASE4_OWNERSHIP_MATRIX_SELF_TEST=fail")
            print("missing matrix file case did not fail closed")
            return 1
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_OWNERSHIP_MATRIX_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

        print("PHASE4_OWNERSHIP_MATRIX_SELF_TEST=pass")
        print(f"PHASE4_OWNERSHIP_MATRIX_SELF_TEST_CASES={cases}")
        return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    issues = validate_root(Path(args.root).resolve())
    if issues:
        print("PHASE4_OWNERSHIP_MATRIX=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE4_OWNERSHIP_MATRIX=pass")
    print("PHASE4_OWNERSHIP_MATRIX_ROW_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
