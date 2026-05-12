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
LANE_PATH = Path("Documentation/zigux/phase6-leaf-helper-lane-sequencing.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HEXDUMP_SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

BASE64_PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
BSEARCH_CORPUS_SCRIPT_PATH = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
CHECKSUM_PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
HEXDUMP_PACKET_SCRIPT_PATH = Path("scripts/zigux/check-phase6-hexdump-packet.py")
PERF_THRESHOLD_SCRIPT_PATH = Path("scripts/zigux/check-phase6-perf-threshold-markers.py")
HEXDUMP_REFRESH_PATH = Path("Documentation/zigux/phase6-hexdump-perf-refresh.md")
HEXDUMP_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")

ABSENT_PATHS = [
    Path("zigux/tests/phase6_base64.zig"),
    Path("zigux/tests/phase6_base64_perf.zig"),
    Path("zigux/tests/fixtures/phase6_base64_vectors.zig"),
    Path("lib/checksum.zig"),
    Path("zigux/tests/phase6_checksum.zig"),
    Path("zigux/tests/phase6_checksum_perf.zig"),
    Path("zigux/tests/fixtures/phase6_checksum_vectors.zig"),
    Path("zigux/tests/phase6_hexdump.zig"),
    Path("zigux/tests/phase6_hexdump_perf.zig"),
    Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig"),
]

PRESENT_PATHS = [
    MANIFEST_PATH,
    CATALOG_PATH,
    PERF_SURVEY_PATH,
    LANE_PATH,
    BASE64_SLICE_PATH,
    BSEARCH_SLICE_PATH,
    CHECKSUM_SLICE_PATH,
    HEXDUMP_SLICE_PATH,
    SCRIPTS_README_PATH,
    BASE64_PARITY_SCRIPT_PATH,
    BSEARCH_CORPUS_SCRIPT_PATH,
    CHECKSUM_PARITY_SCRIPT_PATH,
    HEXDUMP_PACKET_SCRIPT_PATH,
    PERF_THRESHOLD_SCRIPT_PATH,
    HEXDUMP_REFRESH_PATH,
    HEXDUMP_MATRIX_PATH,
]

REQUIRED_SNIPPETS = {
    CATALOG_PATH.as_posix(): [
        "# Phase 6 Helper Parity Catalog",
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`",
        "- still-present direct C parity scaffolding: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
        "- currently missing helper-local replay surfaces on `master`: `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
        "- current perf-route posture: the shared perf survey above keeps the base64 and checksum slowdown routes documentary until their missing helper-owned replay files return, so the aggregate `phase6-perf` route should be read as inventory evidence rather than a truthful current-`master` replay summary",
    ],
    PERF_SURVEY_PATH.as_posix(): [
        "# Phase 6 Perf Gate Survey",
        "* aggregated route note: `make -C zigux phase6-perf` still exists as a narrow convenience wrapper for `phase6-base64-perf`, `phase6-checksum-perf`, and `phase6-hexdump-perf`, but current `master` only keeps the hexdump leg runnable from the committed tree because the base64 and checksum replay files listed below are absent",
        "* base64 shared posture: `lib/base64.zig` still ships the helper, but current `master` no longer carries `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, or `zigux/tests/fixtures/phase6_base64_vectors.zig`, even though `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still advertise `phase6-base64-perf`; that slowdown gate is currently documentary rather than runnable from the committed tree",
        "* checksum shared posture: `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, so that replay is currently not runnable from the committed tree",
        "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
        "* the convenience `make -C zigux phase6-perf` route is not a fully truthful summary of shared perf posture on `master` until the base64 and checksum helper packets are restored or the shared route is rewritten to exclude those absent slowdown gates",
    ],
    LANE_PATH.as_posix(): [
        "# Phase 6 Leaf-Helper Lane Sequencing",
        "- shared packet status source: `zigux/tests/phase6_helper_parity_manifest.json`",
        "If the checksum helper packet is absent on current `master`, split the follow-up cleanly: checksum lanes restore `lib/checksum.zig` plus the checksum-owned tests and fixtures, while `P6-Y10` owns any repo-wide route, checklist, checker, or summary retelling that stops advertising those missing files as a bundled replay.",
        "The current backlog-backed next safe step for `P6-Y10` is one shared-surface-only correction that makes the docs-root, scripts-root, tests-root, checklist, checker, build, Makefile, workflow, or manifest packet tell the same truth about the blocked checksum helper state without attempting checksum restoration in the same change; after that, route the actual helper restoration back to `P6-Y06`, `P6-L13`, or `P6-L16`.",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "# Phase 6 Base64 Slice",
        "- `PHASE6_STATUS=blocked`",
        "- current `master` still keeps `lib/base64.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
        "- current `master` lacks `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- the shipped direct C parity surface is also not currently runnable as a complete packet because `zigux/tests/phase6_base64_c_parity.zig` still imports the absent `zigux/tests/fixtures/phase6_base64_vectors.zig` fixture module",
        "- this slice is documentary only until the missing focused replay and fixture-backed perf packet return, or the direct C parity runner is rewritten to stop depending on the absent fixture module",
    ],
    BSEARCH_SLICE_PATH.as_posix(): [
        "# Phase 6 Bsearch Slice",
        "- `PHASE6_STATUS=parked`",
        "- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- focused direct C ABI equality-budget parity across typed and raw ascending and descending sorted inputs plus packed-record `member_size` ranges through `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "Current `master` also still carries `zigux/tests/fixtures/phase6_bsearch_vectors.zig` as a compact shared seed companion for the representative ascending, descending, hit-or-miss, symbol, and packed-record cases.",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "# Phase 6 Checksum Slice",
        "- `PHASE6_STATUS=blocked`",
        "- current `master` still lacks the broader checksum helper packet under `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current `master` still keeps the direct checksum C parity scaffolding under `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- stale shared routes that still point at the absent broader checksum helper packet: `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
        "- the checked-in direct C parity surface is not currently runnable as a complete packet because `zigux/tests/phase6_checksum_c_parity.zig` still imports the absent `lib/checksum.zig` helper and the absent `zigux/tests/fixtures/phase6_checksum_vectors.zig` fixture module",
        "- this slice is blocked until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state",
    ],
    HEXDUMP_SLICE_PATH.as_posix(): [
        "# Phase 6 Hexdump Slice",
        "- `PHASE6_STATUS=parked`",
        "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
        "- `make -C zigux phase6-hexdump-review`",
        "- current review posture: focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle; `16B-plain-g1` stays capped at `max_slowdown_pct = 175`, `32B-ascii-g2` and `16B-ascii-g4` stay capped at `max_slowdown_pct = 550`, and `16B-ascii-g8` stays capped at `max_slowdown_pct = 600`, with `zigux/tests/phase6_hexdump_perf_matrix.zig` exact-checking the documented case labels, lengths, row sizes, group sizes, ascii flags, replay counts, slowdown caps, and buffer-fit guard before `zigux/tests/phase6_hexdump_perf.zig` times expected output and required length for every fixture-backed perf case",
    ],
    SCRIPTS_README_PATH.as_posix(): [
        "- `check-phase6-shared-surface.py`, `check-phase6-base64-c-parity.py`, `check-phase6-bsearch-corpus-evidence.py`, `check-phase6-checksum-c-parity.py`, `check-phase6-hexdump-packet.py`, and `check-phase6-perf-threshold-markers.py` are the shipped scripts-root Phase 6 checkers on current `master`.",
        "- `make -C zigux phase6-hexdump-review` keeps the dedicated hexdump packet checker, focused helper replay, and helper-local perf gate aligned on the same Linux-style wrapper route.",
        "- `make -C zigux phase6-perf` keeps the three dedicated base64, checksum, and hexdump slowdown gates visible together while `bsearch` stays on its bounded comparison-budget evidence path instead of a separate timing route.",
    ],
    BASE64_PARITY_SCRIPT_PATH.as_posix(): [
        'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
    ],
    BSEARCH_CORPUS_SCRIPT_PATH.as_posix(): [
        '"""Fail-closed exact evidence checks for the Phase 6 bsearch corpus packet."""',
        'MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")',
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
    "base64": "partial_direct_c_parity_only",
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
    "base64 still keeps lib/base64.zig plus the direct C parity packet while its focused replay "
    "and perf files remain absent, and checksum still lacks lib/checksum.zig plus its helper-owned "
    "replay, perf, and fixture files even though shared routes and reminder surfaces still need "
    "follow-up to stop advertising that broader packet as fully runnable."
)


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

    packet_state_summary = manifest.get("packet_state_summary")
    if packet_state_summary != EXPECTED_PACKET_STATE_SUMMARY:
        raise ValidationError(
            f"Phase 6 packet_state_summary drifted in {MANIFEST_PATH}: {packet_state_summary!r}"
        )

    shared_route_note = manifest.get("shared_route_truthfulness_note")
    if shared_route_note != EXPECTED_SHARED_ROUTE_NOTE:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {MANIFEST_PATH}")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        raise ValidationError(f"missing surveyed_commit in {MANIFEST_PATH}")

    catalog_text = read_text(repo_root / CATALOG_PATH)
    if f"- surveyed head: `{surveyed_commit}`" not in catalog_text:
        raise ValidationError(
            f"catalog surveyed head does not match manifest surveyed_commit in {CATALOG_PATH}"
        )

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers list in {MANIFEST_PATH}")

    helper_map = {}
    for item in helpers:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            helper_map[item["id"]] = item

    for helper_id, slice_path in EXPECTED_HELPER_SLICE_NOTES.items():
        helper = helper_map.get(helper_id)
        if not isinstance(helper, dict):
            raise ValidationError(f"missing helper row for {helper_id} in {MANIFEST_PATH}")
        if helper.get("slice_note") != slice_path:
            raise ValidationError(
                f"unexpected slice_note for {helper_id} in {MANIFEST_PATH}: {helper.get('slice_note')!r}"
            )

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks list in {MANIFEST_PATH}")
    for command in [
        "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
        "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
        "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
        "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
        "make -C zigux phase6-hexdump-review",
    ]:
        if command not in exact_checks:
            raise ValidationError(f"missing exact Phase 6 command in {MANIFEST_PATH}: {command}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {MANIFEST_PATH}")

    base64 = determinism.get("base64")
    checksum = determinism.get("checksum")
    if not isinstance(base64, dict) or base64.get("c_parity_cases") != 24:
        raise ValidationError(f"unexpected base64 parity case count in {MANIFEST_PATH}")
    if not isinstance(checksum, dict) or checksum.get("c_parity_cases") != 22:
        raise ValidationError(f"unexpected checksum parity case count in {MANIFEST_PATH}")


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
        "exact_checks": [
            "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
            "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
            "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
            "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
            "make -C zigux phase6-hexdump-review",
        ],
        "determinism_evidence": {
            "base64": {"c_parity_cases": 24},
            "checksum": {"c_parity_cases": 22},
        },
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write(root / rel_path, "\n".join(snippets) + "\n")
    catalog_text = read_text(root / CATALOG_PATH)
    if "- surveyed head: `a0f4d7e`" not in catalog_text:
        write(root / CATALOG_PATH, catalog_text + "- surveyed head: `a0f4d7e`\n")
    write(root / HEXDUMP_REFRESH_PATH, "# Phase 6 Hexdump Perf Refresh\n\nhelper-local perf refresh note\n")
    write(root / HEXDUMP_MATRIX_PATH, 'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {}\n')


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
            '"status": "partially_blocked"',
            '"status": "active"',
        )
        assert_failure(
            root,
            CATALOG_PATH,
            "- surveyed head: `a0f4d7e`",
            "- surveyed head: `deadbeef`",
        )
        assert_failure(
            root,
            CHECKSUM_SLICE_PATH,
            "- this slice is blocked until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state",
            "- this slice is blocked until a later review",
        )
        present_should_be_absent = root / ABSENT_PATHS[0]
        write(present_should_be_absent, "unexpected\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if ABSENT_PATHS[0].as_posix() not in str(exc):
                raise AssertionError(f"unexpected absent-path failure: {exc}") from exc
        else:
            raise AssertionError("expected absent-path failure")
        present_should_be_absent.unlink()
        present_should_be_absent = root / ABSENT_PATHS[-1]
        write(present_should_be_absent, "unexpected\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if ABSENT_PATHS[-1].as_posix() not in str(exc):
                raise AssertionError(f"unexpected absent-path failure: {exc}") from exc
        else:
            raise AssertionError("expected absent-path failure")
        present_should_be_absent.unlink()
        assert_failure(
            root,
            BASE64_PARITY_SCRIPT_PATH,
            'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
            'print(f"PHASE6_BASE64_C_PARITY_COUNT={len(c_lines)}")',
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
    print("Phase 6 shared surface matches the current partially blocked packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
