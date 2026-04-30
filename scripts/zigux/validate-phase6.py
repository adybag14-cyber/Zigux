#!/usr/bin/env python3
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase6.py",
    ROOT / "scripts" / "zigux" / "check-phase6-base64-c-parity.py",
    ROOT / "scripts" / "zigux" / "check-phase6-bsearch-c-parity.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "phase6-helper-parity-catalog.md",
    ROOT / "Documentation" / "zigux" / "phase6-base64-slice.md",
    ROOT / "Documentation" / "zigux" / "phase6-bsearch-slice.md",
    ROOT / "Documentation" / "zigux" / "phase6-checksum-slice.md",
    ROOT / "Documentation" / "zigux" / "phase6-hexdump-slice.md",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase6_base64.zig",
    ROOT / "zigux" / "tests" / "phase6_base64_perf.zig",
    ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig",
    ROOT / "zigux" / "tests" / "phase6_base64_c_casegen.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_harness.c",
    ROOT / "zigux" / "tests" / "phase6_bsearch.zig",
    ROOT / "zigux" / "tests" / "phase6_bsearch_perf.zig",
    ROOT / "zigux" / "tests" / "phase6_bsearch_c_parity.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase6_bsearch_c_harness.c",
    ROOT / "zigux" / "tests" / "phase6_checksum.zig",
    ROOT / "zigux" / "tests" / "phase6_checksum_perf.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase6_checksum_vectors.zig",
    ROOT / "zigux" / "tests" / "phase6_hexdump.zig",
    ROOT / "zigux" / "tests" / "phase6_hexdump_perf.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase6_hexdump_vectors.zig",
    ROOT / "zigux" / "tests" / "phase6_helper_parity_manifest.json",
    ROOT / "zigux" / "tests" / "phase6_build.zig",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE6_VALIDATION=fail")
    print("MISSING_PHASE6_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE6_FILES_END")
    sys.exit(1)

makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
phase6_catalog = (ROOT / "Documentation" / "zigux" / "phase6-helper-parity-catalog.md").read_text(encoding="utf-8")
phase6_manifest = json.loads((ROOT / "zigux" / "tests" / "phase6_helper_parity_manifest.json").read_text(encoding="utf-8"))
phase6_build = (ROOT / "zigux" / "tests" / "phase6_build.zig").read_text(encoding="utf-8")
phase6_base64 = (ROOT / "zigux" / "tests" / "phase6_base64.zig").read_text(encoding="utf-8")
phase6_base64_c_parity = (ROOT / "zigux" / "tests" / "phase6_base64_c_parity.zig").read_text(encoding="utf-8")
phase6_base64_c_casegen = (ROOT / "zigux" / "tests" / "phase6_base64_c_casegen.zig").read_text(encoding="utf-8")
phase6_base64_slice = (ROOT / "Documentation" / "zigux" / "phase6-base64-slice.md").read_text(encoding="utf-8")
phase6_base64_perf = (ROOT / "zigux" / "tests" / "phase6_base64_perf.zig").read_text(encoding="utf-8")
phase6_bsearch = (ROOT / "zigux" / "tests" / "phase6_bsearch.zig").read_text(encoding="utf-8")
phase6_bsearch_perf = (ROOT / "zigux" / "tests" / "phase6_bsearch_perf.zig").read_text(encoding="utf-8")
phase6_bsearch_c_parity = (ROOT / "zigux" / "tests" / "phase6_bsearch_c_parity.zig").read_text(encoding="utf-8")
phase6_bsearch_slice = (ROOT / "Documentation" / "zigux" / "phase6-bsearch-slice.md").read_text(encoding="utf-8")
phase6_checksum_perf = (ROOT / "zigux" / "tests" / "phase6_checksum_perf.zig").read_text(encoding="utf-8")
phase6_checksum_vectors = (ROOT / "zigux" / "tests" / "fixtures" / "phase6_checksum_vectors.zig").read_text(encoding="utf-8")
phase6_checksum_slice = (ROOT / "Documentation" / "zigux" / "phase6-checksum-slice.md").read_text(encoding="utf-8")

phase6_catalog_verified_head_match = re.search(r"- verified head: `([0-9a-f]{40})`", phase6_catalog)
if phase6_catalog_verified_head_match is None:
    print("PHASE6_VALIDATION=fail")
    print("PHASE6_CATALOG_HEAD_STATUS=missing")
    sys.exit(1)
phase6_catalog_verified_head = phase6_catalog_verified_head_match.group(1)

required_make_markers = [
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

required_workflow_markers = [
    "Validate Phase 6 leaf helper gates",
    "make -C zigux phase6-validate",
    "Run Phase 6 leaf helper tests",
    "zig build test --build-file zigux/tests/phase6_build.zig --summary all",
]

required_script_readme_markers = [
    "validate-phase6.py",
    "check-phase6-base64-c-parity.py",
    "check-phase6-bsearch-c-parity.py",
    "Phase 6 flow",
    "make -C zigux phase6-validate",
    "make -C zigux phase6",
    "per-helper perf targets",
]

required_tests_readme_markers = [
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

required_doc_readme_markers = [
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

required_phase6_build_markers = [
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

required_phase6_base64_perf_markers = [
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

required_phase6_base64_markers = [
    'test "phase 6 base64 exact-fit buffers work across fixture vectors" {',
    'test "phase 6 base64 decode rejects invalid kernel-style vectors" {',
    'base64.DecodeError.InvalidInput',
    'base64.DecodeError.DestinationTooSmall',
    "for (fixtures.variant_decode_cases) |case| {",
]

required_phase6_base64_c_parity_markers = [
    'try writer.print("enc\\tstd\\t{}\\t", .{@intFromBool(case.padding)});',
    'try writer.print("dec\\tstd\\t{}\\t{}\\t", .{ @intFromBool(case.padding), exact_len });',
    'try writer.print("inv\\t{s}\\t{}\\t", .{ case.variant_name, @intFromBool(case.padding) });',
    'try writer.print("\\t{s}\\t{s}\\n", .{ errorName(bytes_result), errorName(decode_result) });',
]

required_phase6_base64_c_casegen_markers = [
    "Generated from zigux/tests/fixtures/phase6_base64_vectors.zig.",
    "static const struct encode_case encode_cases[] = {",
    "static const struct decode_case decode_cases[] = {",
    "static const struct invalid_case invalid_cases[] = {",
    'variantEnum(case.variant_name)',
]

required_phase6_base64_slice_markers = [
    "exact-fit encode and decode buffers across the shared standard and variant fixture surface, plus one-byte-short rejection before writes",
    "regenerates the committed C include payload through `zigux/tests/phase6_base64_c_casegen.zig`",
    "invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs",
    "exhaustive reverse-map classification across all 256 byte values for the standard, URL-safe, and IMAP decode variants",
]

required_phase6_bsearch_markers = [
    'test "phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection" {',
    'test "phase 6 bsearch accepts runtime-selected comparator function pointers" {',
    'test "phase 6 bsearch accepts runtime-selected C ABI comparator pointers" {',
    "try std.testing.expect(counted_compare_calls <= 4);",
]

required_phase6_bsearch_perf_markers = [
    "ns_per_lookup={} avg_compare_calls={d:.2} max_compare_calls={} max_compare_budget={}",
    "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
    "try std.testing.expect(compare_calls <= max_compare_budget);",
    "seedDeterministicQueries(case.len, values, &queries, &expected_hits);",
]

required_phase6_bsearch_c_parity_markers = [
    'try writeDuplicateCase(writer, "duplicate-hit-begin", 7, bsearch.searchIndex(u32, u32, &@as(u32, 7), duplicate_at_beginning[0..], compareU32));',
    'try writeIndexCase(writer, "descending-hit", 34, bsearch.searchIndex(u32, u32, &@as(u32, 34), descending_values[0..], compareDescendingU32));',
    'try writer.print("sym-hit\\tkmalloc\\t0x{x}\\n", .{item.address});',
    'try writer.print("mutable-hit\\t21\\t{}\\n", .{mutable_values[3]});',
]

required_phase6_bsearch_slice_markers = [
    "duplicate-key found-or-null parity without claiming stable selection across beginning, middle, and end duplicate runs",
    "runtime-selected comparator function pointers preserve the same found-or-null behavior across ascending and descending sorted slices",
    "runtime-selected C ABI comparator pointers preserve the same found-or-null behavior across ascending and descending sorted slices",
    "representative lookup work stays inside a bounded binary-search comparison budget on every replayed lookup",
    "a representative external C-vs-Zig parity replay currently replays 17 sorted lookup cases",
]

required_phase6_checksum_perf_markers = [
    "fn referencePartial(bytes: []const u8, seed: u32) u32",
    "var slowdown_samples: [3]u64 = undefined;",
    "const slowdown_pct = median3(",
    "helper_ns_per_byte={d:.2}",
    "reference_ns_per_byte={d:.2}",
    "try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);",
]

required_phase6_checksum_vector_markers = [
    '.{ .label = "64", .len = 64, .reps = 20_000, .seed = 0, .max_slowdown_pct = 150 },',
    '.{ .label = "1501", .len = 1501, .reps = 4_000, .seed = 0x1234_5678, .max_slowdown_pct = 150 },',
]

required_phase6_checksum_slice_markers = [
    "replay the checksum perf sanity harness when reviewing checksum-cost drift",
    "deterministic 64-byte and 1501-byte payloads",
    "`referencePartial` path",
    "representative checksum cost per call and per byte",
]


def require_markers(label: str, text: str, markers: list[str], issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing:{marker}")


issues: list[str] = []
require_markers("makefile", makefile, required_make_markers, issues)
require_markers("workflow", workflow, required_workflow_markers, issues)
require_markers("script_readme", script_readme, required_script_readme_markers, issues)
require_markers("tests_readme", tests_readme, required_tests_readme_markers, issues)
require_markers("doc_readme", doc_readme, required_doc_readme_markers, issues)
require_markers("phase6_build", phase6_build, required_phase6_build_markers, issues)
require_markers("phase6_base64", phase6_base64, required_phase6_base64_markers, issues)
require_markers("phase6_base64_c_parity", phase6_base64_c_parity, required_phase6_base64_c_parity_markers, issues)
require_markers("phase6_base64_c_casegen", phase6_base64_c_casegen, required_phase6_base64_c_casegen_markers, issues)
require_markers("phase6_base64_slice", phase6_base64_slice, required_phase6_base64_slice_markers, issues)
require_markers("phase6_base64_perf", phase6_base64_perf, required_phase6_base64_perf_markers, issues)
require_markers("phase6_bsearch", phase6_bsearch, required_phase6_bsearch_markers, issues)
require_markers("phase6_bsearch_perf", phase6_bsearch_perf, required_phase6_bsearch_perf_markers, issues)
require_markers("phase6_bsearch_c_parity", phase6_bsearch_c_parity, required_phase6_bsearch_c_parity_markers, issues)
require_markers("phase6_bsearch_slice", phase6_bsearch_slice, required_phase6_bsearch_slice_markers, issues)
require_markers("phase6_checksum_perf", phase6_checksum_perf, required_phase6_checksum_perf_markers, issues)
require_markers("phase6_checksum_vectors", phase6_checksum_vectors, required_phase6_checksum_vector_markers, issues)
require_markers("phase6_checksum_slice", phase6_checksum_slice, required_phase6_checksum_slice_markers, issues)

if phase6_manifest.get("phase") != "Phase 6":
    issues.append("manifest:phase")
if phase6_manifest.get("status") != "active":
    issues.append("manifest:status")
if phase6_manifest.get("surveyed_commit") != phase6_catalog_verified_head:
    issues.append("manifest:surveyed_commit_mismatch")
if phase6_manifest.get("perf_posture", {}).get("relative_slowdown_helpers") != ["base64", "checksum", "hexdump"]:
    issues.append("manifest:relative_slowdown_helpers")
if phase6_manifest.get("perf_posture", {}).get("comparison_budget_helpers") != ["bsearch"]:
    issues.append("manifest:comparison_budget_helpers")

helper_ids = [helper.get("id") for helper in phase6_manifest.get("helpers", [])]
if helper_ids != ["base64", "bsearch", "checksum", "hexdump"]:
    issues.append("manifest:helper_ids")

if "median-of-three slowdown percentages" not in phase6_catalog:
    issues.append("catalog:base64_median_posture")
if "median-of-three slowdown sample" not in (ROOT / "Documentation" / "zigux" / "phase6-base64-slice.md").read_text(encoding="utf-8"):
    issues.append("base64_slice:median_posture")
if "PHASE6_BASE64_C_PARITY_CASES=90" not in phase6_catalog:
    issues.append("catalog:base64_case_count")
if "PHASE6_BSEARCH_C_PARITY_CASES=17" not in phase6_catalog:
    issues.append("catalog:bsearch_case_count")

if issues:
    print("PHASE6_VALIDATION=fail")
    print("PHASE6_VALIDATION_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE6_VALIDATION_ISSUES_END")
    sys.exit(1)

print("PHASE6_VALIDATION=pass")
print(f"PHASE6_CATALOG_VERIFIED_HEAD={phase6_catalog_verified_head}")