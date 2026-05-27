#!/usr/bin/env python3
"""Fail closed on the exact Phase 4 rollback-ownership packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MATRIX = Path("Documentation/zigux/phase4-validation-matrix.md")
REVERSIBLE_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
PERF_MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
KPROBE_MANIFEST = Path("zigux/tests/phase4_kprobe_example_manifest.json")
TEST_FSMOUNT_MANIFEST = Path("zigux/tests/phase4_test_fsmount_manifest.json")

EXPECTED_SELF_TEST_CASES = 14

SELF_TEST_MATRIX = """# Phase 4 Validation Matrix

## Status
  * scope: name the rollback owners for each bounded gate or survey

## Lab And CI Matrix
  * `zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team`
  * `zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Shared Subsystems Pod`
  * `Documentation/zigux/phase4-kprobe-example-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`
  * `Documentation/zigux/phase4-test-fsmount-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`
  * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
  * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
"""

SELF_TEST_REVERSIBLE_NOTE = """# Phase 4 Reversible Delivery Evidence

Current direct contents reads in this run also confirmed that `Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates, and keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`.
"""

MATRIX_MARKERS = (
    "name the rollback owners for each bounded gate or survey",
    "`zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team`",
    "`zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Shared Subsystems Pod`",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md` `Validation and Perf Team` `Validation and Perf Team`",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
)

REVERSIBLE_NOTE_MARKERS = (
    "`Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates",
    "keeps `Validation and Perf Team` as the decision owner with `ABI and Runtime Team` plus `Shared Subsystems Pod` as coordination owners while shared CI perf promotion stays pending on current `master`",
)


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


def require_markers(text: str, markers: tuple[str, ...], label: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:{marker}")


def expect_json_value(payload: object, path: tuple[str | int, ...], expected: object, label: str, issues: list[str]) -> None:
    current = payload
    for step in path:
        try:
            current = current[step]
        except (KeyError, IndexError, TypeError):
            issues.append(f"{label}:{'.'.join(str(part) for part in path)}:missing")
            return
    if current != expected:
        issues.append(
            f"{label}:{'.'.join(str(part) for part in path)}:expected={expected!r}:actual={current!r}"
        )


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in (MATRIX, REVERSIBLE_NOTE, PERF_MANIFEST, KPROBE_MANIFEST, TEST_FSMOUNT_MANIFEST):
        if not (root / rel).is_file():
            issues.append(f"file:{rel.as_posix()}")
    if issues:
        return issues

    require_markers(read_text(root / MATRIX), MATRIX_MARKERS, "matrix_marker", issues)
    require_markers(read_text(root / REVERSIBLE_NOTE), REVERSIBLE_NOTE_MARKERS, "reversible_note_marker", issues)

    try:
        perf_manifest = json.loads(read_text(root / PERF_MANIFEST))
    except json.JSONDecodeError as exc:
        issues.append(f"perf_manifest:decode:{exc.msg}")
    else:
        expected_perf_values = (
            (("owner",), "Validation and Perf Team"),
            (("rollback_owner",), "Validation and Perf Team"),
            (("decision_owner",), "Validation and Perf Team"),
            (("coordination_owners",), ["ABI and Runtime Team", "Shared Subsystems Pod"]),
            (("gate_surfaces", 0, "surface"), "zigux/tests/atomic64_diff.zig"),
            (("gate_surfaces", 0, "gate_owner"), "ABI and Runtime Team"),
            (("gate_surfaces", 0, "gate_rollback_owner"), "ABI and Runtime Team"),
            (("gate_surfaces", 1, "surface"), "zigux/tests/bitmap_diff.zig"),
            (("gate_surfaces", 1, "gate_owner"), "Shared Subsystems Pod"),
            (("gate_surfaces", 1, "gate_rollback_owner"), "Shared Subsystems Pod"),
            (("atomic64", "gate_owner"), "ABI and Runtime Team"),
            (("atomic64", "gate_rollback_owner"), "ABI and Runtime Team"),
            (("bitmap", "gate_owner"), "Shared Subsystems Pod"),
            (("bitmap", "gate_rollback_owner"), "Shared Subsystems Pod"),
            (("promotion_decision", "owner"), "Validation and Perf Team"),
            (("promotion_decision", "coordination_owners"), ["ABI and Runtime Team", "Shared Subsystems Pod"]),
        )
        for path, expected in expected_perf_values:
            expect_json_value(perf_manifest, path, expected, "perf_manifest", issues)

    for rel, label in (
        (KPROBE_MANIFEST, "kprobe_manifest"),
        (TEST_FSMOUNT_MANIFEST, "test_fsmount_manifest"),
    ):
        try:
            payload = json.loads(read_text(root / rel))
        except json.JSONDecodeError as exc:
            issues.append(f"{label}:decode:{exc.msg}")
            continue
        expect_json_value(payload, ("owner",), "Validation and Perf Team", label, issues)
        expect_json_value(payload, ("rollback_owner",), "Validation and Perf Team", label, issues)

    return issues


def write_fixture_tree(root: Path) -> None:
    write_text(root / MATRIX, SELF_TEST_MATRIX)
    write_text(root / REVERSIBLE_NOTE, SELF_TEST_REVERSIBLE_NOTE)
    write_text(
        root / PERF_MANIFEST,
        json.dumps(
            {
                "owner": "Validation and Perf Team",
                "rollback_owner": "Validation and Perf Team",
                "decision_owner": "Validation and Perf Team",
                "coordination_owners": ["ABI and Runtime Team", "Shared Subsystems Pod"],
                "gate_surfaces": [
                    {
                        "surface": "zigux/tests/atomic64_diff.zig",
                        "gate_owner": "ABI and Runtime Team",
                        "gate_rollback_owner": "ABI and Runtime Team",
                    },
                    {
                        "surface": "zigux/tests/bitmap_diff.zig",
                        "gate_owner": "Shared Subsystems Pod",
                        "gate_rollback_owner": "Shared Subsystems Pod",
                    },
                ],
                "atomic64": {
                    "gate_owner": "ABI and Runtime Team",
                    "gate_rollback_owner": "ABI and Runtime Team",
                },
                "bitmap": {
                    "gate_owner": "Shared Subsystems Pod",
                    "gate_rollback_owner": "Shared Subsystems Pod",
                },
                "promotion_decision": {
                    "owner": "Validation and Perf Team",
                    "coordination_owners": ["ABI and Runtime Team", "Shared Subsystems Pod"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    for rel in (KPROBE_MANIFEST, TEST_FSMOUNT_MANIFEST):
        write_text(
            root / rel,
            json.dumps(
                {
                    "owner": "Validation and Perf Team",
                    "rollback_owner": "Validation and Perf Team",
                },
                indent=2,
            )
            + "\n",
        )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-rollback-owners-") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_ROLLBACK_OWNERS_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1
        variants = (
            (MATRIX, "`zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team`", "`zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `Validation and Perf Team`", "matrix_marker:`zigux/tests/atomic64_diff.zig` `ABI and Runtime Team` `ABI and Runtime Team`"),
            (MATRIX, "`zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Shared Subsystems Pod`", "`zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Validation and Perf Team`", "matrix_marker:`zigux/tests/bitmap_diff.zig` `Shared Subsystems Pod` `Shared Subsystems Pod`"),
            (REVERSIBLE_NOTE, "rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates", "owners for the landed `atomic64_diff` and `bitmap_diff` gates", "reversible_note_marker:`Documentation/zigux/phase4-validation-matrix.md` still names `ABI and Runtime Team` and `Shared Subsystems Pod` as the rollback owners for the landed `atomic64_diff` and `bitmap_diff` gates"),
            (PERF_MANIFEST, '"gate_rollback_owner": "ABI and Runtime Team"', '"gate_rollback_owner": "Validation and Perf Team"', "perf_manifest:gate_surfaces.0.gate_rollback_owner:expected='ABI and Runtime Team'"),
            (PERF_MANIFEST, '"gate_rollback_owner": "Shared Subsystems Pod"', '"gate_rollback_owner": "Validation and Perf Team"', "perf_manifest:gate_surfaces.1.gate_rollback_owner:expected='Shared Subsystems Pod'"),
            (PERF_MANIFEST, '"owner": "Validation and Perf Team"', '"owner": "Shared Subsystems Pod"', "perf_manifest:owner:expected='Validation and Perf Team'"),
            (KPROBE_MANIFEST, '"rollback_owner": "Validation and Perf Team"', '"rollback_owner": "Shared Subsystems Pod"', "kprobe_manifest:rollback_owner:expected='Validation and Perf Team'"),
            (TEST_FSMOUNT_MANIFEST, '"rollback_owner": "Validation and Perf Team"', '"rollback_owner": "Shared Subsystems Pod"', "test_fsmount_manifest:rollback_owner:expected='Validation and Perf Team'"),
        )
        for rel, old, new, expected_prefix in variants:
            write_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_ROLLBACK_OWNERS_SELF_TEST=fail")
                print(f"missing expected failure prefix: {expected_prefix}")
                return 1
            cases += 1

        for rel in (MATRIX, REVERSIBLE_NOTE):
            write_fixture_tree(root)
            (root / rel).unlink()
            if not expect_failure(root, f"file:{rel.as_posix()}"):
                print("PHASE4_ROLLBACK_OWNERS_SELF_TEST=fail")
                print(f"missing file case did not fail closed: {rel.as_posix()}")
                return 1
            cases += 1

        for rel, label in ((PERF_MANIFEST, "perf_manifest"), (KPROBE_MANIFEST, "kprobe_manifest"), (TEST_FSMOUNT_MANIFEST, "test_fsmount_manifest")):
            write_fixture_tree(root)
            write_text(root / rel, "{")
            if not expect_failure(root, f"{label}:decode:"):
                print("PHASE4_ROLLBACK_OWNERS_SELF_TEST=fail")
                print(f"broken JSON case did not fail closed: {label}")
                return 1
            cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_ROLLBACK_OWNERS_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_ROLLBACK_OWNERS_SELF_TEST=pass")
    print(f"PHASE4_ROLLBACK_OWNERS_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_root(Path(args.root).resolve())
    if issues:
        print("PHASE4_ROLLBACK_OWNERS=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE4_ROLLBACK_OWNERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
