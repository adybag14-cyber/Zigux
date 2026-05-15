#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 catalog-backed shared packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
SHARED_CHECKER_PATH = Path("scripts/zigux/check-phase6-shared-surface.py")
BASE64_HELPER_PATH = Path("lib/base64.zig")
BASE64_REPLAY_PATH = Path("zigux/tests/phase6_base64.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BASE64_C_PARITY_PATH = Path("zigux/tests/phase6_base64_c_parity.zig")
BASE64_C_PARITY_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")
BASE64_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_harness.c")
BASE64_C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

EXPECTED_PACKET_STATE_SUMMARY = {
    "base64": "parked_reviewable",
    "bsearch": "parked_reviewable",
    "checksum": "parked_reviewable",
    "hexdump": "parked_reviewable",
}

EXPECTED_SHARED_ROUTE_NOTE = (
    "base64, bsearch, checksum, and hexdump now keep committed helper-local or direct "
    "review surfaces on current `master`, while the Linux-style `zigux/Makefile` "
    "inventory still advertises `phase6-base64-perf`, `phase6-checksum-perf`, "
    "`phase6-perf`, and `phase6` as wrapper names without committed target bodies "
    "and the bootstrap workflow still reruns only the shared surface checkers, the "
    "base64 C parity packet, the bsearch packet, and the hexdump perf gate."
)

REQUIRED_SHARED_GATES = {
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-checksum-slice.md",
    "scripts/zigux/check-phase6-shared-surface.py",
    "zigux/tests/phase6_build.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
}

REQUIRED_PRESENT_ENTRYPOINTS = {
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    "lib/checksum.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
}

REQUIRED_EXACT_CHECKS = {
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
}

EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES = {
    "make -C zigux phase6-base64-c-parity",
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-checksum-c-parity",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-validate",
    "make -C zigux phase6-perf",
    "make -C zigux phase6",
}

REQUIRED_CATALOG_SNIPPETS = [
    "- still-present direct C parity scaffolding: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `24` direct C parity cases and preserves the dedicated slowdown packet as six case labels, `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
    "- slice note: `Documentation/zigux/phase6-checksum-slice.md`",
    "- focused helper replay on current `master`: `zigux/tests/phase6_checksum.zig`",
    "- dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_checksum_perf.zig`",
    "- focused checksum fixture companion on current `master`: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    "- current review posture: the checksum helper-owned packet is directly readable on current `master`, while the broader shared route inventory stays partially blocked only because the Linux-style wrapper surfaces and bootstrap workflow still lag those direct checksum build routes",
    "- current blocked-route posture: the helper-local checksum replay and slowdown gate are now directly readable through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, and `zigux/tests/phase6_build.zig`, but the Linux-style wrapper inventory in `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` still treats `phase6-checksum-perf` as documentary shared-route evidence",
]

REQUIRED_BASE64_SLICE_SNIPPETS = [
    "- current `master` still keeps the direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- present direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`",
    "- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`",
]

REQUIRED_CHECKSUM_SLICE_SNIPPETS = [
    "- `PHASE6_STATUS=parked_reviewable`",
    "- current `master` keeps `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    "- direct focused perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "- route nuance note: the checksum helper-owned replay and slowdown gate are readable from the committed helper packet again, but the shared `zigux/Makefile` and workflow surfaces still need their own route-truthfulness follow-up before reviewers should treat those wrappers as equivalent packet summaries",
    "- current review posture: parked reviewable; the checksum roadmap anchor now keeps the helper-owned replay, slowdown gate, and direct C parity scaffolding readable on current `master`, while the remaining gap has narrowed to shared route inventory truthfulness rather than a missing checksum helper packet",
]

REQUIRED_BUILD_SNIPPETS = [
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
    "checksum_perf_step.dependOn(&run_checksum_perf.step);",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "- name: Self-test Phase 6 shared-surface checker",
    "- name: Check Phase 6 shared surface",
    "- name: Self-test Phase 6 checksum C parity checker",
    "- name: Run Phase 6 bsearch focused packet",
    "- name: Run Phase 6 hexdump perf gate",
]

ABSENT_WORKFLOW_SNIPPETS = [
    "- name: Run Phase 6 checksum perf gate",
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


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path}: {snippet}")


def require_absent_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet in content:
            raise ValidationError(f"unexpected stale Phase 6 marker in {path}: {snippet}")


def helper_row(manifest: dict[str, object], helper_id: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers in {MANIFEST_PATH}")
    rows = [item for item in helpers if isinstance(item, dict) and item.get("id") == helper_id]
    if len(rows) != 1:
        raise ValidationError(f"expected one {helper_id} helper row in {MANIFEST_PATH}")
    return rows[0]


def require_helper_packet(
    manifest: dict[str, object],
    helper_id: str,
    expected_tests: set[str],
    expected_fixtures: set[str],
    expected_checker_key: str | None = None,
    expected_checker_value: str | None = None,
) -> None:
    row = helper_row(manifest, helper_id)
    if set(row.get("tests") or []) != expected_tests:
        raise ValidationError(f"unexpected {helper_id} tests list in {MANIFEST_PATH}")
    if set(row.get("fixtures") or []) != expected_fixtures:
        raise ValidationError(f"unexpected {helper_id} fixtures list in {MANIFEST_PATH}")
    if expected_checker_key is not None and row.get(expected_checker_key) != expected_checker_value:
        raise ValidationError(f"unexpected {helper_id} {expected_checker_key} in {MANIFEST_PATH}")


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

    shared_gates = manifest.get("shared_gates")
    if not isinstance(shared_gates, list):
        raise ValidationError(f"missing shared_gates in {MANIFEST_PATH}")
    if not REQUIRED_SHARED_GATES.issubset(set(shared_gates)):
        raise ValidationError(f"missing required shared_gates entries in {MANIFEST_PATH}")

    present_entrypoints = manifest.get("tests_root_present_entrypoints")
    if not isinstance(present_entrypoints, list):
        raise ValidationError(f"missing tests_root_present_entrypoints in {MANIFEST_PATH}")
    if not REQUIRED_PRESENT_ENTRYPOINTS.issubset(set(present_entrypoints)):
        raise ValidationError(f"missing restored Phase 6 entrypoints in {MANIFEST_PATH}")

    public_tree_gaps = manifest.get("tests_root_public_tree_gaps")
    if public_tree_gaps != []:
        raise ValidationError(f"unexpected tests_root_public_tree_gaps in {MANIFEST_PATH}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH}")
    if not REQUIRED_EXACT_CHECKS.issubset(set(exact_checks)):
        raise ValidationError(f"missing exact_checks for the Phase 6 packet in {MANIFEST_PATH}")

    blocked_routes = manifest.get("inventory_only_blocked_routes")
    if not isinstance(blocked_routes, list):
        raise ValidationError(f"missing inventory_only_blocked_routes in {MANIFEST_PATH}")
    if set(blocked_routes) != EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES:
        raise ValidationError(f"unexpected inventory_only_blocked_routes in {MANIFEST_PATH}")

    require_helper_packet(
        manifest,
        "base64",
        {
            "zigux/tests/phase6_base64.zig",
            "zigux/tests/phase6_base64_c_parity.zig",
            "zigux/tests/phase6_base64_perf.zig",
        },
        {
            "zigux/tests/fixtures/phase6_base64_vectors.zig",
            "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
            "zigux/tests/fixtures/phase6_base64_c_harness.c",
        },
        "external_parity",
        "scripts/zigux/check-phase6-base64-c-parity.py",
    )
    require_helper_packet(
        manifest,
        "checksum",
        {
            "zigux/tests/phase6_checksum.zig",
            "zigux/tests/phase6_checksum_perf.zig",
            "zigux/tests/phase6_checksum_c_parity.zig",
        },
        {
            "zigux/tests/fixtures/phase6_checksum_vectors.zig",
            "zigux/tests/fixtures/phase6_checksum_c_harness.c",
        },
        "external_parity",
        "scripts/zigux/check-phase6-checksum-c-parity.py",
    )


def validate_paths(repo_root: Path) -> None:
    required = {
        CATALOG_PATH.as_posix(),
        BASE64_SLICE_PATH.as_posix(),
        CHECKSUM_SLICE_PATH.as_posix(),
        PHASE6_BUILD_PATH.as_posix(),
        MAKEFILE_PATH.as_posix(),
        WORKFLOW_PATH.as_posix(),
        SHARED_CHECKER_PATH.as_posix(),
        BASE64_HELPER_PATH.as_posix(),
        BASE64_REPLAY_PATH.as_posix(),
        BASE64_PERF_PATH.as_posix(),
        BASE64_VECTORS_PATH.as_posix(),
        BASE64_C_PARITY_PATH.as_posix(),
        BASE64_C_PARITY_VECTORS_PATH.as_posix(),
        BASE64_C_HARNESS_PATH.as_posix(),
        BASE64_C_PARITY_CHECKER_PATH.as_posix(),
        CHECKSUM_HELPER_PATH.as_posix(),
        CHECKSUM_REPLAY_PATH.as_posix(),
        CHECKSUM_PERF_PATH.as_posix(),
        CHECKSUM_VECTORS_PATH.as_posix(),
    }
    for rel_path in sorted(required):
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / BASE64_SLICE_PATH, REQUIRED_BASE64_SLICE_SNIPPETS)
    require_snippets(repo_root / CHECKSUM_SLICE_PATH, REQUIRED_CHECKSUM_SLICE_SNIPPETS)
    require_snippets(repo_root / PHASE6_BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(repo_root / WORKFLOW_PATH, REQUIRED_WORKFLOW_SNIPPETS)
    require_absent_snippets(repo_root / WORKFLOW_PATH, ABSENT_WORKFLOW_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path in REQUIRED_PRESENT_ENTRYPOINTS | REQUIRED_SHARED_GATES:
        write(root / rel_path, "placeholder\n")
    write(root / BASE64_HELPER_PATH, "helper\n")
    write(root / BASE64_REPLAY_PATH, "replay\n")
    write(root / BASE64_PERF_PATH, "perf\n")
    write(root / BASE64_VECTORS_PATH, "vectors\n")
    write(root / BASE64_C_PARITY_PATH, "parity\n")
    write(root / BASE64_C_PARITY_VECTORS_PATH, "parity vectors\n")
    write(root / BASE64_C_HARNESS_PATH, "harness\n")
    write(root / BASE64_C_PARITY_CHECKER_PATH, "checker\n")
    write(root / CHECKSUM_HELPER_PATH, "helper\n")
    write(root / CHECKSUM_REPLAY_PATH, "replay\n")
    write(root / CHECKSUM_PERF_PATH, "perf\n")
    write(root / CHECKSUM_VECTORS_PATH, "vectors\n")
    write(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS + ["- surveyed head: `test-head`", ""]))
    write(root / BASE64_SLICE_PATH, "\n".join(REQUIRED_BASE64_SLICE_SNIPPETS + [""]))
    write(root / CHECKSUM_SLICE_PATH, "\n".join(REQUIRED_CHECKSUM_SLICE_SNIPPETS + [""]))
    write(root / PHASE6_BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS + [""]))
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS + [""]))
    write(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_SNIPPETS + [""]))

    manifest = {
        "phase": "Phase 6",
        "tranche": "leaf-helper-parity",
        "status": "partially_blocked",
        "packet_state_summary": dict(EXPECTED_PACKET_STATE_SUMMARY),
        "shared_route_truthfulness_note": EXPECTED_SHARED_ROUTE_NOTE,
        "surveyed_commit": "test-head",
        "helpers": [
            {
                "id": "base64",
                "tests": sorted(
                    [
                        "zigux/tests/phase6_base64.zig",
                        "zigux/tests/phase6_base64_c_parity.zig",
                        "zigux/tests/phase6_base64_perf.zig",
                    ]
                ),
                "fixtures": sorted(
                    [
                        "zigux/tests/fixtures/phase6_base64_vectors.zig",
                        "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
                        "zigux/tests/fixtures/phase6_base64_c_harness.c",
                    ]
                ),
                "external_parity": "scripts/zigux/check-phase6-base64-c-parity.py",
            },
            {
                "id": "checksum",
                "tests": sorted(
                    [
                        "zigux/tests/phase6_checksum.zig",
                        "zigux/tests/phase6_checksum_perf.zig",
                        "zigux/tests/phase6_checksum_c_parity.zig",
                    ]
                ),
                "fixtures": sorted(
                    [
                        "zigux/tests/fixtures/phase6_checksum_vectors.zig",
                        "zigux/tests/fixtures/phase6_checksum_c_harness.c",
                    ]
                ),
                "external_parity": "scripts/zigux/check-phase6-checksum-c-parity.py",
            },
        ],
        "shared_gates": sorted(REQUIRED_SHARED_GATES),
        "tests_root_present_entrypoints": sorted(REQUIRED_PRESENT_ENTRYPOINTS),
        "tests_root_public_tree_gaps": [],
        "exact_checks": sorted(REQUIRED_EXACT_CHECKS),
        "inventory_only_blocked_routes": sorted(EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES),
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
            '"zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig"',
            '"zigux/tests/fixtures/phase6_base64_c_parity_vectors_missing.zig"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"tests_root_public_tree_gaps": []',
            '"tests_root_public_tree_gaps": ["lib/checksum.zig"]',
        )
        assert_failure(
            root,
            CATALOG_PATH,
            "still-present direct C parity scaffolding: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
            "still-present direct C parity scaffolding: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
        )
        assert_failure(
            root,
            BASE64_SLICE_PATH,
            "- current `master` still keeps the direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
            "- current `master` still keeps the direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
        )
        assert_failure(
            root,
            CHECKSUM_SLICE_PATH,
            "direct focused perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
            "direct focused perf route: `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`",
        )
        assert_failure(
            root,
            PHASE6_BUILD_PATH,
            'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
            'const checksum_perf_step = b.step("phase6-checksum-test", "Run Phase 6 checksum perf gate");',
        )
        assert_failure(
            root,
            WORKFLOW_PATH,
            "- name: Run Phase 6 hexdump perf gate",
            "- name: Run Phase 6 checksum perf gate",
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
    print("Phase 6 shared checker matches the current checksum and base64 shared packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
