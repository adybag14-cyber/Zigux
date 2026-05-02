#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SELF_TEST_HEAD = "0123456789abcdef0123456789abcdef01234567"
SELF_TEST_MUTATED_HEAD = "fedcba9876543210fedcba9876543210fedcba98"

REQUIRED_FILES = [
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-bsearch-c-parity.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-base64-slice.md",
    "Documentation/zigux/phase6-bsearch-slice.md",
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "lib/base64.zig",
    "lib/bsearch.zig",
    "lib/checksum.zig",
    "lib/hexdump.zig",
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
    "zigux/tests/phase6_helper_parity_manifest.json",
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
    "zigux/tests/phase6_helper_parity_manifest.json",
    "refresh `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json` whenever the shipped Phase 6 helper inventory, perf entrypoints, fixtures, or shared slice notes change",
]

DOC_README_MARKERS = [
    "Phase 6 notes",
    "Documentation/zigux/phase6-base64-slice.md",
    "Documentation/zigux/phase6-bsearch-slice.md",
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "make -C zigux phase6-validate",
    "make -C zigux phase6",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
]

PERF_SURVEY_MARKERS = [
    "# Phase 6 Perf Gate Survey",
    "The current bounded Phase 6 perf packet still stops at the four roadmap-backed leaf helpers:",
    "`lib/base64.zig`",
    "`lib/bsearch.zig`",
    "`lib/checksum.zig`",
    "`lib/hexdump.zig`",
    "`make -C zigux phase6-base64-perf`",
    "`make -C zigux phase6-bsearch-perf`",
    "`make -C zigux phase6-checksum-perf`",
    "`make -C zigux phase6-hexdump-perf`",
    "max_encode_slowdown_pct = 190",
    "max_decode_slowdown_pct = 320",
    "std.math.log2_int_ceil(len) + 1",
    "max_slowdown_pct = 150",
    "16B-ascii-g8",
    "max_slowdown_pct = 600",
    "perf gates for math-sensitive helpers",
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

BASE64_HELPER_MARKERS = [
    "pub const Variant = enum {",
    "pub fn chars(nbytes: usize, padding: bool) usize {",
    "pub fn encode(dst: []u8, src: []const u8, padding: bool, variant: Variant) EncodeError!usize {",
    "pub fn decode(dst: []u8, src: []const u8, padding: bool, variant: Variant) DecodeError!usize {",
]

BSEARCH_HELPER_MARKERS = [
    "pub fn Comparator(comptime Key: type, comptime T: type) type {",
    "pub const RawComparator = *const fn (*const anyopaque, *const anyopaque) i32;",
    "pub fn bsearchIndex(",
    "pub fn searchIndex(",
    "pub fn searchMutable(",
]

CHECKSUM_HELPER_MARKERS = [
    "pub fn add(sum: u32, addend: u32) u32 {",
    "pub fn replaceByDiff(sum: u16, diff: u32) u16 {",
    "pub fn tcpUdpNofold(sum: u32, saddr: u32, daddr: u32, len: u16, proto: u8) u32 {",
    "pub fn tcpUdpV6Nofold(sum: u32, saddr: [16]u8, daddr: [16]u8, len: u32, proto: u8) u32 {",
    "pub fn compute(bytes: []const u8) u16 {",
]

HEXDUMP_HELPER_MARKERS = [
    'pub const hex_asc = "0123456789abcdef";',
    "pub fn hexBytePack(buf: []u8, byte: u8) HexError![]u8 {",
    "pub fn bin2hexUpper(dst: []u8, src: []const u8) HexError![]u8 {",
    "pub fn hexDumpLineLength(",
    "pub fn hexDumpToBuffer(",
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
    'print("PHASE6_BASE64_C_PARITY_SELF_TEST_CASE_COUNT=8")',
    'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
]

BASE64_C_PARITY_RUNNER_MARKERS = [
    'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
    "for (fixtures.standard_cases) |case| {",
    "for (fixtures.variant_cases) |case| {",
    "for (fixtures.standard_decode_cases) |case| {",
    "for (fixtures.variant_decode_cases) |case| {",
    "for (fixtures.invalid_decode_cases) |case| {",
    'if (std.mem.eql(u8, name, "imap")) {',
]

BASE64_CASEGEN_MARKERS = [
    'try writer.writeAll("/* Generated from zigux/tests/fixtures/phase6_base64_vectors.zig. */\\n\\n");',
    "for (fixtures.variant_cases, 0..) |case, idx| {",
    "for (fixtures.variant_decode_cases, 0..) |case, idx| {",
    'try writer.writeAll("static const struct invalid_case invalid_cases[] = {\\n");',
    'if (std.mem.eql(u8, name, "imap")) return "BASE64_IMAP";',
    'return if (value) "true" else "false";',
]

BASE64_C_HARNESS_MARKERS = [
    "BASE64_IMAP = 2,",
    '[BASE64_IMAP] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,",',
    "[BASE64_IMAP] = BASE64_REV_INIT('+', ','),",
    '#include "phase6_base64_c_generated_cases.inc"',
    'printf("enc\\t%s\\t%d\\t", variant_name(c->variant), c->padding ? 1 : 0);',
    'printf("dec\\t%s\\t%d\\t%d\\t", variant_name(c->variant), c->padding ? 1 : 0, bytes_result);',
    'printf("\\t%s\\t%s\\n", bytes_result < 0 ? "InvalidInput" : "ok", decode_result < 0 ? "InvalidInput" : "ok");',
]

BASE64_VECTORS_MARKERS = [
    "pub const standard_cases = [_]EncodeCase{",
    '.{ .input = &variant_sample, .expected = "APv,f4A", .padding = false, .variant_name = "imap" },',
    '.{ .input = "APv,f4A", .expected = &variant_sample, .padding = false, .variant_name = "imap" },',
    '.{ .input = ",,A", .expected = &variant_two_byte_sample, .padding = false, .variant_name = "imap" },',
    '.{ .input = "+x", .padding = false, .variant_name = "imap" },',
    "pub const perf_cases = [_]PerfCase{",
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
    'test "phase 6 bsearch exposes the raw Linux-style helper contract" {',
    'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget" {',
    'test "phase 6 bsearch accepts runtime-selected comparator function pointers" {',
    'test "phase 6 bsearch accepts runtime-selected C ABI comparator pointers" {',
    'test "phase 6 bsearch accepts runtime-selected raw comparator pointers" {',
    'test "phase 6 bsearch accepts runtime-selected C ABI raw comparator pointers" {',
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
    'print("PHASE6_BSEARCH_C_PARITY_SELF_TEST=pass")',
    'print("PHASE6_BSEARCH_C_PARITY_SELF_TEST_CASE_COUNT=6")',
    'print(f"PHASE6_BSEARCH_C_PARITY_CASES={len(c_lines)}")',
]

BSEARCH_C_PARITY_RUNNER_MARKERS = [
    "const descending_values = [_]u32{ 89, 55, 34, 21, 13, 8, 3 };",
    'try writeIndexCase(writer, "descending-hit", 34, bsearch.searchIndex(u32, u32, &@as(u32, 34), descending_values[0..], compareDescendingU32));',
    'try writeDuplicateCase(writer, "duplicate-hit-middle", 7, bsearch.searchIndex(u32, u32, &@as(u32, 7), duplicate_in_middle[0..], compareU32));',
    'try writeIndexCase(writer, "raw-descending-hit", 34, bsearch.bsearchIndex(&@as(u32, 34), @ptrCast(descending_values[0..].ptr), descending_values.len, @sizeOf(u32), compareOpaqueDescendingU32));',
    "try writeRuntimeTypedCases(writer, values[0..], descending_values[0..]);",
    "try writeRuntimeRawCases(writer, values[0..], descending_values[0..]);",
    'try writer.print("raw-mutable-hit\\t21\\t{}\\n", .{raw_mutable_values[3]});',
]

BSEARCH_C_HARNESS_MARKERS = [
    "static int compare_descending_u32(const void *key, const void *elt)",
    'print_index_case("descending-hit", key, descending_values, inline_bsearch(&key, descending_values, sizeof(descending_values) / sizeof(descending_values[0]), sizeof(descending_values[0]), compare_descending_u32));',
    'print_duplicate_case("duplicate-hit-middle", key, duplicate_in_middle, inline_bsearch(&key, duplicate_in_middle, sizeof(duplicate_in_middle) / sizeof(duplicate_in_middle[0]), sizeof(duplicate_in_middle[0]), compare_u32));',
    'print_index_case("raw-descending-hit", key, descending_values, inline_bsearch(&key, descending_values, sizeof(descending_values) / sizeof(descending_values[0]), sizeof(descending_values[0]), compare_descending_u32));',
    "print_runtime_typed_cases(values, sizeof(values) / sizeof(values[0]), descending_values, sizeof(descending_values) / sizeof(descending_values[0]));",
    "print_runtime_raw_cases(values, sizeof(values) / sizeof(values[0]), descending_values, sizeof(descending_values) / sizeof(descending_values[0]));",
    'printf("raw-mutable-hit\\t21\\t%u\\n", raw_mutable_values[3]);',
]

BSEARCH_SLICE_MARKERS = [
    "`PHASE6_SLICE=bsearch-leaf-helper`",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test",
    "binary-search comparison budget",
    "`RawComparator`",
    "`bsearchMutable`",
    "found-or-null basis without pinning a stable duplicate index",
]

CHECKSUM_TEST_MARKERS = [
    'test "phase 6 checksum module imports cleanly" {',
    'test "fixture-backed compute parity covers the current checksum vectors" {',
    'test "partial sums compose across the fixture split matrix" {',
    'test "seeded partial accumulation matches the fixture-backed reference" {',
    'test "kunit-inspired carry discipline stays stable on the helper surface" {',
    'test "kunit random-prefix parity stays stable on the helper surface" {',
    'test "pseudo header accumulation matches the fixture-backed reference checksum" {',
    'test "IPv6 pseudo header accumulation matches the fixture-backed reference checksum" {',
    'test "incremental checksum replacements match full recomputation" {',
    "tcpUdpNofold",
    "tcpUdpV6Nofold",
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
    "for (fixtures.perf_cases) |case| {",
    "fn runPerfCase(case: fixtures.PerfCase, io: std.Io) !PerfResult {",
    "fixtures.prepareExpectedLine(expected_buf[0..], case.len, case.rowsize, case.groupsize, case.ascii);",
    "const slowdown_pct = median3(",
    "try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);",
]

HEXDUMP_FIXTURE_MARKERS = [
    "pub const PerfCase = struct {",
    "pub const perf_cases = [_]PerfCase{",
    '.{ .label = "16B-plain", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175 },',
    '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550 },',
    '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550 },',
    '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 },',
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
    "shared `zigux/tests/fixtures/phase6_hexdump_vectors.zig` perf-case table",
    "native-endian 4-byte and 8-byte grouped ASCII branches",
    "max_slowdown_pct = 175",
    "max_slowdown_pct = 550",
    "max_slowdown_pct = 600",
]

CATALOG_MARKERS = [
    "- verified head: `",
    "PHASE6_BASE64_C_PARITY_CASES=96",
    "PHASE6_BSEARCH_C_PARITY_CASES=29",
    "shared portability coverage: `zigux/tests/phase6_bsearch.zig` now exercises both typed and raw runtime-selected comparator pointers across native and C ABI paths",
    "max_slowdown_pct = 150",
    "max_slowdown_pct = 175",
    "max_slowdown_pct = 550",
    "max_slowdown_pct = 600",
    "avg_compare_calls <= std.math.log2_int_ceil(len) + 1",
    "PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=13",
]

EXPECTED_BASE64_DETERMINISM = {
    "standard_encode_vectors": 22,
    "variant_encode_vectors": 18,
    "standard_decode_vectors": 22,
    "variant_decode_vectors": 12,
    "invalid_decode_vectors": 22,
    "c_parity_self_test_cases": 8,
    "c_parity_cases": 96,
}

EXPECTED_BSEARCH_DETERMINISM = {
    "inline_corpus": "sorted integer and symbol tables",
    "c_parity_self_test_cases": 6,
    "c_parity_cases": 29,
}

EXPECTED_CHECKSUM_DETERMINISM = {
    "compute_vectors": 5,
    "composition_vectors": 2,
    "seeded_vectors": 3,
    "ipv4_pseudo_header_vectors": 1,
    "ipv6_pseudo_header_vectors": 2,
    "carry_discipline_vectors": 4,
    "kunit_random_prefix_vectors": 6,
}

EXPECTED_HEXDUMP_DETERMINISM = {
    "parity_vectors": 10,
    "overflow_vectors": 4,
    "required_length_vectors": 9,
    "perf_vectors": 4,
    "normalization_helpers": [
        "normalizedRowsize",
        "normalizedGroupsizeForLen",
        "prepareExpectedLine",
    ],
}

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
        "Documentation/zigux/phase6-helper-parity-catalog.md",
        "Documentation/zigux/phase6-perf-gate-survey.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "zigux/tests/phase6_helper_parity_manifest.json",
    ],
    "perf_posture": {
        "relative_slowdown_helpers": [
            "base64",
            "checksum",
            "hexdump",
        ],
        "comparison_budget_helpers": [
            "bsearch",
        ],
        "timing_sanity_only_helpers": [],
    },
    "fixture_posture": {
        "fixture_backed_helpers": [
            "base64",
            "checksum",
            "hexdump",
        ],
        "inline_corpus_helpers": [
            "bsearch",
        ],
    },
    "determinism_evidence": {
        "base64": {
            "standard_encode_vectors": 22,
            "variant_encode_vectors": 18,
            "standard_decode_vectors": 22,
            "variant_decode_vectors": 12,
            "invalid_decode_vectors": 22,
            "c_parity_self_test_cases": 8,
            "c_parity_cases": 96,
        },
        "bsearch": {
            "inline_corpus": "sorted integer and symbol tables",
            "c_parity_self_test_cases": 6,
            "c_parity_cases": 29,
        },
        "checksum": {
            "compute_vectors": 5,
            "composition_vectors": 2,
            "seeded_vectors": 3,
            "ipv4_pseudo_header_vectors": 1,
            "ipv6_pseudo_header_vectors": 2,
            "carry_discipline_vectors": 4,
            "kunit_random_prefix_vectors": 6,
        },
        "hexdump": {
            "parity_vectors": 10,
            "overflow_vectors": 4,
            "required_length_vectors": 9,
            "perf_vectors": 4,
            "normalization_helpers": [
                "normalizedRowsize",
                "normalizedGroupsizeForLen",
                "prepareExpectedLine",
            ],
        },
        "generated_fixture_artifacts_committed": False,
    },
    "exact_checks": [
        "python3 scripts/zigux/validate-phase6.py --self-test",
        "python3 scripts/zigux/validate-phase6.py",
        "make -C zigux phase6-validate",
        "make -C zigux phase6",
        "make -C zigux phase6-base64-perf",
        "make -C zigux phase6-bsearch-perf",
        "make -C zigux phase6-checksum-perf",
        "make -C zigux phase6-hexdump-perf",
        "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
        "python3 scripts/zigux/check-phase6-base64-c-parity.py",
        "python3 scripts/zigux/check-phase6-bsearch-c-parity.py --self-test",
        "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
    ],
}

MARKER_FILE_CONTENTS = {
    "zigux/Makefile": MAKE_MARKERS,
    ".github/workflows/zigux-bootstrap.yml": WORKFLOW_MARKERS,
    "scripts/zigux/README.md": SCRIPT_README_MARKERS,
    "zigux/tests/README.md": TESTS_README_MARKERS,
    "Documentation/zigux/README.md": DOC_README_MARKERS,
    "Documentation/zigux/phase6-perf-gate-survey.md": PERF_SURVEY_MARKERS,
    "zigux/tests/phase6_build.zig": PHASE6_BUILD_MARKERS,
    "lib/base64.zig": BASE64_HELPER_MARKERS,
    "lib/bsearch.zig": BSEARCH_HELPER_MARKERS,
    "lib/checksum.zig": CHECKSUM_HELPER_MARKERS,
    "lib/hexdump.zig": HEXDUMP_HELPER_MARKERS,
    "zigux/tests/phase6_base64.zig": BASE64_TEST_MARKERS,
    "zigux/tests/phase6_base64_perf.zig": BASE64_PERF_MARKERS,
    "scripts/zigux/check-phase6-base64-c-parity.py": BASE64_PARITY_SCRIPT_MARKERS,
    "zigux/tests/phase6_base64_c_parity.zig": BASE64_C_PARITY_RUNNER_MARKERS,
    "zigux/tests/phase6_base64_c_casegen.zig": BASE64_CASEGEN_MARKERS,
    "zigux/tests/fixtures/phase6_base64_c_harness.c": BASE64_C_HARNESS_MARKERS,
    "zigux/tests/fixtures/phase6_base64_vectors.zig": BASE64_VECTORS_MARKERS,
    "Documentation/zigux/phase6-base64-slice.md": BASE64_SLICE_MARKERS,
    "zigux/tests/phase6_bsearch.zig": BSEARCH_TEST_MARKERS,
    "zigux/tests/phase6_bsearch_perf.zig": BSEARCH_PERF_MARKERS,
    "scripts/zigux/check-phase6-bsearch-c-parity.py": BSEARCH_PARITY_SCRIPT_MARKERS,
    "zigux/tests/phase6_bsearch_c_parity.zig": BSEARCH_C_PARITY_RUNNER_MARKERS,
    "zigux/tests/fixtures/phase6_bsearch_c_harness.c": BSEARCH_C_HARNESS_MARKERS,
    "Documentation/zigux/phase6-bsearch-slice.md": BSEARCH_SLICE_MARKERS,
    "zigux/tests/phase6_checksum.zig": CHECKSUM_TEST_MARKERS,
    "zigux/tests/phase6_checksum_perf.zig": CHECKSUM_PERF_MARKERS,
    "zigux/tests/fixtures/phase6_checksum_vectors.zig": CHECKSUM_FIXTURE_MARKERS,
    "Documentation/zigux/phase6-checksum-slice.md": CHECKSUM_SLICE_MARKERS,
    "zigux/tests/phase6_hexdump.zig": HEXDUMP_TEST_MARKERS,
    "zigux/tests/phase6_hexdump_perf.zig": HEXDUMP_PERF_MARKERS,
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig": HEXDUMP_FIXTURE_MARKERS,
    "Documentation/zigux/phase6-hexdump-slice.md": HEXDUMP_SLICE_MARKERS,
}

def text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")

def require_markers(missing: list[str], label: str, content: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in content:
            missing.append(f"{label}:missing:{marker}")

def require_manifest_equal(missing: list[str], manifest: dict[str, object], key: str, expected: object) -> None:
    if manifest.get(key) != expected:
        missing.append(f"manifest:{key}")

def total_marker_count() -> int:
    return sum(len(markers) for markers in MARKER_FILE_CONTENTS.values()) + len(CATALOG_MARKERS)

def parse_catalog_head(content: str) -> tuple[str | None, str]:
    match = re.search(r"- verified head: `([0-9a-f]{40}|[^`]+)`", content)
    if match is None:
        return None, "missing"
    head = match.group(1)
    if not HEX40.fullmatch(head):
        return head, "invalid"
    return head, "ok"

def validate_phase6(root: Path) -> dict[str, object]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return {
            "ok": False,
            "missing_files": missing_files,
            "missing": [],
            "catalog_head": "",
            "catalog_head_status": "missing_files",
        }

    phase6_catalog = text(root, "Documentation/zigux/phase6-helper-parity-catalog.md")
    catalog_head, catalog_head_status = parse_catalog_head(phase6_catalog)
    if catalog_head_status != "ok":
        return {
            "ok": False,
            "missing_files": [],
            "missing": [],
            "catalog_head": catalog_head or "",
            "catalog_head_status": catalog_head_status,
        }

    missing: list[str] = []
    require_markers(missing, "make", text(root, "zigux/Makefile"), MAKE_MARKERS)
    require_markers(missing, "workflow", text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
    require_markers(missing, "script_readme", text(root, "scripts/zigux/README.md"), SCRIPT_README_MARKERS)
    require_markers(missing, "tests_readme", text(root, "zigux/tests/README.md"), TESTS_README_MARKERS)
    require_markers(missing, "doc_readme", text(root, "Documentation/zigux/README.md"), DOC_README_MARKERS)
    require_markers(missing, "phase6_perf_survey", text(root, "Documentation/zigux/phase6-perf-gate-survey.md"), PERF_SURVEY_MARKERS)
    require_markers(missing, "phase6_build", text(root, "zigux/tests/phase6_build.zig"), PHASE6_BUILD_MARKERS)
    require_markers(missing, "phase6_catalog", phase6_catalog, CATALOG_MARKERS)

    file_marker_specs = [
        ("base64_helper", "lib/base64.zig", BASE64_HELPER_MARKERS),
        ("bsearch_helper", "lib/bsearch.zig", BSEARCH_HELPER_MARKERS),
        ("checksum_helper", "lib/checksum.zig", CHECKSUM_HELPER_MARKERS),
        ("hexdump_helper", "lib/hexdump.zig", HEXDUMP_HELPER_MARKERS),
        ("phase6_base64", "zigux/tests/phase6_base64.zig", BASE64_TEST_MARKERS),
        ("phase6_base64_perf", "zigux/tests/phase6_base64_perf.zig", BASE64_PERF_MARKERS),
        ("phase6_base64_c_parity_script", "scripts/zigux/check-phase6-base64-c-parity.py", BASE64_PARITY_SCRIPT_MARKERS),
        ("phase6_base64_c_parity_runner", "zigux/tests/phase6_base64_c_parity.zig", BASE64_C_PARITY_RUNNER_MARKERS),
        ("phase6_base64_c_casegen", "zigux/tests/phase6_base64_c_casegen.zig", BASE64_CASEGEN_MARKERS),
        ("phase6_base64_c_harness", "zigux/tests/fixtures/phase6_base64_c_harness.c", BASE64_C_HARNESS_MARKERS),
        ("phase6_base64_vectors", "zigux/tests/fixtures/phase6_base64_vectors.zig", BASE64_VECTORS_MARKERS),
        ("phase6_base64_slice", "Documentation/zigux/phase6-base64-slice.md", BASE64_SLICE_MARKERS),
        ("phase6_bsearch", "zigux/tests/phase6_bsearch.zig", BSEARCH_TEST_MARKERS),
        ("phase6_bsearch_perf", "zigux/tests/phase6_bsearch_perf.zig", BSEARCH_PERF_MARKERS),
        ("phase6_bsearch_c_parity_script", "scripts/zigux/check-phase6-bsearch-c-parity.py", BSEARCH_PARITY_SCRIPT_MARKERS),
        ("phase6_bsearch_c_parity_runner", "zigux/tests/phase6_bsearch_c_parity.zig", BSEARCH_C_PARITY_RUNNER_MARKERS),
        ("phase6_bsearch_c_harness", "zigux/tests/fixtures/phase6_bsearch_c_harness.c", BSEARCH_C_HARNESS_MARKERS),
        ("phase6_bsearch_slice", "Documentation/zigux/phase6-bsearch-slice.md", BSEARCH_SLICE_MARKERS),
        ("phase6_checksum", "zigux/tests/phase6_checksum.zig", CHECKSUM_TEST_MARKERS),
        ("phase6_checksum_perf", "zigux/tests/phase6_checksum_perf.zig", CHECKSUM_PERF_MARKERS),
        ("phase6_checksum_vectors", "zigux/tests/fixtures/phase6_checksum_vectors.zig", CHECKSUM_FIXTURE_MARKERS),
        ("phase6_checksum_slice", "Documentation/zigux/phase6-checksum-slice.md", CHECKSUM_SLICE_MARKERS),
        ("phase6_hexdump", "zigux/tests/phase6_hexdump.zig", HEXDUMP_TEST_MARKERS),
        ("phase6_hexdump_perf", "zigux/tests/phase6_hexdump_perf.zig", HEXDUMP_PERF_MARKERS),
        ("phase6_hexdump_vectors", "zigux/tests/fixtures/phase6_hexdump_vectors.zig", HEXDUMP_FIXTURE_MARKERS),
        ("phase6_hexdump_slice", "Documentation/zigux/phase6-hexdump-slice.md", HEXDUMP_SLICE_MARKERS),
    ]
    for label, path, markers in file_marker_specs:
        require_markers(missing, label, text(root, path), markers)

    manifest = json.loads(text(root, "zigux/tests/phase6_helper_parity_manifest.json"))
    if not isinstance(manifest, dict):
        missing.append("manifest:root")
    else:
        surveyed_commit = manifest.get("surveyed_commit")
        if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
            missing.append("manifest:surveyed_commit")
        elif surveyed_commit != catalog_head:
            missing.append("manifest:surveyed_commit_mismatch")

        for key, expected in EXPECTED_MANIFEST.items():
            require_manifest_equal(missing, manifest, key, expected)

        determinism_evidence = manifest.get("determinism_evidence")
        if not isinstance(determinism_evidence, dict):
            missing.append("manifest:determinism_evidence")
        else:
            if determinism_evidence.get("base64") != EXPECTED_BASE64_DETERMINISM:
                missing.append("manifest:determinism_evidence:base64")
            if determinism_evidence.get("bsearch") != EXPECTED_BSEARCH_DETERMINISM:
                missing.append("manifest:determinism_evidence:bsearch")
            if determinism_evidence.get("checksum") != EXPECTED_CHECKSUM_DETERMINISM:
                missing.append("manifest:determinism_evidence:checksum")
            if determinism_evidence.get("hexdump") != EXPECTED_HEXDUMP_DETERMINISM:
                missing.append("manifest:determinism_evidence:hexdump")
            if determinism_evidence.get("generated_fixture_artifacts_committed") is not False:
                missing.append("manifest:determinism_evidence:generated_fixture_artifacts_committed")

    return {
        "ok": not missing,
        "missing_files": [],
        "missing": missing,
        "catalog_head": catalog_head,
        "catalog_head_status": "ok",
    }

def report_validation(result: dict[str, object]) -> int:
    missing_files = result["missing_files"]
    if missing_files:
        print("PHASE6_VALIDATION=fail")
        print("MISSING_PHASE6_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE6_FILES_END")
        return 1

    catalog_head_status = result["catalog_head_status"]
    if catalog_head_status != "ok":
        print("PHASE6_VALIDATION=fail")
        print(f"PHASE6_CATALOG_HEAD_STATUS={catalog_head_status}")
        return 1

    missing = result["missing"]
    if missing:
        print("PHASE6_VALIDATION=fail")
        print("PHASE6_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE6_MISSING_END")
        return 1

    print("PHASE6_VALIDATION=pass")
    print(f"PHASE6_REQUIRED_MARKER_COUNT={total_marker_count()}")
    print(f"PHASE6_CATALOG_VERIFIED_HEAD={result['catalog_head']}")
    return 0

def write_file(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def render_marker_file(markers: list[str]) -> str:
    return "\n".join(markers) + "\n"

def write_self_test_tree(root: Path) -> None:
    for path in REQUIRED_FILES:
        write_file(root, path, "placeholder\n")

    for path, markers in MARKER_FILE_CONTENTS.items():
        write_file(root, path, render_marker_file(markers))

    catalog_markers = [f"- verified head: `{SELF_TEST_HEAD}`"]
    catalog_markers.extend(marker for marker in CATALOG_MARKERS if marker != "- verified head: `")
    write_file(
        root,
        "Documentation/zigux/phase6-helper-parity-catalog.md",
        render_marker_file(catalog_markers),
    )

    manifest = dict(EXPECTED_MANIFEST)
    manifest["surveyed_commit"] = SELF_TEST_HEAD
    manifest["determinism_evidence"] = {
        "base64": dict(EXPECTED_BASE64_DETERMINISM),
        "bsearch": dict(EXPECTED_BSEARCH_DETERMINISM),
        "checksum": dict(EXPECTED_CHECKSUM_DETERMINISM),
        "hexdump": {
            "parity_vectors": EXPECTED_HEXDUMP_DETERMINISM["parity_vectors"],
            "overflow_vectors": EXPECTED_HEXDUMP_DETERMINISM["overflow_vectors"],
            "required_length_vectors": EXPECTED_HEXDUMP_DETERMINISM["required_length_vectors"],
            "perf_vectors": EXPECTED_HEXDUMP_DETERMINISM["perf_vectors"],
            "normalization_helpers": list(EXPECTED_HEXDUMP_DETERMINISM["normalization_helpers"]),
        },
        "generated_fixture_artifacts_committed": False,
    }
    write_file(
        root,
        "zigux/tests/phase6_helper_parity_manifest.json",
        json.dumps(manifest, indent=2) + "\n",
    )

def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            write_self_test_tree(root)
            pass_result = validate_phase6(root)
            if not pass_result["ok"]:
                raise AssertionError(f"positive case failed: {pass_result}")

            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["surveyed_commit"] = SELF_TEST_MUTATED_HEAD
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            fail_result = validate_phase6(root)
            if fail_result["ok"] or "manifest:surveyed_commit_mismatch" not in fail_result["missing"]:
                raise AssertionError(f"expected surveyed_commit mismatch, got: {fail_result}")

            write_self_test_tree(root)
            perf_path = root / "Documentation/zigux/phase6-perf-gate-survey.md"
            perf_text = perf_path.read_text(encoding="utf-8")
            perf_marker = "max_slowdown_pct = 600"
            perf_path.write_text(perf_text.replace(perf_marker, "", 1), encoding="utf-8")
            perf_fail_result = validate_phase6(root)
            if perf_fail_result["ok"] or f"phase6_perf_survey:missing:{perf_marker}" not in perf_fail_result["missing"]:
                raise AssertionError(f"expected perf survey drift failure, got: {perf_fail_result}")

            write_self_test_tree(root)
            script_readme_path = root / "scripts/zigux/README.md"
            script_readme_text = script_readme_path.read_text(encoding="utf-8")
            script_readme_path.write_text(
                script_readme_text.replace("Phase 6 flow", "Phase Six flow", 1),
                encoding="utf-8",
            )
            readme_fail_result = validate_phase6(root)
            if readme_fail_result["ok"] or "script_readme:missing:Phase 6 flow" not in readme_fail_result["missing"]:
                raise AssertionError(f"expected script README drift failure, got: {readme_fail_result}")

            write_self_test_tree(root)
            catalog_path = root / "Documentation/zigux/phase6-helper-parity-catalog.md"
            catalog_text = catalog_path.read_text(encoding="utf-8")
            catalog_marker = "PHASE6_BSEARCH_C_PARITY_CASES=29"
            catalog_path.write_text(
                catalog_text.replace(catalog_marker, "", 1),
                encoding="utf-8",
            )
            catalog_fail_result = validate_phase6(root)
            if catalog_fail_result["ok"] or f"phase6_catalog:missing:{catalog_marker}" not in catalog_fail_result["missing"]:
                raise AssertionError(f"expected catalog drift failure, got: {catalog_fail_result}")

            write_self_test_tree(root)
            catalog_path = root / "Documentation/zigux/phase6-helper-parity-catalog.md"
            catalog_text = catalog_path.read_text(encoding="utf-8")
            validator_count_marker = "PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=13"
            catalog_path.write_text(
                catalog_text.replace(validator_count_marker, "", 1),
                encoding="utf-8",
            )
            validator_count_fail_result = validate_phase6(root)
            if validator_count_fail_result["ok"] or f"phase6_catalog:missing:{validator_count_marker}" not in validator_count_fail_result["missing"]:
                raise AssertionError(
                    f"expected catalog validator-count drift failure, got: {validator_count_fail_result}"
                )

            write_self_test_tree(root)
            helper_path = root / "lib/checksum.zig"
            helper_text = helper_path.read_text(encoding="utf-8")
            helper_marker = "pub fn tcpUdpV6Nofold(sum: u32, saddr: [16]u8, daddr: [16]u8, len: u32, proto: u8) u32 {"
            helper_path.write_text(
                helper_text.replace(helper_marker, "", 1),
                encoding="utf-8",
            )
            helper_fail_result = validate_phase6(root)
            if helper_fail_result["ok"] or f"checksum_helper:missing:{helper_marker}" not in helper_fail_result["missing"]:
                raise AssertionError(f"expected checksum helper drift failure, got: {helper_fail_result}")

            write_self_test_tree(root)
            catalog_path = root / "Documentation/zigux/phase6-helper-parity-catalog.md"
            catalog_text = catalog_path.read_text(encoding="utf-8")
            verified_head_line = f"- verified head: `{SELF_TEST_HEAD}`"
            catalog_path.write_text(
                catalog_text.replace(verified_head_line, "- verified tip: `missing-head-marker`", 1),
                encoding="utf-8",
            )
            missing_head_result = validate_phase6(root)
            if missing_head_result["ok"] or missing_head_result["catalog_head_status"] != "missing":
                raise AssertionError(f"expected missing catalog head failure, got: {missing_head_result}")

            write_self_test_tree(root)
            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            shared_gates = manifest.get("shared_gates")
            if not isinstance(shared_gates, list):
                raise AssertionError(f"expected shared_gates list, got: {shared_gates!r}")
            dropped_gate = "Documentation/zigux/phase6-perf-gate-survey.md"
            manifest["shared_gates"] = [gate for gate in shared_gates if gate != dropped_gate]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            manifest_fail_result = validate_phase6(root)
            if manifest_fail_result["ok"] or "manifest:shared_gates" not in manifest_fail_result["missing"]:
                raise AssertionError(f"expected shared_gates drift failure, got: {manifest_fail_result}")

            write_self_test_tree(root)
            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["determinism_evidence"]["base64"]["c_parity_cases"] = 95
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            base64_determinism_fail_result = validate_phase6(root)
            if base64_determinism_fail_result["ok"] or "manifest:determinism_evidence:base64" not in base64_determinism_fail_result["missing"]:
                raise AssertionError(f"expected base64 determinism drift failure, got: {base64_determinism_fail_result}")

            write_self_test_tree(root)
            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["determinism_evidence"]["bsearch"]["c_parity_cases"] = 28
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            bsearch_determinism_fail_result = validate_phase6(root)
            if bsearch_determinism_fail_result["ok"] or "manifest:determinism_evidence:bsearch" not in bsearch_determinism_fail_result["missing"]:
                raise AssertionError(f"expected bsearch determinism drift failure, got: {bsearch_determinism_fail_result}")

            write_self_test_tree(root)
            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            checksum_evidence = manifest["determinism_evidence"]["checksum"]
            checksum_evidence["kunit_random_prefix_vectors"] = 5
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            determinism_fail_result = validate_phase6(root)
            if determinism_fail_result["ok"] or "manifest:determinism_evidence:checksum" not in determinism_fail_result["missing"]:
                raise AssertionError(f"expected checksum determinism drift failure, got: {determinism_fail_result}")

            write_self_test_tree(root)
            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["determinism_evidence"]["hexdump"]["perf_vectors"] = 3
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            hexdump_determinism_fail_result = validate_phase6(root)
            if hexdump_determinism_fail_result["ok"] or "manifest:determinism_evidence:hexdump" not in hexdump_determinism_fail_result["missing"]:
                raise AssertionError(f"expected hexdump determinism drift failure, got: {hexdump_determinism_fail_result}")

            write_self_test_tree(root)
            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["determinism_evidence"]["generated_fixture_artifacts_committed"] = True
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            generated_fixture_flag_fail_result = validate_phase6(root)
            if generated_fixture_flag_fail_result["ok"] or "manifest:determinism_evidence:generated_fixture_artifacts_committed" not in generated_fixture_flag_fail_result["missing"]:
                raise AssertionError(
                    f"expected generated fixture flag drift failure, got: {generated_fixture_flag_fail_result}"
                )

    except AssertionError as exc:
        print("PHASE6_VALIDATOR_SELF_TEST=fail")
        print(f"PHASE6_VALIDATOR_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_VALIDATOR_SELF_TEST=pass")
    print("PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=13")
    return 0

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 6 leaf-helper packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator checks")
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    return report_validation(validate_phase6(ROOT))

if __name__ == "__main__":
    sys.exit(main())
