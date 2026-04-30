#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_FILES = [
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-bsearch-c-parity.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-base64-slice.md",
    "Documentation/zigux/phase6-bsearch-slice.md",
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_perf.zig",
    "zigux/tests/phase6_bsearch_c_parity.zig",
    "zigux/tests/fixtures/phase6_bsearch_c_harness.c",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "zigux/tests/phase6_build.zig",
    ".github/workflows/zigux-bootstrap.yml",
]

MAKE_MARKERS = [
    "PHONY += phase6-validate phase6-test phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-perf phase6",
    "phase6-validate:",
    "scripts/zigux/validate-phase6.py",
    "phase6-test:",
    "zigux/tests/phase6_build.zig",
    "phase6-base64-perf:",
    "base64-perf --build-file zigux/tests/phase6_build.zig",
    "phase6-bsearch-perf:",
    "bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "phase6-checksum-perf:",
    "checksum-perf --build-file zigux/tests/phase6_build.zig",
    "phase6-hexdump-perf:",
    "hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "phase6: phase6-validate phase6-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 6 leaf helper gates",
    "make -C zigux phase6-validate",
    "Run Phase 6 leaf helper tests",
    "zig build test --build-file zigux/tests/phase6_build.zig --summary all",
]

SCRIPT_README_MARKERS = [
    "validate-phase6.py",
    "check-phase6-base64-c-parity.py",
    "check-phase6-bsearch-c-parity.py",
    "Phase 6 flow",
    "make -C zigux phase6-validate",
    "make -C zigux phase6",
    "per-helper perf targets",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_perf.zig",
    "zigux/tests/phase6_bsearch_c_parity.zig",
    "zigux/tests/fixtures/phase6_bsearch_c_harness.c",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
]

DOC_README_MARKERS = [
    "Phase 6 notes",
    "Documentation/zigux/phase6-base64-slice.md",
    "Documentation/zigux/phase6-bsearch-slice.md",
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "make -C zigux phase6-validate",
    "make -C zigux phase6",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
]

PHASE6_BUILD_MARKERS = [
    "../../lib/base64.zig",
    "../../lib/bsearch.zig",
    "../../lib/checksum.zig",
    "../../lib/hexdump.zig",
    "phase6_base64.zig",
    "phase6_bsearch.zig",
    "phase6_checksum.zig",
    "phase6_hexdump.zig",
    'b.step("test", "Run Phase 6 leaf helper tests")',
    'b.step("base64-perf", "Run the Phase 6 base64 performance sanity harness")',
    'b.step("bsearch-perf", "Run the Phase 6 bsearch performance sanity harness")',
    'b.step("checksum-perf", "Run the Phase 6 checksum performance sanity harness")',
    'b.step("hexdump-perf", "Run the Phase 6 hexdump performance sanity harness")',
]

BASE64_TEST_MARKERS = [
    'test "phase 6 base64 standard encode parity matches kernel vectors" {',
    'test "phase 6 base64 decode rejects invalid kernel-style vectors" {',
    'test "phase 6 base64 exact-fit buffers work across fixture vectors" {',
    "base64.DecodeError.InvalidInput",
    "base64.DecodeError.DestinationTooSmall",
    "for (fixtures.variant_decode_cases) |case| {",
]

BASE64_PERF_MARKERS = [
    "fn median3(a: u64, b: u64, c: u64) u64",
    "var encode_slowdown_samples: [3]u64 = undefined;",
    "var decode_slowdown_samples: [3]u64 = undefined;",
    "max_encode_slowdown_pct = 190",
    "max_decode_slowdown_pct = 320",
    "std.base64.standard.Encoder.encode",
    "std.base64.url_safe_no_pad.Encoder.encode",
    ".imap_no_pad => encodeImapReference(dst, src, false)",
    "const encode_slowdown_pct = median3(",
    "const decode_slowdown_pct = median3(",
    "try std.testing.expect(encode_slowdown_pct <= case.max_encode_slowdown_pct);",
    "try std.testing.expect(decode_slowdown_pct <= case.max_decode_slowdown_pct);",
]

BASE64_PARITY_SCRIPT_MARKERS = [
    'parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")',
    'GENERATED_INCLUDE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_generated_cases.inc"',
    'generated_cases = run_checked([zig, "run", str(CASE_GENERATOR)]).stdout',
    'GENERATED_INCLUDE.write_text(generated_cases, encoding="utf-8")',
    'print("PHASE6_BASE64_C_PARITY_SELF_TEST=pass")',
    'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
]

BASE64_SLICE_MARKERS = [
    "`PHASE6_SLICE=base64-leaf-helper`",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "generated-fixture handoff",
    "generated build template",
    "sorted-output normalization",
]

BSEARCH_TEST_MARKERS = [
    'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget" {',
    'test "phase 6 bsearch accepts runtime-selected comparator function pointers" {',
    'test "phase 6 bsearch accepts runtime-selected C ABI comparator pointers" {',
    'test "phase 6 bsearch exposes a mutable pointer when searching mutable storage" {',
    "counted_compare_calls += 1;",
    "try std.testing.expect(counted_compare_calls <= 4);",
]

BSEARCH_PERF_MARKERS = [
    "phase6-bsearch-perf",
    "avg_compare_calls={d:.2}",
    "max_compare_calls={}",
    "max_compare_budget={}",
    "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
    "try std.testing.expect(compare_calls <= max_compare_budget);",
    "try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));",
]

BSEARCH_PARITY_SCRIPT_MARKERS = [
    'parser.add_argument("--self-test", action="store_true", help="Run built-in parity-script checks")',
    'expect_system_exit(',
    '"missing_harness",',
    '"missing_runner",',
    'sorted_lines("mutable-hit\\t21\\t21\\nascending-hit\\t34\\t4\\n")',
    'print("PHASE6_BSEARCH_C_PARITY_SELF_TEST=pass")',
    'print("PHASE6_BSEARCH_C_PARITY_SELF_TEST_CASE_COUNT=6")',
    'print(f"PHASE6_BSEARCH_C_PARITY_CASES={len(c_lines)}")',
]

BSEARCH_SLICE_MARKERS = [
    "`PHASE6_SLICE=bsearch-leaf-helper`",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test",
    "binary-search comparison budget",
    "found-or-null basis without pinning a stable duplicate index",
]

CHECKSUM_TEST_MARKERS = [
    'test "fixture-backed compute parity covers the current checksum vectors" {',
    'test "partial sums compose across the fixture split matrix" {',
    'test "seeded partial accumulation matches the fixture-backed reference" {',
    'test "kunit-inspired carry discipline stays stable on the helper surface" {',
    'test "pseudo header accumulation matches the fixture-backed reference checksum" {',
    'test "incremental checksum replacements match full recomputation" {',
    "tcpUdpNofold",
    "checksum.replaceByDiff(old_checksum, diff)",
]

CHECKSUM_PERF_MARKERS = [
    "phase6-checksum-perf",
    "fn median3(a: u64, b: u64, c: u64) u64",
    "referencePartial",
    "const slowdown_pct = median3(",
    "try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);",
]

CHECKSUM_FIXTURE_MARKERS = [
    ".max_slowdown_pct = 150",
    '.name = "udp pseudo header",',
]

CHECKSUM_SLICE_MARKERS = [
    "`PHASE6_SLICE=checksum-leaf-helper`",
    "`replaceByDiff`",
    "carry-discipline edge cases on the helper-local surface",
    "widened-accumulator `referencePartial` path",
]

HEXDUMP_TEST_MARKERS = [
    'test "phase 6 hexdump exposes uppercase whole-buffer encoding" {',
    'test "phase 6 hexdump exposes append-style whole-buffer encoding" {',
    'test "phase 6 hexdump directly covers nibble, byte-pack, and decode helpers" {',
    'test "phase 6 hexdump replays serialized fixture vectors" {',
    'test "phase 6 hexdump overflow contract matches truncation expectations" {',
    'test "phase 6 hexdump covers normalization and empty-buffer edge cases" {',
    'test "phase 6 hexdump proves exact 4-byte grouped output" {',
    'test "phase 6 hexdump proves exact 4-byte grouped ascii output" {',
    "fixtures.prepareExpectedLine",
]

HEXDUMP_PERF_MARKERS = [
    "phase6-hexdump-perf",
    "fn median3(a: u64, b: u64, c: u64) u64",
    "max_slowdown_pct = 175",
    "fixtures.prepareExpectedLine(expected_buf[0..], case.len, case.rowsize, case.groupsize, case.ascii);",
    "const slowdown_pct = median3(",
    "try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);",
]

HEXDUMP_SLICE_MARKERS = [
    "`PHASE6_SLICE=hexdump-leaf-helper`",
    "uppercase whole-buffer hex encoding for a representative byte packet",
    "append-style whole-buffer encoding that can chain lowercase and uppercase segments without recomputing offsets",
    "direct nibble helper coverage for lowercase and uppercase hex digits",
    "direct byte-pack helper coverage for lowercase and uppercase output plus the short-buffer contract",
    "mixed-case hex digit decoding",
    "native-endian grouped output for 2, 4, and 8 byte cases",
    "fixtures.prepareExpectedLine(...)",
    "max_slowdown_pct = 175",
]

CATALOG_MARKERS = [
    "- verified head: `",
    "PHASE6_BASE64_C_PARITY_CASES=90",
    "PHASE6_BSEARCH_C_PARITY_CASES=17",
    "max_slowdown_pct = 150",
    "max_slowdown_pct = 175",
    "avg_compare_calls <= std.math.log2_int_ceil(len) + 1",
]

EXPECTED_MANIFEST = {
    "phase": "Phase 6",
    "status": "active",
    "tranche": "leaf-helper-parity",
    "roadmap_anchors": [
        "lib/base64.c",
        "lib/bsearch.c",
        "lib/checksum.c",
        "lib/hexdump.c",
    ],
    "helpers": [
        {
            "id": "base64",
            "helper": "lib/base64.zig",
            "tests": [
                "zigux/tests/phase6_base64.zig",
                "zigux/tests/phase6_base64_perf.zig",
                "zigux/tests/phase6_base64_c_parity.zig",
            ],
            "generators": [
                "zigux/tests/phase6_base64_c_casegen.zig",
            ],
            "fixtures": [
                "zigux/tests/fixtures/phase6_base64_vectors.zig",
                "zigux/tests/fixtures/phase6_base64_c_harness.c",
            ],
            "slice_note": "Documentation/zigux/phase6-base64-slice.md",
            "external_parity": "python3 scripts/zigux/check-phase6-base64-c-parity.py",
        },
        {
            "id": "bsearch",
            "helper": "lib/bsearch.zig",
            "tests": [
                "zigux/tests/phase6_bsearch.zig",
                "zigux/tests/phase6_bsearch_perf.zig",
                "zigux/tests/phase6_bsearch_c_parity.zig",
            ],
            "fixtures": [
                "zigux/tests/fixtures/phase6_bsearch_c_harness.c",
            ],
            "slice_note": "Documentation/zigux/phase6-bsearch-slice.md",
            "external_parity": "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
        },
        {
            "id": "checksum",
            "helper": "lib/checksum.zig",
            "tests": [
                "zigux/tests/phase6_checksum.zig",
                "zigux/tests/phase6_checksum_perf.zig",
            ],
            "fixtures": [
                "zigux/tests/fixtures/phase6_checksum_vectors.zig",
            ],
            "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
        },
        {
            "id": "hexdump",
            "helper": "lib/hexdump.zig",
            "tests": [
                "zigux/tests/phase6_hexdump.zig",
                "zigux/tests/phase6_hexdump_perf.zig",
            ],
            "fixtures": [
                "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
            ],
            "slice_note": "Documentation/zigux/phase6-hexdump-slice.md",
        },
    ],
    "shared_gates": [
        "zigux/tests/phase6_build.zig",
        "zigux/Makefile",
        "scripts/zigux/validate-phase6.py",
        ".github/workflows/zigux-bootstrap.yml",
        "Documentation/zigux/README.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "Documentation/zigux/phase6-helper-parity-catalog.md",
        "zigux/tests/phase6_helper_parity_manifest.json",
    ],
    "perf_posture": {
        "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
        "comparison_budget_helpers": ["bsearch"],
        "timing_sanity_only_helpers": [],
    },
    "fixture_posture": {
        "fixture_backed_helpers": ["base64", "checksum", "hexdump"],
        "inline_corpus_helpers": ["bsearch"],
    },
    "exact_checks": [
        "python3 scripts/zigux/validate-phase6.py",
        "make -C zigux phase6-validate",
        "make -C zigux phase6",
        "make -C zigux phase6-base64-perf",
        "make -C zigux phase6-bsearch-perf",
        "make -C zigux phase6-checksum-perf",
        "make -C zigux phase6-hexdump-perf",
        "python3 scripts/zigux/check-phase6-base64-c-parity.py",
        "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
    ],
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> object:
    return json.loads(text(path))


def collect_missing_files() -> list[str]:
    return [path for path in REQUIRED_FILES if not (ROOT / path).exists()]


def require_markers(missing: list[str], label: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{label}:missing:{marker}")


def require_manifest_equal(missing: list[str], manifest: dict[str, object], key: str, expected: object) -> None:
    actual = manifest.get(key)
    if actual != expected:
        missing.append(f"manifest:{key}")


def main() -> int:
    missing_files = collect_missing_files()
    if missing_files:
        print("PHASE6_VALIDATION=fail")
        print("MISSING_PHASE6_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE6_FILES_END")
        return 1

    makefile = text("zigux/Makefile")
    workflow = text(".github/workflows/zigux-bootstrap.yml")
    script_readme = text("scripts/zigux/README.md")
    tests_readme = text("zigux/tests/README.md")
    doc_readme = text("Documentation/zigux/README.md")
    phase6_build = text("zigux/tests/phase6_build.zig")
    phase6_catalog = text("Documentation/zigux/phase6-helper-parity-catalog.md")
    phase6_manifest = load_json("zigux/tests/phase6_helper_parity_manifest.json")

    catalog_head_match = re.search(r"- verified head: `([0-9a-f]{40})`", phase6_catalog)
    if catalog_head_match is None:
        print("PHASE6_VALIDATION=fail")
        print("PHASE6_CATALOG_HEAD_STATUS=missing")
        return 1
    catalog_head = catalog_head_match.group(1)
    if not HEX40.fullmatch(catalog_head):
        print("PHASE6_VALIDATION=fail")
        print("PHASE6_CATALOG_HEAD_STATUS=invalid")
        return 1

    missing: list[str] = []
    require_markers(missing, "make", makefile, MAKE_MARKERS)
    require_markers(missing, "workflow", workflow, WORKFLOW_MARKERS)
    require_markers(missing, "script_readme", script_readme, SCRIPT_README_MARKERS)
    require_markers(missing, "tests_readme", tests_readme, TESTS_README_MARKERS)
    require_markers(missing, "doc_readme", doc_readme, DOC_README_MARKERS)
    require_markers(missing, "phase6_build", phase6_build, PHASE6_BUILD_MARKERS)
    require_markers(missing, "phase6_catalog", phase6_catalog, CATALOG_MARKERS)

    file_marker_specs = [
        ("phase6_base64", "zigux/tests/phase6_base64.zig", BASE64_TEST_MARKERS),
        ("phase6_base64_perf", "zigux/tests/phase6_base64_perf.zig", BASE64_PERF_MARKERS),
        ("phase6_base64_c_parity_script", "scripts/zigux/check-phase6-base64-c-parity.py", BASE64_PARITY_SCRIPT_MARKERS),
        ("phase6_base64_slice", "Documentation/zigux/phase6-base64-slice.md", BASE64_SLICE_MARKERS),
        ("phase6_bsearch", "zigux/tests/phase6_bsearch.zig", BSEARCH_TEST_MARKERS),
        ("phase6_bsearch_perf", "zigux/tests/phase6_bsearch_perf.zig", BSEARCH_PERF_MARKERS),
        ("phase6_bsearch_c_parity_script", "scripts/zigux/check-phase6-bsearch-c-parity.py", BSEARCH_PARITY_SCRIPT_MARKERS),
        ("phase6_bsearch_slice", "Documentation/zigux/phase6-bsearch-slice.md", BSEARCH_SLICE_MARKERS),
        ("phase6_checksum", "zigux/tests/phase6_checksum.zig", CHECKSUM_TEST_MARKERS),
        ("phase6_checksum_perf", "zigux/tests/phase6_checksum_perf.zig", CHECKSUM_PERF_MARKERS),
        ("phase6_checksum_vectors", "zigux/tests/fixtures/phase6_checksum_vectors.zig", CHECKSUM_FIXTURE_MARKERS),
        ("phase6_checksum_slice", "Documentation/zigux/phase6-checksum-slice.md", CHECKSUM_SLICE_MARKERS),
        ("phase6_hexdump", "zigux/tests/phase6_hexdump.zig", HEXDUMP_TEST_MARKERS),
        ("phase6_hexdump_perf", "zigux/tests/phase6_hexdump_perf.zig", HEXDUMP_PERF_MARKERS),
        ("phase6_hexdump_slice", "Documentation/zigux/phase6-hexdump-slice.md", HEXDUMP_SLICE_MARKERS),
    ]

    for label, path, markers in file_marker_specs:
        require_markers(missing, label, text(path), markers)

    if not isinstance(phase6_manifest, dict):
        missing.append("manifest:root")
    else:
        surveyed_commit = phase6_manifest.get("surveyed_commit")
        if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
            missing.append("manifest:surveyed_commit")
        elif surveyed_commit != catalog_head:
            missing.append("manifest:surveyed_commit_mismatch")

        for key, expected in EXPECTED_MANIFEST.items():
            require_manifest_equal(missing, phase6_manifest, key, expected)

    if missing:
        print("PHASE6_VALIDATION=fail")
        print("PHASE6_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE6_MISSING_END")
        return 1

    total_marker_count = (
        len(MAKE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(SCRIPT_README_MARKERS)
        + len(TESTS_README_MARKERS)
        + len(DOC_README_MARKERS)
        + len(PHASE6_BUILD_MARKERS)
        + len(CATALOG_MARKERS)
        + len(BASE64_TEST_MARKERS)
        + len(BASE64_PERF_MARKERS)
        + len(BASE64_PARITY_SCRIPT_MARKERS)
        + len(BASE64_SLICE_MARKERS)
        + len(BSEARCH_TEST_MARKERS)
        + len(BSEARCH_PERF_MARKERS)
        + len(BSEARCH_PARITY_SCRIPT_MARKERS)
        + len(BSEARCH_SLICE_MARKERS)
        + len(CHECKSUM_TEST_MARKERS)
        + len(CHECKSUM_PERF_MARKERS)
        + len(CHECKSUM_FIXTURE_MARKERS)
        + len(CHECKSUM_SLICE_MARKERS)
        + len(HEXDUMP_TEST_MARKERS)
        + len(HEXDUMP_PERF_MARKERS)
        + len(HEXDUMP_SLICE_MARKERS)
    )

    print("PHASE6_VALIDATION=pass")
    print(f"PHASE6_REQUIRED_MARKER_COUNT={total_marker_count}")
    print(f"PHASE6_CATALOG_VERIFIED_HEAD={catalog_head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
