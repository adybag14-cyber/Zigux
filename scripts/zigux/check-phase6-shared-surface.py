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
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HEXDUMP_SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

EXPECTED_PACKET_STATE_SUMMARY = {
    "base64": "parked_reviewable",
    "bsearch": "parked_reviewable",
    "checksum": "blocked_helper_packet_missing",
    "hexdump": "parked_reviewable",
}

EXPECTED_SHARED_ROUTE_NOTE = (
    "base64 now keeps lib/base64.zig, zigux/tests/phase6_base64.zig, "
    "zigux/tests/fixtures/phase6_base64_vectors.zig, zigux/tests/phase6_base64_perf.zig, "
    "and the direct C parity packet, while checksum still lacks lib/checksum.zig plus "
    "its helper-owned replay, perf, and shared-vector files even though "
    "zigux/tests/phase6_checksum_c_parity.zig plus "
    "zigux/tests/fixtures/phase6_checksum_c_harness.c remain directly readable."
)

EXPECTED_SHARED_GATES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-leaf-helper-lane-sequencing.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase6-shared-surface.py",
    "zigux/tests/README.md",
    "zigux/tests/phase6_build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
]

EXPECTED_PRESENT_ENTRYPOINTS = [
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
]

EXPECTED_PUBLIC_TREE_GAPS = [
    "lib/checksum.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
]

EXPECTED_TESTS_ROOT_TRUTHFULNESS_NOTE = (
    "zigux/tests/README.md should keep tests_root_present_entrypoints as the current "
    "Phase 6 tests-root evidence packet, keep the restored base64 helper-owned perf "
    "replay explicit beside the focused helper replay and shared vectors, and keep the "
    "still-missing checksum helper, focused replay, perf replay, and shared vectors "
    "explicit until those checksum-owned assets return."
)

EXPECTED_HELPER_SLICE_NOTES = {
    "base64": BASE64_SLICE_PATH.as_posix(),
    "bsearch": BSEARCH_SLICE_PATH.as_posix(),
    "checksum": CHECKSUM_SLICE_PATH.as_posix(),
    "hexdump": HEXDUMP_SLICE_PATH.as_posix(),
}

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

REQUIRED_SNIPPETS = {
    CATALOG_PATH.as_posix(): [
        "- dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_base64_perf.zig`",
        "- current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current blocked-route posture: the slice notes above keep the focused base64 helper replay, the dedicated base64 slowdown gate, the direct base64 C parity packet, and the direct checksum C parity scaffolding readable as review surfaces, but the checksum helper packet remains blocked because its helper-owned replay and slowdown packet are still incomplete on current `master`",
        "- current perf-route posture: the shared perf survey above keeps the checksum slowdown route documentary until its missing helper-owned replay files return, while the aggregate `phase6-perf` route should still be read as inventory evidence because the current `zigux/Makefile` readback exposes only the wrapper name instead of a committed target body",
    ],
    PERF_SURVEY_PATH.as_posix(): [
        "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-base64-perf` build step again; that slowdown gate is directly reviewable from the committed tree even though the broader `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` readbacks still expose the wrapper name only through shared route inventory surfaces",
        "* base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, and current `master` now keeps `zigux/tests/phase6_base64_perf.zig`, so this survey can re-read both the helper-owned slowdown thresholds and the dedicated replay from committed evidence today",
        "* checksum shared posture: `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `zigux/tests/phase6_build.zig` no longer defines that dedicated build step and current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, so that replay is currently not runnable from the committed tree",
        "* the current bundled Phase 6 route inventory still advertises three dedicated helper-local perf gates beside the aggregate `phase6-perf` marker, but only the checksum leg remains documentary because its helper-local replay packet is absent and its direct `phase6_build.zig` step is gone from `master`; the base64 leg is back to a directly readable helper-owned slowdown replay through `zigux/tests/phase6_base64_perf.zig` and the restored `phase6-base64-perf` step in `zigux/tests/phase6_build.zig`",
    ],
    TESTS_README_PATH.as_posix(): [
        "* `zigux/tests/phase6_helper_parity_manifest.json`",
        "* `Documentation/zigux/phase6-helper-parity-catalog.md`",
        "* `Documentation/zigux/phase6-perf-gate-survey.md`",
        "* `scripts/zigux/check-phase6-shared-surface.py`",
        "* `zigux/tests/phase6_base64_perf.zig`",
        "* current public-tree Phase 6 gaps: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "- `PHASE6_STATUS=reviewable`",
        "- current `master` keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`",
        "- present focused helper replay, shared vectors, and dedicated slowdown gate: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`",
        "- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "- `PHASE6_STATUS=blocked`",
        "- current `master` still lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet, but current `master` only keeps the direct C parity scaffolding, and it cannot honestly claim the broader helper-local replay or slowdown gate until the missing checksum helper and fixture packet return",
    ],
    PHASE6_BUILD_PATH.as_posix(): [
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    ],
    MAKEFILE_PATH.as_posix(): [
        "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    ],
    WORKFLOW_PATH.as_posix(): [
        "- name: Self-test Phase 6 shared-surface checker",
        "- name: Check Phase 6 shared surface",
        "- name: Self-test Phase 6 perf-threshold checker",
        "- name: Check Phase 6 perf threshold markers",
        "- name: Run Phase 6 leaf helper tests",
        "- name: Run Phase 6 base64 C parity packet",
        "- name: Run Phase 6 bsearch focused packet",
        "- name: Run Phase 6 hexdump perf gate",
    ],
}

ABSENT_BUILD_SNIPPETS = [
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
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
    build_text = read_text(repo_root / PHASE6_BUILD_PATH)
    for snippet in ABSENT_BUILD_SNIPPETS:
        if snippet in build_text:
            raise ValidationError(f"unexpected stale Phase 6 build route in {PHASE6_BUILD_PATH}: {snippet}")


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
    if manifest.get("tests_root_present_entrypoints") != EXPECTED_PRESENT_ENTRYPOINTS:
        raise ValidationError(f"unexpected tests_root_present_entrypoints in {MANIFEST_PATH}")
    if manifest.get("tests_root_public_tree_gaps") != EXPECTED_PUBLIC_TREE_GAPS:
        raise ValidationError(f"unexpected tests_root_public_tree_gaps in {MANIFEST_PATH}")
    if manifest.get("tests_root_truthfulness_note") != EXPECTED_TESTS_ROOT_TRUTHFULNESS_NOTE:
        raise ValidationError(f"unexpected tests_root_truthfulness_note in {MANIFEST_PATH}")
    if manifest.get("exact_checks") != EXPECTED_EXACT_CHECKS:
        raise ValidationError(f"unexpected exact_checks in {MANIFEST_PATH}")
    if manifest.get("inventory_only_blocked_routes") != EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES:
        raise ValidationError(f"unexpected inventory_only_blocked_routes in {MANIFEST_PATH}")

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
        item.get("id"): item
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
    if not isinstance(base64, dict) or base64.get("c_parity_cases") != 24 or base64.get("perf_replay_cases") != 4:
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
    if determinism.get("generated_fixture_artifacts_committed") is not False:
        raise ValidationError(f"unexpected generated fixture posture in {MANIFEST_PATH}")


def validate_paths(repo_root: Path) -> None:
    required = {
        CATALOG_PATH.as_posix(),
        PERF_SURVEY_PATH.as_posix(),
        TESTS_README_PATH.as_posix(),
        BASE64_SLICE_PATH.as_posix(),
        CHECKSUM_SLICE_PATH.as_posix(),
        BSEARCH_SLICE_PATH.as_posix(),
        HEXDUMP_SLICE_PATH.as_posix(),
        PHASE6_BUILD_PATH.as_posix(),
        MAKEFILE_PATH.as_posix(),
        WORKFLOW_PATH.as_posix(),
        BASE64_PERF_PATH.as_posix(),
        *EXPECTED_SHARED_GATES,
        *EXPECTED_PRESENT_ENTRYPOINTS,
    }
    for rel_path in sorted(required):
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")
    for rel_path in EXPECTED_PUBLIC_TREE_GAPS:
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
    write(root / CATALOG_PATH, "\n".join(REQUIRED_SNIPPETS[CATALOG_PATH.as_posix()] + ["- surveyed head: `test-head`", ""]))
    write(root / PERF_SURVEY_PATH, "\n".join(REQUIRED_SNIPPETS[PERF_SURVEY_PATH.as_posix()] + [""]))
    write(root / TESTS_README_PATH, "\n".join(REQUIRED_SNIPPETS[TESTS_README_PATH.as_posix()] + [""]))
    write(root / BASE64_SLICE_PATH, "\n".join(REQUIRED_SNIPPETS[BASE64_SLICE_PATH.as_posix()] + [""]))
    write(root / BSEARCH_SLICE_PATH, "# Phase 6 Bsearch Slice\n")
    write(root / CHECKSUM_SLICE_PATH, "\n".join(REQUIRED_SNIPPETS[CHECKSUM_SLICE_PATH.as_posix()] + [""]))
    write(root / HEXDUMP_SLICE_PATH, "# Phase 6 Hexdump Slice\n")
    write(root / PHASE6_BUILD_PATH, "\n".join(REQUIRED_SNIPPETS[PHASE6_BUILD_PATH.as_posix()] + [""]))
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_SNIPPETS[MAKEFILE_PATH.as_posix()] + [""]))
    write(root / WORKFLOW_PATH, "\n".join(REQUIRED_SNIPPETS[WORKFLOW_PATH.as_posix()] + [""]))

    for rel_path in EXPECTED_SHARED_GATES + EXPECTED_PRESENT_ENTRYPOINTS:
        path = root / rel_path
        if path.exists():
            continue
        write(path, "placeholder\n")

    manifest = {
        "phase": "Phase 6",
        "tranche": "leaf-helper-parity",
        "status": "partially_blocked",
        "packet_state_summary": dict(EXPECTED_PACKET_STATE_SUMMARY),
        "shared_route_truthfulness_note": EXPECTED_SHARED_ROUTE_NOTE,
        "surveyed_commit": "test-head",
        "helpers": [
            {"id": "base64", "slice_note": BASE64_SLICE_PATH.as_posix()},
            {"id": "bsearch", "slice_note": BSEARCH_SLICE_PATH.as_posix()},
            {"id": "checksum", "slice_note": CHECKSUM_SLICE_PATH.as_posix()},
            {"id": "hexdump", "slice_note": HEXDUMP_SLICE_PATH.as_posix()},
        ],
        "shared_gates": list(EXPECTED_SHARED_GATES),
        "tests_root_present_entrypoints": list(EXPECTED_PRESENT_ENTRYPOINTS),
        "tests_root_public_tree_gaps": list(EXPECTED_PUBLIC_TREE_GAPS),
        "tests_root_truthfulness_note": EXPECTED_TESTS_ROOT_TRUTHFULNESS_NOTE,
        "exact_checks": list(EXPECTED_EXACT_CHECKS),
        "inventory_only_blocked_routes": list(EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES),
        "determinism_evidence": {
            "base64": {
                "c_parity_cases": 24,
                "perf_replay_cases": 4,
                "transient_generated_include_committed": False,
            },
            "bsearch": {
                "comparison_budget_max_compare_calls": 4,
                "fixture_dynamic_case_lengths": 33,
            },
            "checksum": {"c_parity_cases": 27},
            "hexdump": {"perf_replay_cases": 4},
            "generated_fixture_artifacts_committed": False,
        },
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


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
            '"base64": "parked_reviewable"',
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
            CATALOG_PATH,
            "dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_base64_perf.zig`",
            "dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_base64.zig`",
        )
        assert_failure(
            root,
            PERF_SURVEY_PATH,
            "zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`",
            "zigux/tests/phase6_base64_perf.zig` are not directly readable on current `master`",
        )
        assert_failure(
            root,
            TESTS_README_PATH,
            "`zigux/tests/phase6_base64_perf.zig`",
            "`zigux/tests/phase6_checksum_perf.zig`",
        )
        assert_failure(
            root,
            BASE64_SLICE_PATH,
            "zigux/tests/phase6_base64_perf.zig`",
            "zigux/tests/phase6_checksum_perf.zig`",
        )
        (root / CHECKSUM_HELPER_PATH).parent.mkdir(parents=True, exist_ok=True)
        write(root / CHECKSUM_HELPER_PATH, "unexpected\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if CHECKSUM_HELPER_PATH.as_posix() not in str(exc):
                raise AssertionError(f"unexpected absent-path failure: {exc}") from exc
        else:
            raise AssertionError("expected absent-path failure")
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
