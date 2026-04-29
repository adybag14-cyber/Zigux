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
phase6_base64_perf = (ROOT / "zigux" / "tests" / "phase6_base64_perf.zig").read_text(encoding="utf-8")

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
require_markers("phase6_base64_perf", phase6_base64_perf, required_phase6_base64_perf_markers, issues)

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
