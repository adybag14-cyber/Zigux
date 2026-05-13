#!/usr/bin/env python3
"""Fail-closed checks for the current bounded Phase 6 shared-surface packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
LANE_PATH = Path("Documentation/zigux/phase6-leaf-helper-lane-sequencing.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HEXDUMP_SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")

BASE64_HELPER_PATH = Path("lib/base64.zig")
BASE64_REPLAY_PATH = Path("zigux/tests/phase6_base64.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BASE64_PARITY_PATH = Path("zigux/tests/phase6_base64_c_parity.zig")
BASE64_CASEGEN_PATH = Path("zigux/tests/phase6_base64_c_casegen.zig")
BASE64_PARITY_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")
BASE64_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_harness.c")
BASE64_GENERATED_INCLUDE_PATH = Path("zigux/tests/fixtures/phase6_base64_c_generated_cases.inc")

BSEARCH_HELPER_PATH = Path("lib/bsearch.zig")
BSEARCH_REPLAY_PATH = Path("zigux/tests/phase6_bsearch.zig")
BSEARCH_LOWER_BOUND_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
BSEARCH_BUDGET_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
BSEARCH_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")

CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_PARITY_PATH = Path("zigux/tests/phase6_checksum_c_parity.zig")
CHECKSUM_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_checksum_c_harness.c")

HEXDUMP_HELPER_PATH = Path("lib/hexdump.zig")
HEXDUMP_REPLAY_PATH = Path("zigux/tests/phase6_hexdump.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
HEXDUMP_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_REFRESH_PATH = Path("Documentation/zigux/phase6-hexdump-perf-refresh.md")

BASE64_PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
BSEARCH_CORPUS_SCRIPT_PATH = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
CHECKSUM_PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
HEXDUMP_PACKET_SCRIPT_PATH = Path("scripts/zigux/check-phase6-hexdump-packet.py")
PERF_THRESHOLD_SCRIPT_PATH = Path("scripts/zigux/check-phase6-perf-threshold-markers.py")

ABSENT_PATHS = [
    BASE64_PERF_PATH,
    BASE64_GENERATED_INCLUDE_PATH,
    CHECKSUM_HELPER_PATH,
    CHECKSUM_REPLAY_PATH,
    CHECKSUM_PERF_PATH,
    CHECKSUM_VECTORS_PATH,
]

PRESENT_PATHS = [
    MANIFEST_PATH,
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    CATALOG_PATH,
    PERF_SURVEY_PATH,
    LANE_PATH,
    BASE64_SLICE_PATH,
    BSEARCH_SLICE_PATH,
    CHECKSUM_SLICE_PATH,
    HEXDUMP_SLICE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    PHASE6_BUILD_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    BASE64_HELPER_PATH,
    BASE64_REPLAY_PATH,
    BASE64_VECTORS_PATH,
    BASE64_PARITY_PATH,
    BASE64_CASEGEN_PATH,
    BASE64_PARITY_VECTORS_PATH,
    BASE64_C_HARNESS_PATH,
    BSEARCH_HELPER_PATH,
    BSEARCH_REPLAY_PATH,
    BSEARCH_LOWER_BOUND_PATH,
    BSEARCH_BUDGET_PATH,
    BSEARCH_VECTORS_PATH,
    CHECKSUM_PARITY_PATH,
    CHECKSUM_C_HARNESS_PATH,
    HEXDUMP_HELPER_PATH,
    HEXDUMP_REPLAY_PATH,
    HEXDUMP_PERF_PATH,
    HEXDUMP_MATRIX_PATH,
    HEXDUMP_VECTORS_PATH,
    HEXDUMP_REFRESH_PATH,
    BASE64_PARITY_SCRIPT_PATH,
    BSEARCH_CORPUS_SCRIPT_PATH,
    CHECKSUM_PARITY_SCRIPT_PATH,
    HEXDUMP_PACKET_SCRIPT_PATH,
    PERF_THRESHOLD_SCRIPT_PATH,
]

REQUIRED_SNIPPETS = {
    DOCS_README_PATH.as_posix(): [
        "`zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `scripts/zigux/check-phase6-base64-c-parity.py`, `zigux/tests/phase6_bsearch.zig`",
        "while `zigux/tests/phase6_base64_perf.zig`, `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` stay explicit as current public-tree gaps rather than shipped replay evidence.",
        "the current bounded Phase 6 decision is no longer whether the base64 and checksum helper packet is fully runnable on `master`",
    ],
    CATALOG_PATH.as_posix(): [
        "- focused helper replay: `zigux/tests/phase6_base64.zig`",
        "- focused slowdown-fixture companion: `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- currently missing helper-local perf replay on `master`: `zigux/tests/phase6_base64_perf.zig`",
        "- current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    ],
    PERF_SURVEY_PATH.as_posix(): [
        "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` are directly readable on current `master`, but `zigux/tests/phase6_base64_perf.zig` is still absent",
        "* checksum shared posture: `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "* the current bundled Phase 6 route inventory still advertises three dedicated helper-local perf gates beside the aggregate `phase6-perf` marker, but the base64 leg remains documentary because its committed perf replay file is absent and the checksum leg remains documentary because its helper-local replay packet is absent from `master`",
    ],
    LANE_PATH.as_posix(): [
        "The current backlog-backed next safe step for `P6-Y11` is one shared closure-note or ledger sync before any broader tests-root or checker rewrite",
        "direct current-`master` file reads still show `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_bsearch.zig`, while `zigux/tests/phase6_base64_perf.zig`, `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` are not directly readable from that same head",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "- current `master` still keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- current `master` lacks `zigux/tests/phase6_base64_perf.zig`",
        "- helper-local truthfulness note: the focused helper replay and shared vectors are directly readable again on current `master`",
    ],
    BSEARCH_SLICE_PATH.as_posix(): [
        "# Phase 6 Bsearch Slice",
        "- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "- current `master` still lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current `master` still keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet",
    ],
    HEXDUMP_SLICE_PATH.as_posix(): [
        "# Phase 6 Hexdump Slice",
        "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
        "- `make -C zigux phase6-hexdump-review`",
    ],
    BASE64_PARITY_SCRIPT_PATH.as_posix(): [
        'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
    ],
    BSEARCH_CORPUS_SCRIPT_PATH.as_posix(): [
        '"""Fail-closed exact evidence checks for the Phase 6 bsearch corpus packet."""',
        'print("Phase 6 bsearch corpus evidence looks aligned.")',
    ],
    CHECKSUM_PARITY_SCRIPT_PATH.as_posix(): [
        'print(f"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}")',
    ],
    HEXDUMP_PACKET_SCRIPT_PATH.as_posix(): [
        '"""Fail-closed checker for the bounded Phase 6 hexdump review packet."""',
        'print("PHASE6_HEXDUMP_PACKET_SELF_TEST=pass")',
    ],
    PERF_THRESHOLD_SCRIPT_PATH.as_posix(): [
        '"""Fail-closed checks for the current Phase 6 exact perf-threshold packet."""',
        'print("self-test passed")',
    ],
}

EXPECTED_PACKET_STATE_SUMMARY = {
    "base64": "partial_replay_present_perf_missing",
    "bsearch": "parked_reviewable",
    "checksum": "blocked_helper_packet_missing",
    "hexdump": "parked_reviewable",
}

EXPECTED_HELPER_SLICE_NOTES = {
    "base64": BASE64_SLICE_PATH.as_posix(),
    "bsearch": BSEARCH_SLICE_PATH.as_posix(),
    "checksum": CHECKSUM_SLICE_PATH.as_posix(),
    "hexdump": HEXDUMP_SLICE_PATH.as_posix(),
}

EXPECTED_SHARED_ROUTE_NOTE = (
    "base64 now keeps lib/base64.zig, zigux/tests/phase6_base64.zig, and "
    "zigux/tests/fixtures/phase6_base64_vectors.zig plus the direct C parity "
    "packet while zigux/tests/phase6_base64_perf.zig remains absent, and checksum "
    "still lacks lib/checksum.zig plus its helper-owned replay, perf, and shared-vector "
    "files even though zigux/tests/phase6_checksum_c_parity.zig plus "
    "zigux/tests/fixtures/phase6_checksum_c_harness.c remain directly readable."
)

EXPECTED_SHARED_GATES = [
    DOCS_README_PATH.as_posix(),
    REVIEW_CHECKLIST_PATH.as_posix(),
    CATALOG_PATH.as_posix(),
    PERF_SURVEY_PATH.as_posix(),
    LANE_PATH.as_posix(),
    SCRIPTS_README_PATH.as_posix(),
    Path("scripts/zigux/check-phase6-shared-surface.py").as_posix(),
    TESTS_README_PATH.as_posix(),
    PHASE6_BUILD_PATH.as_posix(),
    WORKFLOW_PATH.as_posix(),
    MAKEFILE_PATH.as_posix(),
]

EXPECTED_TESTS_ROOT_PRESENT_ENTRYPOINTS = [
    PHASE6_BUILD_PATH.as_posix(),
    MANIFEST_PATH.as_posix(),
    CATALOG_PATH.as_posix(),
    PERF_SURVEY_PATH.as_posix(),
    BASE64_REPLAY_PATH.as_posix(),
    BASE64_PARITY_PATH.as_posix(),
    BASE64_VECTORS_PATH.as_posix(),
    BASE64_C_HARNESS_PATH.as_posix(),
    BASE64_PARITY_SCRIPT_PATH.as_posix(),
    BSEARCH_REPLAY_PATH.as_posix(),
    BSEARCH_LOWER_BOUND_PATH.as_posix(),
    BSEARCH_BUDGET_PATH.as_posix(),
    BSEARCH_VECTORS_PATH.as_posix(),
    CHECKSUM_PARITY_PATH.as_posix(),
    CHECKSUM_C_HARNESS_PATH.as_posix(),
    CHECKSUM_PARITY_SCRIPT_PATH.as_posix(),
    HEXDUMP_REPLAY_PATH.as_posix(),
    HEXDUMP_PERF_PATH.as_posix(),
    HEXDUMP_MATRIX_PATH.as_posix(),
    HEXDUMP_VECTORS_PATH.as_posix(),
]

EXPECTED_TESTS_ROOT_PUBLIC_TREE_GAPS = [
    BASE64_PERF_PATH.as_posix(),
    CHECKSUM_HELPER_PATH.as_posix(),
    CHECKSUM_REPLAY_PATH.as_posix(),
    CHECKSUM_PERF_PATH.as_posix(),
    CHECKSUM_VECTORS_PATH.as_posix(),
]

EXPECTED_TESTS_ROOT_TRUTHFULNESS_NOTE = (
    "zigux/tests/README.md should keep tests_root_present_entrypoints as the current "
    "Phase 6 tests-root evidence packet, keep zigux/tests/phase6_base64_perf.zig "
    "explicit as the remaining base64 public-tree gap, and keep the still-missing "
    "checksum helper, focused replay, perf replay, and shared vectors explicit "
    "until those checksum-owned assets return."
)

EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES = [
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "make -C zigux phase6-base64-c-parity",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "make -C zigux phase6-checksum-c-parity",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-validate",
    "make -C zigux phase6-perf",
    "make -C zigux phase6",
]

EXPECTED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-hexdump-review",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
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


def require_snippets(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(f"missing expected Phase 6 marker in {rel_path}: {snippet}")


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    if manifest.get("status") != "partially_blocked":
        raise ValidationError(f"unexpected Phase 6 status in {MANIFEST_PATH}")

    if manifest.get("packet_state_summary") != EXPECTED_PACKET_STATE_SUMMARY:
        raise ValidationError(f"unexpected packet_state_summary in {MANIFEST_PATH}")

    if manifest.get("shared_route_truthfulness_note") != EXPECTED_SHARED_ROUTE_NOTE:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {MANIFEST_PATH}")

    if manifest.get("shared_gates") != EXPECTED_SHARED_GATES:
        raise ValidationError(f"unexpected shared_gates in {MANIFEST_PATH}")

    if manifest.get("tests_root_present_entrypoints") != EXPECTED_TESTS_ROOT_PRESENT_ENTRYPOINTS:
        raise ValidationError(f"unexpected tests_root_present_entrypoints in {MANIFEST_PATH}")

    if manifest.get("tests_root_public_tree_gaps") != EXPECTED_TESTS_ROOT_PUBLIC_TREE_GAPS:
        raise ValidationError(f"unexpected tests_root_public_tree_gaps in {MANIFEST_PATH}")

    if manifest.get("tests_root_truthfulness_note") != EXPECTED_TESTS_ROOT_TRUTHFULNESS_NOTE:
        raise ValidationError(f"unexpected tests_root_truthfulness_note in {MANIFEST_PATH}")

    if manifest.get("inventory_only_blocked_routes") != EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES:
        raise ValidationError(f"unexpected inventory_only_blocked_routes in {MANIFEST_PATH}")

    if manifest.get("exact_checks") != EXPECTED_EXACT_CHECKS:
        raise ValidationError(f"unexpected exact_checks in {MANIFEST_PATH}")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        raise ValidationError(f"missing surveyed_commit in {MANIFEST_PATH}")

    catalog_text = read_text(repo_root / CATALOG_PATH)
    if f"- surveyed head: `{surveyed_commit}`" not in catalog_text:
        raise ValidationError(f"catalog surveyed head does not match manifest surveyed_commit in {CATALOG_PATH}")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers list in {MANIFEST_PATH}")

    helper_map = {
        item["id"]: item
        for item in helpers
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for helper_id, slice_path in EXPECTED_HELPER_SLICE_NOTES.items():
        helper = helper_map.get(helper_id)
        if not isinstance(helper, dict):
            raise ValidationError(f"missing helper row for {helper_id} in {MANIFEST_PATH}")
        if helper.get("slice_note") != slice_path:
            raise ValidationError(f"unexpected slice_note for {helper_id} in {MANIFEST_PATH}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {MANIFEST_PATH}")
    base64 = determinism.get("base64")
    bsearch = determinism.get("bsearch")
    checksum = determinism.get("checksum")
    hexdump = determinism.get("hexdump")
    if not isinstance(base64, dict) or base64.get("c_parity_cases") != 24:
        raise ValidationError(f"unexpected base64 determinism evidence in {MANIFEST_PATH}")
    if base64.get("transient_generated_include_committed") is not False:
        raise ValidationError(f"unexpected base64 generated-include posture in {MANIFEST_PATH}")
    if not isinstance(bsearch, dict) or bsearch.get("comparison_budget_max_compare_calls") != 4:
        raise ValidationError(f"unexpected bsearch determinism evidence in {MANIFEST_PATH}")
    if bsearch.get("fixture_dynamic_case_lengths") != 33:
        raise ValidationError(f"unexpected bsearch fixture dynamic lengths in {MANIFEST_PATH}")
    if not isinstance(checksum, dict) or checksum.get("c_parity_cases") != 27:
        raise ValidationError(f"unexpected checksum determinism evidence in {MANIFEST_PATH}")
    if not isinstance(hexdump, dict) or hexdump.get("perf_replay_cases") != 4:
        raise ValidationError(f"unexpected hexdump determinism evidence in {MANIFEST_PATH}")


def validate_paths(repo_root: Path) -> None:
    for rel_path in PRESENT_PATHS:
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")
    for rel_path in ABSENT_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(f"Phase 6 path should stay absent in the current packet: {rel_path}")


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    manifest = {
        "phase": "Phase 6",
        "tranche": "leaf-helper-parity",
        "status": "partially_blocked",
        "packet_state_summary": dict(EXPECTED_PACKET_STATE_SUMMARY),
        "shared_route_truthfulness_note": EXPECTED_SHARED_ROUTE_NOTE,
        "surveyed_commit": "a0f4d7e",
        "helpers": [
            {"id": "base64", "slice_note": BASE64_SLICE_PATH.as_posix()},
            {"id": "bsearch", "slice_note": BSEARCH_SLICE_PATH.as_posix()},
            {"id": "checksum", "slice_note": CHECKSUM_SLICE_PATH.as_posix()},
            {"id": "hexdump", "slice_note": HEXDUMP_SLICE_PATH.as_posix()},
        ],
        "shared_gates": list(EXPECTED_SHARED_GATES),
        "tests_root_present_entrypoints": list(EXPECTED_TESTS_ROOT_PRESENT_ENTRYPOINTS),
        "tests_root_public_tree_gaps": list(EXPECTED_TESTS_ROOT_PUBLIC_TREE_GAPS),
        "tests_root_truthfulness_note": EXPECTED_TESTS_ROOT_TRUTHFULNESS_NOTE,
        "inventory_only_blocked_routes": list(EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES),
        "exact_checks": list(EXPECTED_EXACT_CHECKS),
        "determinism_evidence": {
            "base64": {
                "c_parity_cases": 24,
                "transient_generated_include_committed": False,
            },
            "bsearch": {
                "comparison_budget_max_compare_calls": 4,
                "fixture_dynamic_case_lengths": 33,
            },
            "checksum": {
                "c_parity_cases": 27,
            },
            "hexdump": {
                "perf_replay_cases": 4,
            },
        },
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        body = "\n".join(snippets)
        if rel_path == CATALOG_PATH.as_posix():
            body += "\n- surveyed head: `a0f4d7e`\n"
        else:
            body += "\n"
        write(root / rel_path, body)

    placeholder_files = {
        REVIEW_CHECKLIST_PATH: "# review checklist\n",
        SCRIPTS_README_PATH: "# scripts root\n",
        TESTS_README_PATH: "# tests root\n",
        BASE64_HELPER_PATH: "pub fn encode() void {}\n",
        BASE64_REPLAY_PATH: 'test "phase6 base64 replay" {}\n',
        BASE64_VECTORS_PATH: "pub const perf_cases = .{};\n",
        BASE64_PARITY_PATH: 'test "phase6 base64 c parity" {}\n',
        BASE64_CASEGEN_PATH: "pub fn main() void {}\n",
        BASE64_PARITY_VECTORS_PATH: "pub const standard_cases = .{};\n",
        BASE64_C_HARNESS_PATH: "int main(void) { return 0; }\n",
        BSEARCH_HELPER_PATH: "pub fn locate() void {}\n",
        BSEARCH_REPLAY_PATH: 'test "phase6 bsearch" {}\n',
        BSEARCH_LOWER_BOUND_PATH: 'test "phase6 bsearch lower bound" {}\n',
        BSEARCH_BUDGET_PATH: 'test "phase6 bsearch budget" {}\n',
        BSEARCH_VECTORS_PATH: "pub const seed_cases = .{};\n",
        CHECKSUM_PARITY_PATH: 'test "phase6 checksum c parity" {}\n',
        CHECKSUM_C_HARNESS_PATH: "int main(void) { return 0; }\n",
        HEXDUMP_HELPER_PATH: "pub fn format() void {}\n",
        HEXDUMP_REPLAY_PATH: 'test "phase6 hexdump" {}\n',
        HEXDUMP_PERF_PATH: "pub fn main() void {}\n",
        HEXDUMP_MATRIX_PATH: 'test "phase6 hexdump matrix" {}\n',
        HEXDUMP_VECTORS_PATH: "pub const cases = .{};\n",
        HEXDUMP_REFRESH_PATH: "# hexdump refresh\n",
        PHASE6_BUILD_PATH: 'const std = @import("std");\n',
        WORKFLOW_PATH: "name: zigux-bootstrap\n",
        MAKEFILE_PATH: "phase6:\n\t@true\n",
        BASE64_PARITY_SCRIPT_PATH: 'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")\n',
        BSEARCH_CORPUS_SCRIPT_PATH: '"""Fail-closed exact evidence checks for the Phase 6 bsearch corpus packet."""\nprint("Phase 6 bsearch corpus evidence looks aligned.")\n',
        CHECKSUM_PARITY_SCRIPT_PATH: 'print(f"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}")\n',
        HEXDUMP_PACKET_SCRIPT_PATH: '"""Fail-closed checker for the bounded Phase 6 hexdump review packet."""\nprint("PHASE6_HEXDUMP_PACKET_SELF_TEST=pass")\n',
        PERF_THRESHOLD_SCRIPT_PATH: '"""Fail-closed checks for the current Phase 6 exact perf-threshold packet."""\nprint("self-test passed")\n',
    }
    for rel_path, content in placeholder_files.items():
        write(root / rel_path, content)


def assert_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if rel_path.as_posix() not in str(exc):
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
            MANIFEST_PATH,
            '"base64": "partial_replay_present_perf_missing"',
            '"base64": "blocked_helper_packet_missing"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"zigux/tests/phase6_base64_perf.zig"',
            '"zigux/tests/phase6_base64.zig"',
        )
        assert_failure(
            root,
            DOCS_README_PATH,
            "zigux/tests/phase6_base64_perf.zig`, `lib/checksum.zig`",
            "lib/checksum.zig`",
        )
        assert_failure(
            root,
            CATALOG_PATH,
            "- currently missing helper-local perf replay on `master`: `zigux/tests/phase6_base64_perf.zig`",
            "- currently missing helper-local perf replay on `master`: `zigux/tests/phase6_base64.zig`",
        )
        assert_failure(
            root,
            PERF_SURVEY_PATH,
            "`zigux/tests/phase6_base64_perf.zig` is still absent",
            "`zigux/tests/phase6_base64_perf.zig` is present",
        )
        assert_failure(
            root,
            BASE64_SLICE_PATH,
            "- current `master` lacks `zigux/tests/phase6_base64_perf.zig`",
            "- current `master` lacks nothing in the base64 packet",
        )
        assert_failure(
            root,
            CHECKSUM_SLICE_PATH,
            "- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet",
            "- current review posture: runnable",
        )
        unexpected_present = root / BASE64_PERF_PATH
        write(unexpected_present, "unexpected\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if BASE64_PERF_PATH.as_posix() not in str(exc):
                raise AssertionError(f"unexpected absent-path failure: {exc}") from exc
        else:
            raise AssertionError("expected absent-path failure")
        unexpected_present.unlink()
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
    print("Phase 6 shared surface matches the current partially blocked packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
