#!/usr/bin/env python3
"""Fail-closed exact evidence checks for the Phase 6 bsearch corpus packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BSEARCH_PATH = Path("zigux/tests/phase6_bsearch.zig")
LOWER_UPPER_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
EQUALITY_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")


REQUIRED_SNIPPETS = {
    BSEARCH_PATH.as_posix(): [
        'const values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };',
        'const values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };',
        'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget"',
        'test "phase 6 bsearch keeps descending lookup work inside a binary-search budget"',
        'test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget"',
        'test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget"',
        'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers"',
    ],
    LOWER_UPPER_PATH.as_posix(): [
        "var ascending_storage: [32]u32 = undefined;",
        "var descending_storage: [32]u32 = undefined;",
        "var record_storage: [32]RawRecord = undefined;",
        'const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));',
        'test "phase 6 bsearch lower-bound c abi helpers match bounded insertion points across ascending and descending ranges"',
        'test "phase 6 bsearch upper-bound c abi helpers match bounded insertion points across ascending and descending ranges"',
        'test "phase 6 bsearch lower-bound c abi record member_size replay stays inside a binary-search budget"',
        'test "phase 6 bsearch upper-bound c abi record member_size replay stays inside a binary-search budget"',
    ],
    EQUALITY_PATH.as_posix(): [
        "var ascending_storage: [32]u32 = undefined;",
        "var descending_storage: [32]u32 = undefined;",
        "var record_storage: [32]RawRecord = undefined;",
        'const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 1));',
        'test "phase 6 bsearch direct c abi equality helpers stay inside a binary-search budget"',
    ],
    CATALOG_PATH.as_posix(): [
        "- exact corpus evidence: `zigux/tests/phase6_bsearch.zig` still anchors 15-element ascending and descending equality replays with five representative hit-or-miss probes each across typed and raw lookup paths, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig` still sweep dynamic lengths `0...32` plus packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` comparison budget",
    ],
}


EXACT_OCCURRENCE_MARKERS = {
    BSEARCH_PATH.as_posix(): [
        ("try std.testing.expect(counted_compare_calls <= 4);", 10),
        ("try std.testing.expect(counted_raw_compare_calls <= 4);", 10),
    ],
}


EXPECTED_BSEARCH_EVIDENCE = {
    "inline_corpus": "15-element ascending and descending sorted integer slices plus sorted symbol and packed-record replays",
    "representative_lookup_len": 15,
    "comparison_budget_typed_cases": 10,
    "comparison_budget_raw_cases": 10,
    "comparison_budget_max_compare_calls": 4,
    "lower_upper_dynamic_lengths": 33,
    "lower_upper_max_probe_formula": "len == 0 ? 1 : 2 * len + 2",
    "lower_upper_probe_count_formula": "len == 0 ? 2 : 2 * len + 3",
    "lower_upper_record_member_size_replay": True,
    "c_abi_equality_dynamic_lengths": 33,
    "c_abi_equality_max_probe_formula": "len == 0 ? 1 : 2 * len + 1",
    "c_abi_equality_record_member_size_replay": True,
}


REQUIRED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def validate_manifest(repo_root: Path) -> None:
    manifest_rel = MANIFEST_PATH.as_posix()
    manifest = read_json(repo_root / manifest_rel)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {manifest_rel}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {manifest_rel}")

    bsearch = determinism.get("bsearch")
    if not isinstance(bsearch, dict):
        raise ValidationError(f"missing determinism_evidence.bsearch in {manifest_rel}")

    for key, expected in EXPECTED_BSEARCH_EVIDENCE.items():
        actual = bsearch.get(key)
        if actual != expected:
            raise ValidationError(
                f"Phase 6 bsearch evidence drifted in {manifest_rel}: expected {key}={expected!r}, found {actual!r}"
            )

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks list in {manifest_rel}")
    for check in REQUIRED_EXACT_CHECKS:
        if check not in exact_checks:
            raise ValidationError(f"missing exact check in {manifest_rel}: {check}")


def run_checks(repo_root: Path) -> None:
    validate_manifest(repo_root)

    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(f"missing expected Phase 6 bsearch marker in {rel_path}: {snippet}")

    for rel_path, markers in EXACT_OCCURRENCE_MARKERS.items():
        content = read_text(repo_root / rel_path)
        for marker, expected in markers:
            occurrences = content.count(marker)
            if occurrences != expected:
                raise ValidationError(
                    f"expected {expected} occurrences of Phase 6 bsearch marker in {rel_path}, found {occurrences}: {marker}"
                )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    manifest = {
        "determinism_evidence": {
            "bsearch": dict(EXPECTED_BSEARCH_EVIDENCE),
        },
        "exact_checks": list(REQUIRED_EXACT_CHECKS),
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        lines = list(dict.fromkeys(snippets))
        for marker, expected in EXACT_OCCURRENCE_MARKERS.get(rel_path, []):
            lines.extend([marker] * expected)
        write(root / rel_path, "\n".join(lines) + "\n")


def assert_failure(root: Path, rel_path: str, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"missing self-test marker in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if rel_path not in str(exc):
            raise AssertionError(f"unexpected failure for {rel_path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"representative_lookup_len": 15',
            '"representative_lookup_len": 14',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            'check-phase6-bsearch-corpus-evidence.py --self-test',
            'check-phase6-bsearch-corpus-proof.py --self-test',
        )
        assert_failure(
            root,
            BSEARCH_PATH.as_posix(),
            'const values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };',
            'const values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42 };',
        )
        assert_failure(
            root,
            BSEARCH_PATH.as_posix(),
            'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers"',
            'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointer drift"',
        )
        assert_failure(
            root,
            LOWER_UPPER_PATH.as_posix(),
            'const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));',
            'const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 3));',
        )
        assert_failure(
            root,
            EQUALITY_PATH.as_posix(),
            'const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 1));',
            'const max_probe: u32 = if (len == 0) 1 else @as(u32, @intCast((len * 2) + 2));',
        )
        assert_failure(
            root,
            CATALOG_PATH.as_posix(),
            "- exact corpus evidence: `zigux/tests/phase6_bsearch.zig` still anchors 15-element ascending and descending equality replays with five representative hit-or-miss probes each across typed and raw lookup paths, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig` still sweep dynamic lengths `0...32` plus packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` comparison budget",
            "- exact corpus evidence: drifted",
        )
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 bsearch corpus evidence looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
