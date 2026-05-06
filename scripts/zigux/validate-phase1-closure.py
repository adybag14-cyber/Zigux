#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile
from typing import Any


_SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else _SELF_PATH.parent
EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]
EXPECTED_BENCH_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}
EXPECTED_BENCH_CHECKSUMS = [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
]
WORKFLOW_INSTALL_ZIG_RE = re.compile(
    r"python3 scripts/zigux/install-zig\.py --channel \S+ --dest \.zig-toolchain"
)

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_bench.zig",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
]

required_closure_markers = [
    (
        "closure_status_count",
        "PHASE1_STATUS=closed",
        1,
    ),
    (
        "closure_helper_count_count",
        "PHASE1_HELPER_COUNT=13",
        1,
    ),
    (
        "closure_manifest_line_count",
        "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
        1,
    ),
    (
        "closure_parity_gate_count",
        "PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py",
        1,
    ),
    (
        "closure_unit_gate_count",
        "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig",
        1,
    ),
    (
        "closure_bench_gate_count",
        "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig",
        1,
    ),
    (
        "closure_bench_check_gate_count",
        "PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py",
        1,
    ),
    (
        "closure_closure_gate_count",
        "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py",
        1,
    ),
    (
        "closure_rollback_count",
        "PHASE1_ROLLBACK=keep C authoritative and remove failing Zig helper from test/build wiring",
        1,
    ),
    (
        "closure_shared_review_workflow_count",
        "- `.github/workflows/zigux-bootstrap.yml`",
        1,
    ),
    (
        "closure_find_bit_single_word_review_count",
        "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior",
        1,
    ),
    (
        "closure_find_bit_inclusive_boundary_review_count",
        "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start",
        1,
    ),
    (
        "closure_find_bit_tail_clamp_review_count",
        "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits",
        1,
    ),
    (
        "closure_bitmap_partial_xor_review_count",
        "PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay explicit through the shared Phase 1 parity fixture and replay so caller-selected bit windows cannot silently leak tail bits beyond nbits",
        1,
    ),
    (
        "closure_bitmap_scnprintf_truncation_review_count",
        "PHASE1_BITMAP_SCNPRINTF_TRUNCATION_REVIEW=helper-local bitmap.scnprintf truncation proof stays explicit through the direct bitmap test anchor because the shared Phase 1 parity fixture only locks the full rendered range string",
        1,
    ),
    (
        "closure_bitmap_copy_alias_review_count",
        "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics",
        1,
    ),
    (
        "closure_rbtree_review_packet_count",
        "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal and detached-node replay stay explicit so duplicate-search and cached-root behavior keep direct review anchors without implying a broader duplicate-search fixture packet than current master ships",
        1,
    ),
    (
        "closure_string_review_packet_count",
        "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors and parity fixture keys",
        1,
    ),
]
required_workflow_markers = [
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "uses: actions/checkout@v6.0.2",
    "uses: actions/setup-python@v6.2.0",
    "python3 scripts/zigux/check-zig-toolchain.py",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "python3 scripts/zigux/check-phase1-bench.py",
    "zig build bench --build-file zigux/tests/build.zig",
]
required_exact_workflow_markers = [
    (
        "workflow_node24_count",
        "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
        1,
    ),
    (
        "workflow_checkout_count",
        "uses: actions/checkout@v6.0.2",
        1,
    ),
    (
        "workflow_setup_python_count",
        "uses: actions/setup-python@v6.2.0",
        1,
    ),
    (
        "workflow_toolchain_check_count",
        "run: python3 scripts/zigux/check-zig-toolchain.py",
        1,
    ),
    (
        "workflow_install_zig_count",
        "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
        1,
    ),
]
required_phase1_workflow_markers = [
    (
        "workflow_phase1_validate_count",
        "run: python3 scripts/zigux/validate-phase1.py",
        1,
    ),
    (
        "workflow_phase1_closure_count",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        1,
    ),
    (
        "workflow_phase1_parity_count",
        "run: python3 scripts/zigux/check-phase1-parity.py",
        1,
    ),
    (
        "workflow_phase1_bench_count",
        "run: python3 scripts/zigux/check-phase1-bench.py",
        1,
    ),
    (
        "workflow_phase1_unit_replay_count",
        "run: zig build test --build-file zigux/tests/build.zig",
        1,
    ),
    (
        "workflow_phase1_bench_replay_count",
        "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe",
        1,
    ),
]
required_build_markers = [
    (
        "build_phase1_bench_source_count",
        "phase1_bench.zig",
        1,
    ),
    (
        "build_phase1_bench_step_count",
        "const bench_step = b.step(\"bench\", \"Run Phase 1 helper benchmark smoke\");",
        1,
    ),
]
required_ledger_markers = [
    (
        "ledger_phase1_closure_commit_count",
        "docs(zigux): close bounded phase-1 helper tranche",
        1,
    ),
]
required_makefile_markers = [
    (
        "makefile_phase1_validate_target",
        "phase1-validate:",
        1,
    ),
    (
        "makefile_phase1_validate_inventory",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py",
        1,
    ),
    (
        "makefile_phase1_validate_closure",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
        1,
    ),
    (
        "makefile_phase1_test_target",
        "phase1-test:",
        1,
    ),
    (
        "makefile_phase1_test_parity",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
        1,
    ),
    (
        "makefile_phase1_test_replay",
        "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig",
        1,
    ),
    (
        "makefile_phase1_bench_target",
        "phase1-bench:",
        1,
    ),
    (
        "makefile_phase1_bench_check",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py",
        1,
    ),
    (
        "makefile_phase1_bench_replay",
        "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig",
        1,
    ),
    (
        "makefile_phase1_target",
        "phase1: phase1-validate phase1-test phase1-bench",
        1,
    ),
]
required_docs_root_markers = [
    (
        "docs_root_phase1_packet",
        "- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the closure, bootstrap-workflow replay, and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.",
        1,
    ),
]
required_scripts_readme_markers = [
    (
        "scripts_readme_phase1_packet",
        "- `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep that same closed host-side helper packet reviewable through the docs-root closure record, the reviewer-facing checklist, the bootstrap workflow replay, and the Linux-style replay routes instead of leaving the Phase 1 closure stack visible only through direct script and Zig commands.",
        1,
    ),
]
required_tests_readme_markers = [
    (
        "tests_readme_phase1_packet",
        "  * keep the closed Phase 1 host-tools packet explicit in the tests root too: `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` should continue to keep the closed helper tranche reviewable from the tests root instead of leaving the host-tools closure stack split across the docs root, scripts root, and workflow replay surface",
        1,
    ),
]
required_review_checklist_markers = [
    (
        "review_checklist_phase1_packet",
        "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` still agree on the same closed helper tranche and validator-first replay path without widening Phase 1 beyond the bounded host-side helper packet?",
        1,
    ),
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg is None:
        return DEFAULT_ROOT
    return Path(root_arg).resolve()


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_manifest_markers(manifest: object, root: Path) -> list[str]:
    missing_markers: list[str] = []
    if not isinstance(manifest, dict):
        return ["manifest:json_object"]

    manifest_helpers = manifest.get("helpers")
    if not isinstance(manifest_helpers, list):
        return ["manifest:helpers=list"]

    manifest_count = manifest.get("helper_count")
    if manifest.get("phase") != "Phase 1":
        missing_markers.append("manifest:phase=Phase 1")
    if manifest.get("status") != "closed":
        missing_markers.append("manifest:status=closed")
    if manifest_count != len(EXPECTED_HELPERS):
        missing_markers.append(f"manifest:helper_count={len(EXPECTED_HELPERS)}")
    if len(manifest_helpers) != len(EXPECTED_HELPERS):
        missing_markers.append(f"manifest:helpers_len={len(EXPECTED_HELPERS)}")

    seen: set[str] = set()
    duplicates: list[str] = []
    string_helpers: list[str] = []
    for rel in manifest_helpers:
        if not isinstance(rel, str):
            missing_markers.append("manifest:helper_path_type=str")
            continue
        string_helpers.append(rel)
        if rel in seen and rel not in duplicates:
            duplicates.append(rel)
        seen.add(rel)
        if not (root / rel).exists():
            missing_markers.append(f"manifest_file:{rel}")

    expected = set(EXPECTED_HELPERS)
    actual = set(string_helpers)
    for rel in sorted(expected - actual):
        missing_markers.append(f"manifest:missing_helper={rel}")
    for rel in sorted(actual - expected):
        missing_markers.append(f"manifest:unexpected_helper={rel}")
    for rel in duplicates:
        missing_markers.append(f"manifest:duplicate_helper={rel}")

    return missing_markers


def collect_bench_expectation_markers(expectations: object) -> list[str]:
    missing_markers: list[str] = []
    if not isinstance(expectations, dict):
        return ["bench_expectations:json_object"]

    if expectations.get("status") != "pass":
        missing_markers.append("bench_expectations:status=pass")

    iterations = expectations.get("iterations")
    if not isinstance(iterations, dict):
        missing_markers.append("bench_expectations:iterations=dict")
    else:
        actual_iteration_keys: set[str] = set()
        for key, value in iterations.items():
            if not isinstance(key, str):
                missing_markers.append("bench_expectations:iteration_key_type=str")
                continue
            actual_iteration_keys.add(key)
            expected_value = EXPECTED_BENCH_ITERATIONS.get(key)
            if expected_value is None:
                missing_markers.append(f"bench_expectations:unexpected_iteration={key}")
                continue
            if value != expected_value:
                missing_markers.append(
                    f"bench_expectations:iteration_value={key}:{expected_value}"
                )
        for key in sorted(set(EXPECTED_BENCH_ITERATIONS) - actual_iteration_keys):
            missing_markers.append(f"bench_expectations:missing_iteration={key}")

    checksums = expectations.get("checksums")
    if not isinstance(checksums, list):
        missing_markers.append("bench_expectations:checksums=list")
    else:
        actual_checksums: list[str] = []
        seen: set[str] = set()
        duplicates: list[str] = []
        for item in checksums:
            if not isinstance(item, str):
                missing_markers.append("bench_expectations:checksum_type=str")
                continue
            actual_checksums.append(item)
            if item in seen and item not in duplicates:
                duplicates.append(item)
            seen.add(item)
        for item in duplicates:
            missing_markers.append(f"bench_expectations:duplicate_checksum={item}")
        expected_checksums = set(EXPECTED_BENCH_CHECKSUMS)
        actual_checksum_set = set(actual_checksums)
        for item in sorted(expected_checksums - actual_checksum_set):
            missing_markers.append(f"bench_expectations:missing_checksum={item}")
        for item in sorted(actual_checksum_set - expected_checksums):
            missing_markers.append(f"bench_expectations:unexpected_checksum={item}")

    return missing_markers


def load_json_file(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [
            f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ]


def collect_exact_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    missing_markers: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing_markers.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return missing_markers


def collect_exact_line_count_markers(text: str, markers: list[tuple[str, str, int]]) -> list[str]:
    actual_counts: dict[str, int] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        actual_counts[line] = actual_counts.get(line, 0) + 1

    missing_markers: list[str] = []
    for label, marker, expected_count in markers:
        actual_count = actual_counts.get(marker, 0)
        if actual_count != expected_count:
            missing_markers.append(f"{label}:expected={expected_count}:actual={actual_count}")
    return missing_markers


def extract_workflow_job(text: str, job_name: str) -> str:
    pattern = re.compile(
        rf"(?ms)^  {re.escape(job_name)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)"
    )
    match = pattern.search(text)
    if match is None:
        return ""
    return match.group(0)


def collect_workflow_markers(text: str) -> list[str]:
    missing_markers: list[str] = []
    for marker in required_workflow_markers:
        if marker not in text:
            missing_markers.append(f"workflow:{marker}")
    if WORKFLOW_INSTALL_ZIG_RE.search(text) is None:
        missing_markers.append(
            "workflow:python3 scripts/zigux/install-zig.py --channel <explicit> --dest .zig-toolchain"
        )
    if "mlugg/setup-zig@" in text:
        missing_markers.append("workflow:remove mlugg/setup-zig@")
    return missing_markers


def render_marker_fixture(markers: list[tuple[str, str, int]]) -> str:
    return "\n".join(marker for _, marker, _ in markers) + "\n"


def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        fixture_path = tmp_root / rel
        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_text("// fixture\n", encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_closure_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        for rel in EXPECTED_HELPERS:
            path = tmp_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// fixture\n", encoding="utf-8")

        valid_manifest = {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS,
        }
        duplicate_manifest = {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS[:-1] + [EXPECTED_HELPERS[0]],
        }
        unexpected_helper = "tools/lib/not_phase1.zig"
        unexpected_path = tmp_root / unexpected_helper
        unexpected_path.parent.mkdir(parents=True, exist_ok=True)
        unexpected_path.write_text("// out of scope fixture\n", encoding="utf-8")
        unexpected_manifest = {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": len(EXPECTED_HELPERS) + 1,
            "helpers": EXPECTED_HELPERS[:-1] + [unexpected_helper],
        }
        valid_bench_expectations = {
            "status": "pass",
            "iterations": dict(EXPECTED_BENCH_ITERATIONS),
            "checksums": list(EXPECTED_BENCH_CHECKSUMS),
        }
        missing_bench_iteration = {
            "status": "pass",
            "iterations": {
                key: value
                for key, value in EXPECTED_BENCH_ITERATIONS.items()
                if key != "PHASE1_BENCH_STRING_ITERATIONS"
            },
            "checksums": list(EXPECTED_BENCH_CHECKSUMS),
        }
        wrong_bench_iteration = {
            "status": "pass",
            "iterations": dict(EXPECTED_BENCH_ITERATIONS),
            "checksums": list(EXPECTED_BENCH_CHECKSUMS),
        }
        wrong_bench_iteration["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"] = 4096
        duplicate_bench_checksum = {
            "status": "pass",
            "iterations": dict(EXPECTED_BENCH_ITERATIONS),
            "checksums": list(EXPECTED_BENCH_CHECKSUMS[:-1]) + [EXPECTED_BENCH_CHECKSUMS[0]],
        }
        unexpected_bench_checksum = {
            "status": "pass",
            "iterations": dict(EXPECTED_BENCH_ITERATIONS),
            "checksums": list(EXPECTED_BENCH_CHECKSUMS) + ["PHASE1_BENCH_FAKE_CHECKSUM"],
        }
        malformed_manifest_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"
        malformed_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        malformed_manifest_path.write_text('{"phase": "Phase 1",\n', encoding="utf-8")
        malformed_bench_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"
        malformed_bench_path.parent.mkdir(parents=True, exist_ok=True)
        malformed_bench_path.write_text('{"status": "pass",\n', encoding="utf-8")

        assert collect_manifest_markers(valid_manifest, tmp_root) == []
        duplicate_markers = collect_manifest_markers(duplicate_manifest, tmp_root)
        assert f"manifest:duplicate_helper={EXPECTED_HELPERS[0]}" in duplicate_markers
        assert f"manifest:missing_helper={EXPECTED_HELPERS[-1]}" in duplicate_markers
        unexpected_markers = collect_manifest_markers(unexpected_manifest, tmp_root)
        assert f"manifest:helper_count={len(EXPECTED_HELPERS)}" in unexpected_markers
        assert f"manifest:missing_helper={EXPECTED_HELPERS[-1]}" in unexpected_markers
        assert f"manifest:unexpected_helper={unexpected_helper}" in unexpected_markers

        assert collect_bench_expectation_markers(valid_bench_expectations) == []
        assert (
            "bench_expectations:missing_iteration=PHASE1_BENCH_STRING_ITERATIONS"
            in collect_bench_expectation_markers(missing_bench_iteration)
        )
        assert (
            "bench_expectations:iteration_value=PHASE1_BENCH_RBTREE_ITERATIONS:4000"
            in collect_bench_expectation_markers(wrong_bench_iteration)
        )
        duplicate_bench_markers = collect_bench_expectation_markers(duplicate_bench_checksum)
        assert (
            "bench_expectations:duplicate_checksum=PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM"
            in duplicate_bench_markers
        )
        assert (
            "bench_expectations:missing_checksum=PHASE1_BENCH_RBTREE_CHECKSUM"
            in duplicate_bench_markers
        )
        assert (
            "bench_expectations:unexpected_checksum=PHASE1_BENCH_FAKE_CHECKSUM"
            in collect_bench_expectation_markers(unexpected_bench_checksum)
        )

        _, malformed_manifest_markers = load_json_file(malformed_manifest_path, "manifest")
        assert any(marker.startswith("manifest:json_decode_error:") for marker in malformed_manifest_markers)
        _, malformed_bench_markers = load_json_file(malformed_bench_path, "bench_expectations")
        assert any(marker.startswith("bench_expectations:json_decode_error:") for marker in malformed_bench_markers)

        valid_closure = render_marker_fixture(required_closure_markers)
        assert collect_exact_count_markers(valid_closure, required_closure_markers) == []

        duplicate_closure_status = valid_closure + "PHASE1_STATUS=closed\n"
        duplicate_closure_markers = collect_exact_count_markers(
            duplicate_closure_status,
            required_closure_markers,
        )
        assert "closure_status_count:expected=1:actual=2" in duplicate_closure_markers

        missing_closure_gate = valid_closure.replace(
            "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py\n",
            "",
            1,
        )
        missing_closure_gate_markers = collect_exact_count_markers(
            missing_closure_gate,
            required_closure_markers,
        )
        assert "closure_closure_gate_count:expected=1:actual=0" in missing_closure_gate_markers

        missing_closure_workflow = valid_closure.replace(
            "- `.github/workflows/zigux-bootstrap.yml`\n",
            "",
            1,
        )
        missing_closure_workflow_markers = collect_exact_count_markers(
            missing_closure_workflow,
            required_closure_markers,
        )
        assert "closure_shared_review_workflow_count:expected=1:actual=0" in missing_closure_workflow_markers

        missing_find_bit_single_word_review = valid_closure.replace(
            "PHASE1_FIND_BIT_SINGLE_WORD_REVIEW=helper-local single-word next-scan proof stays explicit through the direct find_bit test anchor because the shared Phase 1 parity fixture does not isolate same-word start-mask behavior\n",
            "",
            1,
        )
        missing_find_bit_single_word_review_markers = collect_exact_count_markers(
            missing_find_bit_single_word_review,
            required_closure_markers,
        )
        assert (
            "closure_find_bit_single_word_review_count:expected=1:actual=0"
            in missing_find_bit_single_word_review_markers
        )

        missing_find_bit_inclusive_boundary_review = valid_closure.replace(
            "PHASE1_FIND_BIT_INCLUSIVE_BOUNDARY_REVIEW=helper-local inclusive boundary proof stays explicit through the direct find_bit test anchor so same-word next scans keep the last in-range head-word bit reachable from an inclusive start\n",
            "",
            1,
        )
        missing_find_bit_inclusive_boundary_review_markers = collect_exact_count_markers(
            missing_find_bit_inclusive_boundary_review,
            required_closure_markers,
        )
        assert (
            "closure_find_bit_inclusive_boundary_review_count:expected=1:actual=0"
            in missing_find_bit_inclusive_boundary_review_markers
        )

        missing_find_bit_tail_clamp_review = valid_closure.replace(
            "PHASE1_FIND_BIT_TAIL_CLAMP_REVIEW=tail_clamped_first, tail_clamped_next, tail_zero_clamped_first, tail_zero_clamped_next, tail_and_clamped_first, and tail_and_clamped_next stay explicit through the shared Phase 1 parity fixture and replay so last-word scans cannot silently leak masked tail bits beyond nbits\n",
            "",
            1,
        )
        missing_find_bit_tail_clamp_review_markers = collect_exact_count_markers(
            missing_find_bit_tail_clamp_review,
            required_closure_markers,
        )
        assert (
            "closure_find_bit_tail_clamp_review_count:expected=1:actual=0"
            in missing_find_bit_tail_clamp_review_markers
        )

        missing_bitmap_copy_alias_review = valid_closure.replace(
            "PHASE1_BITMAP_COPY_ALIAS_REVIEW=helper-local bitmap copy alias proof stays explicit through the direct bitmap test anchor so bitmap_copy_clear_tail and bitmap_copy_and_extend preserve tail masking and zero-filled extension semantics\n",
            "",
            1,
        )
        missing_bitmap_copy_alias_review_markers = collect_exact_count_markers(
            missing_bitmap_copy_alias_review,
            required_closure_markers,
        )
        assert (
            "closure_bitmap_copy_alias_review_count:expected=1:actual=0"
            in missing_bitmap_copy_alias_review_markers
        )

        missing_rbtree_review_packet = valid_closure.replace(
            "PHASE1_RBTREE_REVIEW_PACKET=helper-local rbtree tests plus the shared traversal and detached-node replay stay explicit so duplicate-search and cached-root behavior keep direct review anchors without implying a broader duplicate-search fixture packet than current master ships\n",
            "",
            1,
        )
        missing_rbtree_review_packet_markers = collect_exact_count_markers(
            missing_rbtree_review_packet,
            required_closure_markers,
        )
        assert (
            "closure_rbtree_review_packet_count:expected=1:actual=0"
            in missing_rbtree_review_packet_markers
        )

        missing_string_review_packet = valid_closure.replace(
            "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors and parity fixture keys\n",
            "",
            1,
        )
        missing_string_review_packet_markers = collect_exact_count_markers(
            missing_string_review_packet,
            required_closure_markers,
        )
        assert (
            "closure_string_review_packet_count:expected=1:actual=0"
            in missing_string_review_packet_markers
        )

        valid_phase1_workflow = render_marker_fixture(required_phase1_workflow_markers)
        assert collect_exact_count_markers(valid_phase1_workflow, required_phase1_workflow_markers) == []
        assert WORKFLOW_INSTALL_ZIG_RE.search(
            "python3 scripts/zigux/install-zig.py --channel master --dest .zig-toolchain\n"
        )
        assert WORKFLOW_INSTALL_ZIG_RE.search(
            "python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain\n"
        )
        assert WORKFLOW_INSTALL_ZIG_RE.search(
            "python3 scripts/zigux/install-zig.py --dest .zig-toolchain\n"
        ) is None

        valid_workflow = (
            "\n".join(
                required_workflow_markers
                + [
                    "python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain"
                ]
            )
            + "\n"
        )
        assert collect_workflow_markers(valid_workflow) == []
        valid_workflow_exact = "\n".join(
            [
                required_exact_workflow_markers[0][1],
                required_exact_workflow_markers[1][1],
                required_exact_workflow_markers[2][1],
                required_exact_workflow_markers[3][1],
                required_exact_workflow_markers[4][1],
            ]
        ) + "\n"
        valid_bootstrap_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in valid_workflow_exact.splitlines()
        )
        valid_phase1_bootstrap_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in valid_phase1_workflow.splitlines()
        )
        assert collect_exact_line_count_markers(valid_workflow_exact, [required_exact_workflow_markers[0]]) == []
        assert collect_exact_line_count_markers(
            valid_bootstrap_job,
            required_exact_workflow_markers[1:],
        ) == []
        assert collect_exact_line_count_markers(
            valid_phase1_bootstrap_job,
            required_phase1_workflow_markers,
        ) == []
        assert extract_workflow_job("  bootstrap:\n    run: one\n  other:\n    run: two\n", "bootstrap") == "  bootstrap:\n    run: one\n"
        assert extract_workflow_job("  bootstrap:\n    run: one\n  other:\n    run: two\n", "missing") == ""

        missing_node24_workflow = valid_workflow.replace(
            "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n",
            "",
            1,
        )
        missing_node24_markers = collect_workflow_markers(missing_node24_workflow)
        assert "workflow:FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in missing_node24_markers

        missing_workflow_install = "\n".join(required_workflow_markers) + "\n"
        missing_workflow_install_markers = collect_workflow_markers(missing_workflow_install)
        assert (
            "workflow:python3 scripts/zigux/install-zig.py --channel <explicit> --dest .zig-toolchain"
            in missing_workflow_install_markers
        )

        legacy_setup_zig_workflow = valid_workflow + "uses: mlugg/setup-zig@v1\n"
        legacy_setup_zig_markers = collect_workflow_markers(legacy_setup_zig_workflow)
        assert "workflow:remove mlugg/setup-zig@" in legacy_setup_zig_markers

        duplicate_checkout_workflow = valid_workflow_exact + "uses: actions/checkout@v6.0.2\n"
        duplicate_checkout_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in duplicate_checkout_workflow.splitlines()
        )
        duplicate_checkout_markers = collect_exact_line_count_markers(
            duplicate_checkout_job,
            required_exact_workflow_markers[1:4],
        )
        assert "workflow_checkout_count:expected=1:actual=2" in duplicate_checkout_markers

        duplicate_node24_workflow = valid_workflow_exact + "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true\n"
        duplicate_node24_markers = collect_exact_line_count_markers(
            duplicate_node24_workflow,
            [required_exact_workflow_markers[0]],
        )
        assert "workflow_node24_count:expected=1:actual=2" in duplicate_node24_markers

        duplicate_later_job = (
            "jobs:\n"
            + valid_bootstrap_job
            + "  phase2-cross:\n"
            + "    steps:\n"
            + "      - uses: actions/checkout@v6.0.2\n"
            + "      - uses: actions/setup-python@v6.2.0\n"
            + "      - run: python3 scripts/zigux/check-zig-toolchain.py\n"
        )
        duplicate_later_job_markers = collect_exact_line_count_markers(
            extract_workflow_job(duplicate_later_job, "bootstrap"),
            required_exact_workflow_markers[1:4],
        )
        assert duplicate_later_job_markers == []

        duplicate_install_workflow = (
            valid_workflow_exact
            + "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain\n"
        )
        duplicate_install_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in duplicate_install_workflow.splitlines()
        )
        duplicate_install_markers = collect_exact_line_count_markers(
            duplicate_install_job,
            [required_exact_workflow_markers[4]],
        )
        assert "workflow_install_zig_count:expected=1:actual=2" in duplicate_install_markers

        missing_phase1_validate = valid_phase1_workflow.replace(
            "run: python3 scripts/zigux/validate-phase1.py\n",
            "",
            1,
        )
        missing_phase1_validate_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in missing_phase1_validate.splitlines()
        )
        missing_phase1_validate_markers = collect_exact_line_count_markers(
            missing_phase1_validate_job,
            required_phase1_workflow_markers,
        )
        assert "workflow_phase1_validate_count:expected=1:actual=0" in missing_phase1_validate_markers

        duplicate_phase1_parity = (
            valid_phase1_workflow + "run: python3 scripts/zigux/check-phase1-parity.py\n"
        )
        duplicate_phase1_parity_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in duplicate_phase1_parity.splitlines()
        )
        duplicate_phase1_parity_markers = collect_exact_line_count_markers(
            duplicate_phase1_parity_job,
            required_phase1_workflow_markers,
        )
        assert "workflow_phase1_parity_count:expected=1:actual=2" in duplicate_phase1_parity_markers

        missing_phase1_unit_replay = valid_phase1_workflow.replace(
            "run: zig build test --build-file zigux/tests/build.zig\n",
            "",
            1,
        )
        missing_phase1_unit_replay_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in missing_phase1_unit_replay.splitlines()
        )
        missing_phase1_unit_replay_markers = collect_exact_line_count_markers(
            missing_phase1_unit_replay_job,
            required_phase1_workflow_markers,
        )
        assert "workflow_phase1_unit_replay_count:expected=1:actual=0" in missing_phase1_unit_replay_markers

        missing_phase1_bench = valid_phase1_workflow.replace(
            "run: python3 scripts/zigux/check-phase1-bench.py\n",
            "",
            1,
        )
        missing_phase1_bench_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in missing_phase1_bench.splitlines()
        )
        missing_phase1_bench_markers = collect_exact_line_count_markers(
            missing_phase1_bench_job,
            required_phase1_workflow_markers,
        )
        assert "workflow_phase1_bench_count:expected=1:actual=0" in missing_phase1_bench_markers

        missing_phase1_bench_replay = valid_phase1_workflow.replace(
            "run: zig build bench --build-file zigux/tests/build.zig -Doptimize=ReleaseSafe\n",
            "",
            1,
        )
        missing_phase1_bench_replay_job = "  bootstrap:\n" + "".join(
            f"    {line}\n" for line in missing_phase1_bench_replay.splitlines()
        )
        missing_phase1_bench_replay_markers = collect_exact_line_count_markers(
            missing_phase1_bench_replay_job,
            required_phase1_workflow_markers,
        )
        assert "workflow_phase1_bench_replay_count:expected=1:actual=0" in missing_phase1_bench_replay_markers

        valid_build = render_marker_fixture(required_build_markers)
        assert collect_exact_count_markers(valid_build, required_build_markers) == []

        duplicate_build_source = valid_build + "phase1_bench.zig\n"
        duplicate_build_markers = collect_exact_count_markers(
            duplicate_build_source,
            required_build_markers,
        )
        assert "build_phase1_bench_source_count:expected=1:actual=2" in duplicate_build_markers

        valid_makefile = render_marker_fixture(required_makefile_markers)
        assert collect_exact_count_markers(valid_makefile, required_makefile_markers) == []

        missing_validate_target = valid_makefile.replace("phase1-validate:\n", "", 1)
        missing_validate_markers = collect_exact_count_markers(missing_validate_target, required_makefile_markers)
        assert "makefile_phase1_validate_target:expected=1:actual=0" in missing_validate_markers

        missing_validate_closure = valid_makefile.replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py\n",
            "",
            1,
        )
        missing_validate_closure_markers = collect_exact_count_markers(
            missing_validate_closure,
            required_makefile_markers,
        )
        assert "makefile_phase1_validate_closure:expected=1:actual=0" in missing_validate_closure_markers

        duplicate_phase1_test_replay = (
            valid_makefile
            + "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/build.zig\n"
        )
        duplicate_phase1_test_replay_markers = collect_exact_count_markers(
            duplicate_phase1_test_replay,
            required_makefile_markers,
        )
        assert "makefile_phase1_test_replay:expected=1:actual=2" in duplicate_phase1_test_replay_markers

        missing_bench_target = valid_makefile.replace("phase1-bench:\n", "", 1)
        missing_bench_target_markers = collect_exact_count_markers(
            missing_bench_target,
            required_makefile_markers,
        )
        assert "makefile_phase1_bench_target:expected=1:actual=0" in missing_bench_target_markers

        duplicate_phase1_target = valid_makefile + "phase1: phase1-validate phase1-test phase1-bench\n"
        duplicate_phase1_markers = collect_exact_count_markers(duplicate_phase1_target, required_makefile_markers)
        assert "makefile_phase1_target:expected=1:actual=2" in duplicate_phase1_markers

        missing_bench_check = valid_makefile.replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py\n",
            "",
            1,
        )
        missing_bench_markers = collect_exact_count_markers(missing_bench_check, required_makefile_markers)
        assert "makefile_phase1_bench_check:expected=1:actual=0" in missing_bench_markers

        missing_bench_replay = valid_makefile.replace(
            "cd $(ZIGUX_ROOT) && $(ZIG) build bench --build-file zigux/tests/build.zig\n",
            "",
            1,
        )
        missing_bench_replay_markers = collect_exact_count_markers(
            missing_bench_replay,
            required_makefile_markers,
        )
        assert "makefile_phase1_bench_replay:expected=1:actual=0" in missing_bench_replay_markers

        valid_docs_root = render_marker_fixture(required_docs_root_markers)
        assert collect_exact_count_markers(valid_docs_root, required_docs_root_markers) == []
        missing_docs_root = collect_exact_count_markers("", required_docs_root_markers)
        assert "docs_root_phase1_packet:expected=1:actual=0" in missing_docs_root
        duplicate_docs_root = valid_docs_root + valid_docs_root
        duplicate_docs_root_markers = collect_exact_count_markers(
            duplicate_docs_root,
            required_docs_root_markers,
        )
        assert "docs_root_phase1_packet:expected=1:actual=2" in duplicate_docs_root_markers

        valid_scripts_readme = render_marker_fixture(required_scripts_readme_markers)
        assert collect_exact_count_markers(valid_scripts_readme, required_scripts_readme_markers) == []
        duplicate_scripts_readme = valid_scripts_readme + valid_scripts_readme
        duplicate_scripts_markers = collect_exact_count_markers(
            duplicate_scripts_readme,
            required_scripts_readme_markers,
        )
        assert "scripts_readme_phase1_packet:expected=1:actual=2" in duplicate_scripts_markers
        missing_scripts_markers = collect_exact_count_markers("", required_scripts_readme_markers)
        assert "scripts_readme_phase1_packet:expected=1:actual=0" in missing_scripts_markers

        valid_tests_readme = render_marker_fixture(required_tests_readme_markers)
        assert collect_exact_count_markers(valid_tests_readme, required_tests_readme_markers) == []
        missing_tests_markers = collect_exact_count_markers("", required_tests_readme_markers)
        assert "tests_readme_phase1_packet:expected=1:actual=0" in missing_tests_markers
        duplicate_tests_readme = valid_tests_readme + valid_tests_readme
        duplicate_tests_markers = collect_exact_count_markers(
            duplicate_tests_readme,
            required_tests_readme_markers,
        )
        assert "tests_readme_phase1_packet:expected=1:actual=2" in duplicate_tests_markers

        valid_review_checklist = render_marker_fixture(required_review_checklist_markers)
        assert collect_exact_count_markers(valid_review_checklist, required_review_checklist_markers) == []
        missing_review_checklist_markers = collect_exact_count_markers("", required_review_checklist_markers)
        assert "review_checklist_phase1_packet:expected=1:actual=0" in missing_review_checklist_markers
        duplicate_review_checklist = valid_review_checklist + valid_review_checklist
        duplicate_review_checklist_markers = collect_exact_count_markers(
            duplicate_review_checklist,
            required_review_checklist_markers,
        )
        assert "review_checklist_phase1_packet:expected=1:actual=2" in duplicate_review_checklist_markers

        valid_ledger = render_marker_fixture(required_ledger_markers)
        assert collect_exact_count_markers(valid_ledger, required_ledger_markers) == []

        duplicate_ledger = valid_ledger + "docs(zigux): close bounded phase-1 helper tranche\n"
        duplicate_ledger_markers = collect_exact_count_markers(
            duplicate_ledger,
            required_ledger_markers,
        )
        assert "ledger_phase1_closure_commit_count:expected=1:actual=2" in duplicate_ledger_markers

        make_fixture_root(tmp_root)
        assert collect_missing_files(repo_root_from_arg(str(tmp_root))) == []

        missing_workflow = ".github/workflows/zigux-bootstrap.yml"
        (tmp_root / missing_workflow).unlink()
        assert collect_missing_files(repo_root_from_arg(str(tmp_root))) == [missing_workflow]

        make_fixture_root(tmp_root)
        required_build = "zigux/tests/build.zig"
        (tmp_root / required_build).unlink()
        assert collect_missing_files(repo_root_from_arg(str(tmp_root))) == [required_build]

        make_fixture_root(tmp_root)
        required_ledger = "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"
        (tmp_root / required_ledger).unlink()
        assert collect_missing_files(repo_root_from_arg(str(tmp_root))) == [required_ledger]

        make_fixture_root(tmp_root)
        required_phase1_validator = "scripts/zigux/validate-phase1.py"
        (tmp_root / required_phase1_validator).unlink()
        assert collect_missing_files(repo_root_from_arg(str(tmp_root))) == [required_phase1_validator]

        make_fixture_root(tmp_root)
        required_phase1_parity = "scripts/zigux/check-phase1-parity.py"
        (tmp_root / required_phase1_parity).unlink()
        assert collect_missing_files(repo_root_from_arg(str(tmp_root))) == [required_phase1_parity]

    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=58")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 1 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    parser.add_argument(
        "--root",
        help="Validate an alternate Zigux tree root instead of the validator script checkout root.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing = collect_missing_files(root)
    if missing:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE1_CLOSURE_FILES_END")
        return 1

    docs_root = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
    closure = (root / "Documentation" / "zigux" / "phase1-closure.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    tests_build = (root / "zigux" / "tests" / "build.zig").read_text(encoding="utf-8")
    tests_readme = (root / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    ledger = (root / "zigux-alpha" / "BOOTSTRAP_COMMIT_LEDGER.md").read_text(encoding="utf-8")
    makefile = (root / "zigux" / "Makefile").read_text(encoding="utf-8")
    manifest, manifest_parse_markers = load_json_file(
        root / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json",
        "manifest",
    )
    bench_expectations, bench_parse_markers = load_json_file(
        root / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json",
        "bench_expectations",
    )
    bootstrap_workflow = extract_workflow_job(workflow, "bootstrap")

    missing_markers = collect_workflow_markers(workflow)
    missing_markers.extend(manifest_parse_markers)
    missing_markers.extend(bench_parse_markers)
    missing_markers.extend(
        collect_exact_line_count_markers(workflow, [required_exact_workflow_markers[0]])
    )
    missing_markers.extend(
        collect_exact_line_count_markers(bootstrap_workflow, required_exact_workflow_markers[1:])
    )

    missing_markers.extend(collect_exact_count_markers(closure, required_closure_markers))
    missing_markers.extend(collect_exact_count_markers(tests_build, required_build_markers))
    missing_markers.extend(collect_exact_count_markers(ledger, required_ledger_markers))

    if manifest is not None:
        missing_markers.extend(collect_manifest_markers(manifest, root))
    if bench_expectations is not None:
        missing_markers.extend(collect_bench_expectation_markers(bench_expectations))
    missing_markers.extend(
        collect_exact_line_count_markers(bootstrap_workflow, required_phase1_workflow_markers)
    )
    missing_markers.extend(collect_exact_count_markers(makefile, required_makefile_markers))
    missing_markers.extend(collect_exact_count_markers(docs_root, required_docs_root_markers))
    missing_markers.extend(collect_exact_count_markers(scripts_readme, required_scripts_readme_markers))
    missing_markers.extend(collect_exact_count_markers(tests_readme, required_tests_readme_markers))
    missing_markers.extend(collect_exact_count_markers(review_checklist, required_review_checklist_markers))

    if missing_markers:
        print("PHASE1_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE1_CLOSURE_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE1_CLOSURE_MARKERS_END")
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print(f"PHASE1_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(required_closure_markers) + len(required_workflow_markers) + len(required_exact_workflow_markers) + len(required_phase1_workflow_markers) + len(required_build_markers) + len(required_ledger_markers) + len(required_makefile_markers) + len(required_docs_root_markers) + len(required_scripts_readme_markers) + len(required_tests_readme_markers) + len(required_review_checklist_markers)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
