#!/usr/bin/env python3
"""Fail-closed exact evidence checks for the Phase 6 bsearch corpus packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BSEARCH_PATH = Path("zigux/tests/phase6_bsearch.zig")
LOWER_UPPER_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
EQUALITY_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")


FIXTURE_BASELINE = """const std = @import(\"std\");

pub const representative_ascending_values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };
pub const representative_descending_values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };

pub const representative_hit_queries = [_]u32{ 3, 21, 24, 39, 45 };
pub const representative_miss_queries = [_]u32{ 1, 10, 26, 44, 50 };

pub const sorted_symbols = [_][]const u8{
    \"do_exit\",
    \"kfree\",
    \"kmalloc\",
    \"schedule\",
};

pub const RawRecord = extern struct {
    key: u32,
    value: u32,
};

pub const packed_record_values = [_]RawRecord{
    .{ .key = 3, .value = 0x3000 },
    .{ .key = 8, .value = 0x8000 },
    .{ .key = 13, .value = 0xd000 },
    .{ .key = 21, .value = 0x15000 },
    .{ .key = 34, .value = 0x22000 },
    .{ .key = 55, .value = 0x37000 },
    .{ .key = 89, .value = 0x59000 },
};

pub const dynamic_case_lengths = [_]usize{
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32,
};

pub fn typedQuerySeed(index: usize) u32 {
    return representative_hit_queries[index % representative_hit_queries.len];
}

pub fn rawQuerySeed(index: usize) u32 {
    return representative_miss_queries[index % representative_miss_queries.len];
}

test \"phase 6 bsearch vectors stay deterministic and sorted\" {
    try std.testing.expectEqual(@as(usize, 15), representative_ascending_values.len);
    try std.testing.expectEqual(@as(usize, 15), representative_descending_values.len);
    try std.testing.expectEqual(@as(usize, 33), dynamic_case_lengths.len);

    for (representative_ascending_values, 0..) |value, index| {
        if (index > 0) {
            try std.testing.expect(representative_ascending_values[index - 1] < value);
        }
        try std.testing.expectEqual(value, representative_descending_values[representative_descending_values.len - 1 - index]);
    }

    for (dynamic_case_lengths, 0..) |length, index| {
        try std.testing.expectEqual(index, length);
    }
}
"""


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
    SLICE_PATH.as_posix(): [
        "- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, lower- or upper-bound companion, or packet-alignment drift appears",
        "- `equalRangeIndex`",
        "- `bsearchEqualRangeIndex`",
        "- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
        "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- direct local corpus evidence checker self-test: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`",
        "Current `master` also still carries `zigux/tests/fixtures/phase6_bsearch_vectors.zig` as a compact shared seed companion for the representative ascending, descending, hit-or-miss, symbol, and packed-record cases.",
    ],
    PERF_SURVEY_PATH.as_posix(): [
        "- bsearch shared posture: the live executable measurement evidence remains the algorithmic comparison-budget replays inside `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig`, not a separate wall-clock perf harness",
        "- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline sorted inputs plus the bundled comparison-budget replays rather than a separate fixture module or standalone `phase6_bsearch_perf` route",
    ],
}


EXACT_OCCURRENCE_MARKERS = {
    BSEARCH_PATH.as_posix(): [
        ("try std.testing.expect(counted_compare_calls <= 4);", 10),
        ("try std.testing.expect(counted_raw_compare_calls <= 4);", 10),
    ],
}


EXPECTED_BSEARCH_HELPER_ROW = {
    "id": "bsearch",
    "roadmap_anchor": "lib/bsearch.c",
    "helper": "lib/bsearch.zig",
    "tests": [
        "zigux/tests/phase6_bsearch.zig",
        "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
        "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    ],
    "fixtures": [
        "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    ],
    "slice_note": "Documentation/zigux/phase6-bsearch-slice.md",
    "corpus_evidence_checker": "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
}


EXPECTED_BSEARCH_PERF_POSTURE = {
    "replay": "zigux/tests/phase6_bsearch.zig",
    "measurement_mode": "comparison_budget",
    "typed_lookup_budget": 4,
    "raw_lookup_budget": 4,
    "representative_typed_cases": 10,
    "representative_raw_cases": 10,
    "lower_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "upper_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "equality_c_abi_replay": "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    "lower_bound_budget_formula": "std.math.log2_int_ceil(len) + 1",
    "upper_bound_budget_formula": "std.math.log2_int_ceil(len) + 1",
    "equality_budget_formula": "std.math.log2_int_ceil(len) + 1",
    "lower_bound_budget_surfaces": [
        "typed ascending and descending insertion-point ranges",
        "raw ascending and descending insertion-point ranges",
        "packed-record member_size insertion-point ranges",
        "alias-comparator empty and singleton insertion edges",
    ],
    "upper_bound_budget_surfaces": [
        "typed ascending and descending insertion-point ranges",
        "raw ascending and descending insertion-point ranges",
        "packed-record member_size insertion-point ranges",
        "alias-comparator empty and singleton insertion edges",
    ],
    "equality_budget_surfaces": [
        "typed ascending and descending equality ranges through runtime-selected c abi comparator pointers",
        "raw ascending and descending equality ranges through runtime-selected c abi comparator pointers",
        "packed-record member_size equality ranges through runtime-selected raw c abi comparator pointers",
    ],
}


EXPECTED_BSEARCH_INLINE_CORPUS_GOVERNANCE = {
    "focused_replay": "zigux/tests/phase6_bsearch.zig",
    "lower_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "upper_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "equality_c_abi_replay": "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    "fixture_companion": "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    "fixture_companion_role": "compact shared seed evidence for the representative ascending, descending, hit-or-miss, symbol, and packed-record cases while executable comparison-budget replays stay inline in the focused bsearch test files",
    "policy": "keep representative sorted slices, duplicate-bearing lower- and upper-bound insertion probes, direct c abi equality probes, and packed-record member_size cases inline in the focused bsearch replays instead of a separate Phase 6 fixture module",
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
    "fixture_companion": "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    "fixture_ascending_values": 15,
    "fixture_descending_values": 15,
    "fixture_hit_queries": 5,
    "fixture_miss_queries": 5,
    "fixture_sorted_symbols": 4,
    "fixture_packed_records": 7,
    "fixture_dynamic_case_lengths": 33,
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


def extract_array_body(content: str, prefix: str, rel_path: str) -> str:
    start = content.find(prefix)
    if start == -1:
        raise ValidationError(f"missing expected Phase 6 bsearch fixture array in {rel_path}: {prefix}")
    start += len(prefix)
    end = content.find("};", start)
    if end == -1:
        raise ValidationError(f"unterminated Phase 6 bsearch fixture array in {rel_path}: {prefix}")
    return content[start:end]


def parse_int_array(body: str) -> list[int]:
    return [int(item.strip()) for item in body.replace("\n", " ").split(",") if item.strip()]


def parse_string_array(body: str) -> list[str]:
    values: list[str] = []
    for item in body.replace("\n", " ").split(","):
        stripped = item.strip()
        if not stripped:
            continue
        if not (stripped.startswith('"') and stripped.endswith('"')):
            raise ValidationError(f"unexpected non-string item in fixture string array: {stripped}")
        values.append(stripped[1:-1])
    return values


def validate_fixture_content(repo_root: Path) -> None:
    rel_path = FIXTURE_PATH.as_posix()
    content = read_text(repo_root / rel_path)

    for marker in [
        'pub fn typedQuerySeed(index: usize) u32 {',
        'return representative_hit_queries[index % representative_hit_queries.len];',
        'pub fn rawQuerySeed(index: usize) u32 {',
        'return representative_miss_queries[index % representative_miss_queries.len];',
        'test "phase 6 bsearch vectors stay deterministic and sorted"',
    ]:
        if marker not in content:
            raise ValidationError(f"missing expected Phase 6 bsearch fixture marker in {rel_path}: {marker}")

    ascending = parse_int_array(
        extract_array_body(content, "pub const representative_ascending_values = [_]u32{", rel_path)
    )
    descending = parse_int_array(
        extract_array_body(content, "pub const representative_descending_values = [_]u32{", rel_path)
    )
    hits = parse_int_array(extract_array_body(content, "pub const representative_hit_queries = [_]u32{", rel_path))
    misses = parse_int_array(extract_array_body(content, "pub const representative_miss_queries = [_]u32{", rel_path))
    symbols = parse_string_array(extract_array_body(content, "pub const sorted_symbols = [_][]const u8{", rel_path))
    lengths = parse_int_array(extract_array_body(content, "pub const dynamic_case_lengths = [_]usize{", rel_path))
    record_body = extract_array_body(content, "pub const packed_record_values = [_]RawRecord{", rel_path)
    record_keys = [int(match.group(1)) for match in re.finditer(r"\.key = (\d+)", record_body)]

    if ascending != [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45]:
        raise ValidationError(f"unexpected ascending fixture corpus in {rel_path}: {ascending!r}")
    if descending != [45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3]:
        raise ValidationError(f"unexpected descending fixture corpus in {rel_path}: {descending!r}")
    if hits != [3, 21, 24, 39, 45]:
        raise ValidationError(f"unexpected representative hit queries in {rel_path}: {hits!r}")
    if misses != [1, 10, 26, 44, 50]:
        raise ValidationError(f"unexpected representative miss queries in {rel_path}: {misses!r}")
    if symbols != ["do_exit", "kfree", "kmalloc", "schedule"]:
        raise ValidationError(f"unexpected sorted symbol fixture corpus in {rel_path}: {symbols!r}")
    if record_keys != [3, 8, 13, 21, 34, 55, 89]:
        raise ValidationError(f"unexpected packed-record keys in {rel_path}: {record_keys!r}")
    if lengths != list(range(33)):
        raise ValidationError(f"unexpected dynamic case lengths in {rel_path}: {lengths!r}")


def validate_manifest(repo_root: Path) -> None:
    manifest_rel = MANIFEST_PATH.as_posix()
    manifest = read_json(repo_root / manifest_rel)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {manifest_rel}")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers list in {manifest_rel}")
    helper_row = next((item for item in helpers if isinstance(item, dict) and item.get("id") == "bsearch"), None)
    if helper_row != EXPECTED_BSEARCH_HELPER_ROW:
        raise ValidationError(
            f"Phase 6 bsearch helper row drifted in {manifest_rel}: expected {EXPECTED_BSEARCH_HELPER_ROW!r}, found {helper_row!r}"
        )

    perf_thresholds = manifest.get("perf_thresholds")
    if not isinstance(perf_thresholds, dict):
        raise ValidationError(f"missing perf_thresholds in {manifest_rel}")
    bsearch_perf = perf_thresholds.get("bsearch")
    if bsearch_perf != EXPECTED_BSEARCH_PERF_POSTURE:
        raise ValidationError(
            f"Phase 6 bsearch perf posture drifted in {manifest_rel}: expected {EXPECTED_BSEARCH_PERF_POSTURE!r}, found {bsearch_perf!r}"
        )

    fixture_posture = manifest.get("fixture_posture")
    if not isinstance(fixture_posture, dict):
        raise ValidationError(f"missing fixture_posture in {manifest_rel}")
    inline_corpus_governance = fixture_posture.get("inline_corpus_governance")
    if not isinstance(inline_corpus_governance, dict):
        raise ValidationError(f"missing fixture_posture.inline_corpus_governance in {manifest_rel}")
    bsearch_inline_governance = inline_corpus_governance.get("bsearch")
    if bsearch_inline_governance != EXPECTED_BSEARCH_INLINE_CORPUS_GOVERNANCE:
        raise ValidationError(
            f"Phase 6 bsearch inline corpus governance drifted in {manifest_rel}: expected {EXPECTED_BSEARCH_INLINE_CORPUS_GOVERNANCE!r}, found {bsearch_inline_governance!r}"
        )

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
    validate_fixture_content(repo_root)

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
        "helpers": [dict(EXPECTED_BSEARCH_HELPER_ROW)],
        "perf_thresholds": {"bsearch": dict(EXPECTED_BSEARCH_PERF_POSTURE)},
        "fixture_posture": {
            "inline_corpus_governance": {"bsearch": dict(EXPECTED_BSEARCH_INLINE_CORPUS_GOVERNANCE)},
        },
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

    write(root / FIXTURE_PATH, FIXTURE_BASELINE)


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
            '"roadmap_anchor": "lib/bsearch.c"',
            '"roadmap_anchor": "lib/bsearch-old.c"',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"fixtures": [\n        "zigux/tests/fixtures/phase6_bsearch_vectors.zig"\n      ]',
            '"fixtures": []',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"fixture_sorted_symbols": 4',
            '"fixture_sorted_symbols": 5',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"upper_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig"',
            '"upper_bound_c_abi_replay": "zigux/tests/phase6_bsearch_upper_bound_only.zig"',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"fixture_companion": "zigux/tests/fixtures/phase6_bsearch_vectors.zig"',
            '"fixture_companion": "zigux/tests/fixtures/phase6_bsearch_seed_vectors.zig"',
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
            FIXTURE_PATH.as_posix(),
            'pub const representative_miss_queries = [_]u32{ 1, 10, 26, 44, 50 };',
            'pub const representative_miss_queries = [_]u32{ 1, 10, 26, 44 };',
        )
        assert_failure(
            root,
            CATALOG_PATH.as_posix(),
            "- exact corpus evidence: `zigux/tests/phase6_bsearch.zig` still anchors 15-element ascending and descending equality replays with five representative hit-or-miss probes each across typed and raw lookup paths, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig` still sweep dynamic lengths `0...32` plus packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` comparison budget",
            "- exact corpus evidence: drifted",
        )
        assert_failure(
            root,
            SLICE_PATH.as_posix(),
            "- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, lower- or upper-bound companion, or packet-alignment drift appears",
            "- lane state: helper slice drifted",
        )
        assert_failure(
            root,
            SLICE_PATH.as_posix(),
            "- `equalRangeIndex`",
            "- `equalRangeDrift`",
        )
        assert_failure(
            root,
            SLICE_PATH.as_posix(),
            "Current `master` also still carries `zigux/tests/fixtures/phase6_bsearch_vectors.zig` as a compact shared seed companion for the representative ascending, descending, hit-or-miss, symbol, and packed-record cases.",
            "Current `master` still carries no fixture companion.",
        )
        assert_failure(
            root,
            PERF_SURVEY_PATH.as_posix(),
            "- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline sorted inputs plus the bundled comparison-budget replays rather than a separate fixture module or standalone `phase6_bsearch_perf` route",
            "- bsearch review-surface posture: drifted",
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
