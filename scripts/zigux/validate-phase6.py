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

EXPECTED_SHARED_GATES = [
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
]

REQUIRED_FILES = [
    *EXPECTED_SHARED_GATES,
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-bsearch-c-parity.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "Documentation/zigux/phase6-base64-slice.md",
    "Documentation/zigux/phase6-bsearch-slice.md",
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_perf.zig",
    "zigux/tests/phase6_bsearch_c_parity.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "zigux/tests/fixtures/phase6_bsearch_c_harness.c",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
]

MAKE_MARKERS = [
    "PHONY += phase6-validate phase6-test phase6-perf phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-perf phase6",
    "phase6-perf:",
    "perf --build-file zigux/tests/phase6_build.zig",
]

CATALOG_MARKERS = [
    "PHASE6_BASE64_C_PARITY_CASES=112",
    "PHASE6_BSEARCH_C_PARITY_CASES=29",
    "PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=10",
    "PHASE6_CHECKSUM_C_PARITY_CASES=22",
    "max_encode_slowdown_pct = 190",
    "max_decode_slowdown_pct = 320",
    "max_slowdown_pct = 150",
    "max_slowdown_pct = 175",
    "max_slowdown_pct = 550",
    "max_slowdown_pct = 600",
    "avg_compare_calls <= std.math.log2_int_ceil(len) + 1",
    "PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=23",
]

PERF_SURVEY_MARKERS = [
    "max_encode_slowdown_pct = 190",
    "max_decode_slowdown_pct = 320",
    "std.math.log2_int_ceil(len) + 1",
    "max_slowdown_pct = 150",
    "max_slowdown_pct = 175",
    "max_slowdown_pct = 550",
    "max_slowdown_pct = 600",
]

HEXDUMP_SLICE_MARKERS = [
    "a replayable perf-sanity harness reports representative dump cost per call and per byte for plain, grouped, and ASCII formatter paths through the shared `zigux/tests/fixtures/phase6_hexdump_vectors.zig` perf-case table, including the native-endian 4-byte and 8-byte grouped ASCII branches",
    "the same perf harness now measures helper output against the committed `fixtures.prepareExpectedLine(...)` reference path, keeping `16B-plain` at `max_slowdown_pct = 175` while the grouped ASCII `32B-ascii-g2` and `16B-ascii-g4` replays use `max_slowdown_pct = 550` and the wider native-endian `16B-ascii-g8` replay uses `max_slowdown_pct = 600`",
]

SCRIPTS_README_MARKERS = [
    "validate-phase6.py keeps the shipped Phase 6 leaf-helper packet aligned across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the four helper-local slice notes before any shared replay claims stay green.",
    "`validate-phase6.py --self-test` exercises the shared Phase 6 marker walk in a compact synthetic tree and fails if catalog-head provenance, script-README wording, perf-survey markers, shared-gates inventory, manifest `surveyed_commit`, or helper-local determinism evidence drifts.",
]

DOCS_ROOT_MARKERS = [
    "`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, and `Documentation/zigux/phase6-helper-parity-catalog.md` are the current shared notes for the bounded `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig` leaf-helper packet.",
    "`python3 scripts/zigux/validate-phase6.py`, `make -C zigux phase6-validate`, and `make -C zigux phase6` are the published validator-first shared replay path for the current Phase 6 helper tranche.",
]

TESTS_README_MARKERS = [
    "- `zigux/tests/phase6_build.zig`",
    "- `zigux/tests/phase6_checksum_c_parity.zig`",
    "- `zigux/tests/fixtures/phase6_checksum_c_harness.c`",
    "- `zigux/tests/phase6_helper_parity_manifest.json`",
    "- `scripts/zigux/validate-phase6.py`",
    "refresh `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json` whenever the shipped Phase 6 helper inventory, perf entrypoints, fixtures, or shared slice notes change",
]

WORKFLOW_MARKERS = [
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
]

PHASE6_BUILD_MARKERS = [
    '.name = "phase6-base64-tests"',
    '.name = "phase6-bsearch-tests"',
    '.name = "phase6-checksum-tests"',
    '.name = "phase6-hexdump-tests"',
    'const perf_step = b.step("perf", "Run the Phase 6 leaf helper performance sanity harnesses");',
]

BASE64_PERF_MARKERS = [
    "max_encode_slowdown_pct = 190",
    "max_decode_slowdown_pct = 320",
]

BSEARCH_PERF_MARKERS = [
    "avg_compare_calls={d:.2}",
    "max_compare_calls={}",
    "max_compare_budget={}",
    "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
]

CHECKSUM_PERF_MARKERS = [
    "try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);",
]

HEXDUMP_PERF_MARKERS = [
    "try std.testing.expect(slowdown_pct <= case.max_slowdown_pct);",
]

CHECKSUM_FIXTURE_MARKERS = [
    '.max_slowdown_pct = 150',
]

HEXDUMP_FIXTURE_MARKERS = [
    '.{ .label = "16B-plain", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175 },',
    '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550 },',
    '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550 },',
    '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 },',
]

CHECKSUM_PARITY_SCRIPT_MARKERS = [
    'print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST=pass")',
    'print("PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=10")',
    'print(f"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}")',
]

CHECKSUM_PARITY_RUNNER_MARKERS = [
    'try writer.print("compute\\t{s}\\t0x{x:0>4}\\n", .{ case.name, checksum.compute(case.bytes) });',
    'try writer.print("partial\\t{s}\\t0x{x:0>8}\\n", .{ case.name, checksum.partial(case.bytes, case.seed) });',
    'try writer.print("replace4\\tipv4-saddr\\t0x{x:0>4}\\n", .{checksum.replace4(checksum_before_addr_change, old_saddr, new_saddr)});',
]

CHECKSUM_PARITY_HARNESS_MARKERS = [
    'print_u16_case("compute", "empty", compute_bytes(empty, 0));',
    'print_u32_case("tcpudp-nofold", "udp pseudo header",',
    'print_u16_case("replace4", "ipv4-saddr", replaced4);',
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
    "shared_gates": EXPECTED_SHARED_GATES,
    "perf_posture": {
        "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
        "comparison_budget_helpers": ["bsearch"],
        "timing_sanity_only_helpers": [],
    },
    "fixture_posture": {
        "fixture_backed_helpers": ["base64", "checksum", "hexdump"],
        "inline_corpus_helpers": ["bsearch"],
    },
}

EXPECTED_BASE64_DETERMINISM = {
    "standard_encode_vectors": 22,
    "variant_encode_vectors": 24,
    "standard_decode_vectors": 22,
    "variant_decode_vectors": 16,
    "invalid_decode_vectors": 28,
    "perf_payload_cases": 2,
    "perf_replay_cases": 10,
    "c_parity_self_test_cases": 8,
    "c_parity_cases": 112,
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
    "ipv6_pseudo_header_vectors": 3,
    "carry_discipline_vectors": 4,
    "kunit_random_prefix_vectors": 6,
    "c_parity_self_test_cases": 10,
    "c_parity_cases": 22,
}

EXPECTED_HEXDUMP_DETERMINISM = {
    "parity_vectors": 10,
    "overflow_vectors": 4,
    "required_length_vectors": 9,
    "perf_vectors": 4,
    "perf_labels": [
        "16B-plain",
        "32B-ascii-g2",
        "16B-ascii-g4",
        "16B-ascii-g8",
    ],
    "normalization_helpers": [
        "normalizedRowsize",
        "normalizedGroupsizeForLen",
        "prepareExpectedLine",
    ],
}


EXPECTED_BASE64_HELPER = {
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
}

EXPECTED_BSEARCH_HELPER = {
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
}

EXPECTED_CHECKSUM_HELPER = {
    "id": "checksum",
    "helper": "lib/checksum.zig",
    "tests": [
        "zigux/tests/phase6_checksum.zig",
        "zigux/tests/phase6_checksum_perf.zig",
        "zigux/tests/phase6_checksum_c_parity.zig",
    ],
    "fixtures": [
        "zigux/tests/fixtures/phase6_checksum_vectors.zig",
        "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    ],
    "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
    "external_parity": "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
}

EXPECTED_HEXDUMP_HELPER = {
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
}


def text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def require_markers(missing: list[str], label: str, content: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in content:
            missing.append(f"{label}:missing:{marker}")


def parse_catalog_head(content: str) -> tuple[str | None, str]:
    match = re.search(r"- verified head: `([0-9a-f]{40}|[^`]+)`", content)
    if match is None:
        return None, "missing"
    head = match.group(1)
    if not HEX40.fullmatch(head):
        return head, "invalid"
    return head, "ok"


def validate_manifest(missing: list[str], manifest: dict[str, object], catalog_head: str) -> None:
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")
    elif surveyed_commit != catalog_head:
        missing.append("manifest:surveyed_commit_mismatch")

    for key, expected in EXPECTED_MANIFEST.items():
        if manifest.get(key) != expected:
            missing.append(f"manifest:{key}")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list) or len(helpers) != 4:
        missing.append("manifest:helpers")
    else:
        expected_helpers = {
            "base64": EXPECTED_BASE64_HELPER,
            "bsearch": EXPECTED_BSEARCH_HELPER,
            "checksum": EXPECTED_CHECKSUM_HELPER,
            "hexdump": EXPECTED_HEXDUMP_HELPER,
        }
        for helper_id, expected_helper in expected_helpers.items():
            helper = next((item for item in helpers if item.get("id") == helper_id), None)
            if helper is None:
                missing.append(f"manifest:helpers:{helper_id}")
            elif helper != expected_helper:
                missing.append(f"manifest:helpers:{helper_id}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        missing.append("manifest:determinism_evidence")
        return
    if determinism.get("base64") != EXPECTED_BASE64_DETERMINISM:
        missing.append("manifest:determinism_evidence:base64")
    if determinism.get("bsearch") != EXPECTED_BSEARCH_DETERMINISM:
        missing.append("manifest:determinism_evidence:bsearch")
    if determinism.get("checksum") != EXPECTED_CHECKSUM_DETERMINISM:
        missing.append("manifest:determinism_evidence:checksum")
    if determinism.get("hexdump") != EXPECTED_HEXDUMP_DETERMINISM:
        missing.append("manifest:determinism_evidence:hexdump")
    if determinism.get("generated_fixture_artifacts_committed") is not False:
        missing.append("manifest:determinism_evidence:generated_fixture_artifacts_committed")


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

    catalog = text(root, "Documentation/zigux/phase6-helper-parity-catalog.md")
    catalog_head, catalog_head_status = parse_catalog_head(catalog)
    if catalog_head_status != "ok":
        return {
            "ok": False,
            "missing_files": [],
            "missing": [],
            "catalog_head": catalog_head or "",
            "catalog_head_status": catalog_head_status,
        }

    missing: list[str] = []
    require_markers(missing, "catalog", catalog, CATALOG_MARKERS)
    require_markers(missing, "perf_survey", text(root, "Documentation/zigux/phase6-perf-gate-survey.md"), PERF_SURVEY_MARKERS)
    require_markers(missing, "hexdump_slice", text(root, "Documentation/zigux/phase6-hexdump-slice.md"), HEXDUMP_SLICE_MARKERS)
    require_markers(missing, "scripts_readme", text(root, "scripts/zigux/README.md"), SCRIPTS_README_MARKERS)
    require_markers(missing, "docs_root", text(root, "Documentation/zigux/README.md"), DOCS_ROOT_MARKERS)
    require_markers(missing, "tests_readme", text(root, "zigux/tests/README.md"), TESTS_README_MARKERS)
    require_markers(missing, "workflow", text(root, ".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS)
    require_markers(missing, "phase6_build", text(root, "zigux/tests/phase6_build.zig"), PHASE6_BUILD_MARKERS)
    require_markers(missing, "base64_perf", text(root, "zigux/tests/phase6_base64_perf.zig"), BASE64_PERF_MARKERS)
    require_markers(missing, "bsearch_perf", text(root, "zigux/tests/phase6_bsearch_perf.zig"), BSEARCH_PERF_MARKERS)
    require_markers(missing, "checksum_perf", text(root, "zigux/tests/phase6_checksum_perf.zig"), CHECKSUM_PERF_MARKERS)
    require_markers(missing, "hexdump_perf", text(root, "zigux/tests/phase6_hexdump_perf.zig"), HEXDUMP_PERF_MARKERS)
    require_markers(missing, "checksum_vectors", text(root, "zigux/tests/fixtures/phase6_checksum_vectors.zig"), CHECKSUM_FIXTURE_MARKERS)
    require_markers(missing, "hexdump_vectors", text(root, "zigux/tests/fixtures/phase6_hexdump_vectors.zig"), HEXDUMP_FIXTURE_MARKERS)
    require_markers(missing, "checksum_parity_script", text(root, "scripts/zigux/check-phase6-checksum-c-parity.py"), CHECKSUM_PARITY_SCRIPT_MARKERS)
    require_markers(missing, "checksum_parity_runner", text(root, "zigux/tests/phase6_checksum_c_parity.zig"), CHECKSUM_PARITY_RUNNER_MARKERS)
    require_markers(missing, "checksum_parity_harness", text(root, "zigux/tests/fixtures/phase6_checksum_c_harness.c"), CHECKSUM_PARITY_HARNESS_MARKERS)
    require_markers(missing, "make", text(root, "zigux/Makefile"), MAKE_MARKERS)

    manifest = json.loads(text(root, "zigux/tests/phase6_helper_parity_manifest.json"))
    if not isinstance(manifest, dict):
        missing.append("manifest:root")
    else:
        validate_manifest(missing, manifest, catalog_head)

    return {
        "ok": not missing,
        "missing_files": [],
        "missing": missing,
        "catalog_head": catalog_head,
        "catalog_head_status": "ok",
    }


def report_validation(result: dict[str, object]) -> int:
    if result["missing_files"]:
        print("PHASE6_VALIDATION=fail")
        print("MISSING_PHASE6_FILES_START")
        for path in result["missing_files"]:
            print(path)
        print("MISSING_PHASE6_FILES_END")
        return 1
    if result["catalog_head_status"] != "ok":
        print("PHASE6_VALIDATION=fail")
        print(f"PHASE6_CATALOG_HEAD_STATUS={result['catalog_head_status']}")
        return 1
    if result["missing"]:
        print("PHASE6_VALIDATION=fail")
        print("PHASE6_MISSING_START")
        for item in result["missing"]:
            print(item)
        print("PHASE6_MISSING_END")
        return 1
    print("PHASE6_VALIDATION=pass")
    print(f"PHASE6_CATALOG_VERIFIED_HEAD={result['catalog_head']}")
    print("PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=23")
    return 0


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_self_test_tree(root: Path) -> None:
    for path in REQUIRED_FILES:
        write(root, path, "placeholder\n")
    write(root, "Documentation/zigux/phase6-helper-parity-catalog.md", "\n".join([f"# x", f"- verified head: `{SELF_TEST_HEAD}`", *CATALOG_MARKERS]) + "\n")
    write(root, "Documentation/zigux/phase6-perf-gate-survey.md", "\n".join(PERF_SURVEY_MARKERS) + "\n")
    write(root, "Documentation/zigux/phase6-hexdump-slice.md", "\n".join(HEXDUMP_SLICE_MARKERS) + "\n")
    write(root, "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write(root, "Documentation/zigux/README.md", "\n".join(DOCS_ROOT_MARKERS) + "\n")
    write(root, "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(WORKFLOW_MARKERS) + "\n")
    write(root, "zigux/tests/phase6_build.zig", "\n".join(PHASE6_BUILD_MARKERS) + "\n")
    write(root, "zigux/tests/phase6_base64_perf.zig", "\n".join(BASE64_PERF_MARKERS) + "\n")
    write(root, "zigux/tests/phase6_bsearch_perf.zig", "\n".join(BSEARCH_PERF_MARKERS) + "\n")
    write(root, "zigux/tests/phase6_checksum_perf.zig", "\n".join(CHECKSUM_PERF_MARKERS) + "\n")
    write(root, "zigux/tests/phase6_hexdump_perf.zig", "\n".join(HEXDUMP_PERF_MARKERS) + "\n")
    write(root, "zigux/tests/fixtures/phase6_checksum_vectors.zig", "\n".join(CHECKSUM_FIXTURE_MARKERS) + "\n")
    write(root, "zigux/tests/fixtures/phase6_hexdump_vectors.zig", "\n".join(HEXDUMP_FIXTURE_MARKERS) + "\n")
    write(root, "scripts/zigux/check-phase6-checksum-c-parity.py", "\n".join(CHECKSUM_PARITY_SCRIPT_MARKERS) + "\n")
    write(root, "zigux/tests/phase6_checksum_c_parity.zig", "\n".join(CHECKSUM_PARITY_RUNNER_MARKERS) + "\n")
    write(root, "zigux/tests/fixtures/phase6_checksum_c_harness.c", "\n".join(CHECKSUM_PARITY_HARNESS_MARKERS) + "\n")
    write(root, "zigux/Makefile", "\n".join(MAKE_MARKERS) + "\n")

    manifest = {
        **EXPECTED_MANIFEST,
        "surveyed_commit": SELF_TEST_HEAD,
        "helpers": [
            EXPECTED_BASE64_HELPER,
            EXPECTED_BSEARCH_HELPER,
            EXPECTED_CHECKSUM_HELPER,
            EXPECTED_HEXDUMP_HELPER,
        ],
        "determinism_evidence": {
            "base64": EXPECTED_BASE64_DETERMINISM,
            "bsearch": EXPECTED_BSEARCH_DETERMINISM,
            "checksum": EXPECTED_CHECKSUM_DETERMINISM,
            "hexdump": EXPECTED_HEXDUMP_DETERMINISM,
            "generated_fixture_artifacts_committed": False,
        },
    }
    write(root, "zigux/tests/phase6_helper_parity_manifest.json", json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_self_test_tree(root)

            pass_result = validate_phase6(root)
            if not pass_result["ok"]:
                raise AssertionError(pass_result)

            manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["surveyed_commit"] = SELF_TEST_MUTATED_HEAD
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if "manifest:surveyed_commit_mismatch" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing surveyed_commit mismatch")

            build_self_test_tree(root)
            survey = root / "Documentation/zigux/phase6-perf-gate-survey.md"
            survey.write_text(survey.read_text(encoding="utf-8").replace("max_slowdown_pct = 600", "", 1), encoding="utf-8")
            if "perf_survey:missing:max_slowdown_pct = 600" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing perf survey marker failure")

            build_self_test_tree(root)
            hexdump_slice = root / "Documentation/zigux/phase6-hexdump-slice.md"
            hexdump_slice.write_text(hexdump_slice.read_text(encoding="utf-8").replace(HEXDUMP_SLICE_MARKERS[1], "", 1), encoding="utf-8")
            if f"hexdump_slice:missing:{HEXDUMP_SLICE_MARKERS[1]}" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing hexdump slice marker failure")

            build_self_test_tree(root)
            scripts_readme = root / "scripts/zigux/README.md"
            scripts_readme.write_text(scripts_readme.read_text(encoding="utf-8").replace(SCRIPTS_README_MARKERS[0], "", 1), encoding="utf-8")
            if f"scripts_readme:missing:{SCRIPTS_README_MARKERS[0]}" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing scripts README marker failure")

            build_self_test_tree(root)
            docs_root = root / "Documentation/zigux/README.md"
            docs_root.write_text(docs_root.read_text(encoding="utf-8").replace(DOCS_ROOT_MARKERS[0], "", 1), encoding="utf-8")
            if f"docs_root:missing:{DOCS_ROOT_MARKERS[0]}" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing docs root marker failure")

            build_self_test_tree(root)
            tests_readme = root / "zigux/tests/README.md"
            tests_readme.write_text(tests_readme.read_text(encoding="utf-8").replace(TESTS_README_MARKERS[5], "", 1), encoding="utf-8")
            if f"tests_readme:missing:{TESTS_README_MARKERS[5]}" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing tests README marker failure")

            build_self_test_tree(root)
            workflow = root / ".github/workflows/zigux-bootstrap.yml"
            workflow.write_text(workflow.read_text(encoding="utf-8").replace(WORKFLOW_MARKERS[0], "", 1), encoding="utf-8")
            if f"workflow:missing:{WORKFLOW_MARKERS[0]}" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing workflow marker failure")

            build_self_test_tree(root)
            phase6_build = root / "zigux/tests/phase6_build.zig"
            phase6_build.write_text(phase6_build.read_text(encoding="utf-8").replace(PHASE6_BUILD_MARKERS[4], "", 1), encoding="utf-8")
            if f"phase6_build:missing:{PHASE6_BUILD_MARKERS[4]}" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing phase6 build marker failure")

            build_self_test_tree(root)
            catalog = root / "Documentation/zigux/phase6-helper-parity-catalog.md"
            catalog.write_text(catalog.read_text(encoding="utf-8").replace("PHASE6_CHECKSUM_C_PARITY_CASES=22", "", 1), encoding="utf-8")
            if "catalog:missing:PHASE6_CHECKSUM_C_PARITY_CASES=22" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing catalog failure")

            build_self_test_tree(root)
            makefile = root / "zigux/Makefile"
            makefile.write_text(makefile.read_text(encoding="utf-8").replace("phase6-perf:", "", 1), encoding="utf-8")
            if "make:missing:phase6-perf:" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing aggregate perf make marker failure")

            build_self_test_tree(root)
            checksum_vectors = root / "zigux/tests/fixtures/phase6_checksum_vectors.zig"
            checksum_vectors.write_text("", encoding="utf-8")
            if "checksum_vectors:missing:.max_slowdown_pct = 150" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing checksum threshold failure")

            build_self_test_tree(root)
            hexdump_vectors = root / "zigux/tests/fixtures/phase6_hexdump_vectors.zig"
            hexdump_vectors.write_text("", encoding="utf-8")
            if "hexdump_vectors:missing:.{ .label = \"16B-ascii-g8\", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 }," not in validate_phase6(root)["missing"]:
                raise AssertionError("missing hexdump threshold failure")

            build_self_test_tree(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["shared_gates"] = manifest["shared_gates"][:-1]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if "manifest:shared_gates" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing shared gates manifest failure")

            build_self_test_tree(root)
            bad_catalog = root / "Documentation/zigux/phase6-helper-parity-catalog.md"
            bad_catalog.write_text("- verified head: `not-a-sha`\n", encoding="utf-8")
            bad_result = validate_phase6(root)
            if bad_result["catalog_head_status"] != "invalid":
                raise AssertionError("missing catalog head invalid failure")

            build_self_test_tree(root)
            missing_file = root / "zigux/tests/phase6_checksum_c_parity.zig"
            missing_file.unlink()
            if "zigux/tests/phase6_checksum_c_parity.zig" not in validate_phase6(root)["missing_files"]:
                raise AssertionError("missing required file failure")

            build_self_test_tree(root)
            base64_runner = root / "zigux/tests/phase6_base64_c_parity.zig"
            base64_runner.unlink()
            if "zigux/tests/phase6_base64_c_parity.zig" not in validate_phase6(root)["missing_files"]:
                raise AssertionError("missing base64 parity runner failure")

            build_self_test_tree(root)
            bsearch_runner = root / "zigux/tests/phase6_bsearch_c_parity.zig"
            bsearch_runner.unlink()
            if "zigux/tests/phase6_bsearch_c_parity.zig" not in validate_phase6(root)["missing_files"]:
                raise AssertionError("missing bsearch parity runner failure")

            build_self_test_tree(root)
            checksum_test = root / "zigux/tests/phase6_checksum.zig"
            checksum_test.unlink()
            if "zigux/tests/phase6_checksum.zig" not in validate_phase6(root)["missing_files"]:
                raise AssertionError("missing checksum test failure")

            build_self_test_tree(root)
            hexdump_test = root / "zigux/tests/phase6_hexdump.zig"
            hexdump_test.unlink()
            if "zigux/tests/phase6_hexdump.zig" not in validate_phase6(root)["missing_files"]:
                raise AssertionError("missing hexdump test failure")

            build_self_test_tree(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["helpers"][0]["fixtures"] = manifest["helpers"][0]["fixtures"][:-1]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if "manifest:helpers:base64" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing base64 helper manifest failure")

            build_self_test_tree(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["helpers"][1]["external_parity"] = "python3 scripts/zigux/check-phase6-bsearch-c-parity.py --bogus"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if "manifest:helpers:bsearch" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing bsearch helper manifest failure")

            build_self_test_tree(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["helpers"][3]["slice_note"] = "Documentation/zigux/phase6-hexdump-slice.md -- drift"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if "manifest:helpers:hexdump" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing hexdump helper manifest failure")

            build_self_test_tree(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["determinism_evidence"]["generated_fixture_artifacts_committed"] = True
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if "manifest:determinism_evidence:generated_fixture_artifacts_committed" not in validate_phase6(root)["missing"]:
                raise AssertionError("missing generated fixture flag failure")
    except AssertionError as exc:
        print("PHASE6_VALIDATOR_SELF_TEST=fail")
        print(f"PHASE6_VALIDATOR_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_VALIDATOR_SELF_TEST=pass")
    print("PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT=23")
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
