#!/usr/bin/env python3
"""Guard the current Phase 6 checksum and hexdump perf-marker packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKER_PATH = Path("scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py")

REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "`zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-checksum-perf`",
    "`zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`",
    "`make -C zigux phase6-hexdump-perf`",
]

REQUIRED_CATALOG_SNIPPETS = [
    "checksum keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`",
    "- `checksum` keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`, with the committed payload threshold matrix (`64B`, `1501B`) and the `checksum.ipFastCsum` IPv4 fast-path matrix (`IPV4_20B`, `IPV4_20B_UPDATED`, `IPV4_24B`, `IPV4_60B`) still owned by `zigux/tests/fixtures/phase6_checksum_vectors.zig`; the shared replay packet exposes that packet through `zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf-matrix-test`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-perf`.",
    "hexdump keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`",
    "- `make -C zigux phase6-checksum-perf`",
    "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`",
    "- `make -C zigux phase6-hexdump-perf`",
]

REQUIRED_SURVEY_SNIPPETS = [
    "`64B` at `iterations = 200_000` with `max_slowdown_pct = 150`",
    "`1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`",
    "`IPV4_20B` with `iterations = 600_000` and `max_slowdown_pct = 100`",
    "`IPV4_20B_UPDATED` with `iterations = 600_000` and `max_slowdown_pct = 100`",
    "`IPV4_24B` with `iterations = 500_000` and `max_slowdown_pct = 100`",
    "`IPV4_60B` with `iterations = 250_000` and `max_slowdown_pct = 100`",
    "`16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`",
    "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`",
    "`16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`",
    "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf-matrix-test:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_BUILD_SNIPPETS = [
    'const checksum_perf_matrix_test_step = b.step(',
    '        "phase6-checksum-perf-matrix-test",',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
    'const hexdump_perf_matrix_test_step = b.step(',
    '        "phase6-hexdump-perf-matrix-test",',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
]

REQUIRED_CHECKSUM_PERF_SNIPPETS = [
    "try validatePerfMatrix();",
    "try validateFastPathMatrix();",
    "PHASE6_CHECKSUM_PERF_CASE_COUNT",
    "PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT",
    'std.debug.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
    'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
    'std.debug.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
    "error.ChecksumPerfRegression",
]

REQUIRED_EVIDENCE_REPLAYS = [
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]

REQUIRED_DIRECT_READBACK_COMPANION = CHECKER_PATH.as_posix()
REQUIRED_SHARED_DIRECT_EVIDENCE = [
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
REQUIRED_CHECKSUM_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]
REQUIRED_HEXDUMP_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_CHECKSUM_NO_DIRECT_COMPANION_GAPS = []
EXPECTED_HEXDUMP_NO_DIRECT_COMPANION_GAPS = []
REQUIRED_CHECKSUM_EVIDENCE_LINUX_STYLE_RERUN_ROUTES = [
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
REQUIRED_HEXDUMP_EVIDENCE_LINUX_STYLE_RERUN_ROUTES = [
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
REQUIRED_CHECKSUM_LINUX_STYLE_RERUN_ROUTES = [
    "make -C zigux phase6-checksum-perf-matrix-test",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]
REQUIRED_HEXDUMP_LINUX_STYLE_RERUN_ROUTES = [
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]
EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT = "zigux/tests/phase6_hexdump_perf_matrix.zig"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_EVIDENCE_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_CHECKSUM_CASES = {
    "64B": {"iterations": 200000, "max_slowdown_pct": 150},
    "1501B": {"iterations": 12000, "max_slowdown_pct": 150},
}
EXPECTED_CHECKSUM_IPV4_FAST_PATH_CASES = {
    "IPV4_20B": {"iterations": 600000, "max_slowdown_pct": 100},
    "IPV4_20B_UPDATED": {"iterations": 600000, "max_slowdown_pct": 100},
    "IPV4_24B": {"iterations": 500000, "max_slowdown_pct": 100},
    "IPV4_60B": {"iterations": 250000, "max_slowdown_pct": 100},
}
EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS = ["IPV4_20B", "IPV4_20B_UPDATED", "IPV4_24B", "IPV4_60B"]
EXPECTED_HEXDUMP_CASES = {
    "16B-plain-g1": {"reps": 40000, "max_slowdown_pct": 175},
    "32B-ascii-g2": {"reps": 10000, "max_slowdown_pct": 550},
    "16B-ascii-g4": {"reps": 20000, "max_slowdown_pct": 550},
    "16B-ascii-g8": {"reps": 20000, "max_slowdown_pct": 600},
}

SELF_TEST_CASE_COUNT = 78


class ValidationError(RuntimeError):
    """Raised when the Phase 6 perf packet drifts."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 perf marker in {path.as_posix()}: {snippet}"
            )


def load_manifest(path: Path) -> dict[str, object]:
    try:
        parsed = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return parsed


def get_helper(manifest: dict[str, object], key: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"manifest helpers[] missing for {key}")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper row in manifest: {key}")


def require_checker_surfaces(helper: dict[str, object], key: str, expected_surfaces: list[str]) -> None:
    checker_surfaces = helper.get("checker_surfaces")
    if not isinstance(checker_surfaces, list):
        raise ValidationError(f"{key} checker_surfaces missing")
    for surface in expected_surfaces:
        if surface not in checker_surfaces:
            raise ValidationError(f"{key} checker surface drifted: {surface}")


def validate_case_matrix(name: str, cases: object, expected: dict[str, dict[str, int]]) -> None:
    if not isinstance(cases, list):
        raise ValidationError(f"{name} perf cases missing")

    by_label: dict[str, dict[str, object]] = {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValidationError(f"{name} perf case entry is not an object")
        label = case.get("label")
        if not isinstance(label, str):
            raise ValidationError(f"{name} perf case label missing")
        if label in by_label:
            raise ValidationError(f"{name} duplicate perf case label: {label}")
        by_label[label] = case

    if set(by_label) != set(expected):
        raise ValidationError(f"{name} perf case drift: {sorted(by_label)}")

    for label, fields in expected.items():
        case = by_label[label]
        for field, value in fields.items():
            if case.get(field) != value:
                raise ValidationError(f"{name} {label} {field} drifted")


def validate_unique_routes(name: str, routes: object, required_routes: list[str]) -> None:
    if not isinstance(routes, list):
        raise ValidationError(f"{name} rerun routes missing")

    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str):
            raise ValidationError(f"{name} rerun route malformed")
        if route in seen:
            raise ValidationError(f"{name} duplicate rerun route: {route}")
        seen.add(route)

    for route in required_routes:
        if route not in routes:
            raise ValidationError(f"{name} rerun route missing {route}")


def validate_evidence_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-evidence":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("helper-evidence surveyed_head drifted")
    if manifest.get("lane_scope") != EXPECTED_EVIDENCE_LANE_SCOPE:
        raise ValidationError("helper-evidence lane_scope drifted")

    companions = manifest.get("current_direct_readback_companions")
    if not isinstance(companions, list):
        raise ValidationError("current_direct_readback_companions is missing")
    if REQUIRED_DIRECT_READBACK_COMPANION not in companions:
        raise ValidationError(f"missing direct readback companion in {path.as_posix()}: {REQUIRED_DIRECT_READBACK_COMPANION}")

    checksum = get_helper(manifest, "checksum")
    hexdump = get_helper(manifest, "hexdump")

    if checksum.get("dedicated_slowdown_replay") != "zigux/tests/phase6_checksum_perf.zig":
        raise ValidationError("checksum dedicated_slowdown_replay drifted")
    if hexdump.get("dedicated_slowdown_replay") != "zigux/tests/phase6_hexdump_perf.zig":
        raise ValidationError("hexdump dedicated_slowdown_replay drifted")
    if hexdump.get("perf_matrix_preflight") != EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT:
        raise ValidationError("hexdump evidence perf_matrix_preflight drifted")
    require_checker_surfaces(checksum, "checksum", REQUIRED_CHECKSUM_CHECKER_SURFACES)
    require_checker_surfaces(hexdump, "hexdump", REQUIRED_HEXDUMP_CHECKER_SURFACES)
    if checksum.get("still_missing_direct_companions") != EXPECTED_CHECKSUM_NO_DIRECT_COMPANION_GAPS:
        raise ValidationError("checksum evidence still_missing_direct_companions drifted")
    if hexdump.get("still_missing_direct_companions") != EXPECTED_HEXDUMP_NO_DIRECT_COMPANION_GAPS:
        raise ValidationError("hexdump evidence still_missing_direct_companions drifted")

    checksum_perf = checksum.get("current_perf_evidence")
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("checksum current_perf_evidence missing")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("hexdump current_perf_evidence missing")

    validate_case_matrix("checksum evidence", checksum_perf.get("cases"), EXPECTED_CHECKSUM_CASES)
    if checksum_perf.get("payload_case_labels") != list(EXPECTED_CHECKSUM_CASES):
        raise ValidationError("checksum evidence payload_case_labels drifted")
    validate_case_matrix("checksum evidence ipv4 fast path", checksum_perf.get("ipv4_fast_path_cases"), EXPECTED_CHECKSUM_IPV4_FAST_PATH_CASES)
    if checksum_perf.get("ipv4_fast_path_case_labels") != EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS:
        raise ValidationError("checksum evidence ipv4_fast_path_case_labels drifted")
    validate_case_matrix("hexdump evidence", hexdump_perf.get("cases"), EXPECTED_HEXDUMP_CASES)

    checksum_routes = checksum_perf.get("linux_style_rerun_routes")
    hexdump_routes = hexdump_perf.get("linux_style_rerun_routes")
    validate_unique_routes(
        "checksum evidence",
        checksum_routes,
        REQUIRED_CHECKSUM_EVIDENCE_LINUX_STYLE_RERUN_ROUTES,
    )
    validate_unique_routes(
        "hexdump evidence",
        hexdump_routes,
        REQUIRED_HEXDUMP_EVIDENCE_LINUX_STYLE_RERUN_ROUTES,
    )

    inventory = manifest.get("current_shared_replay_inventory")
    if not isinstance(inventory, list):
        raise ValidationError("current_shared_replay_inventory is missing")
    for replay in REQUIRED_EVIDENCE_REPLAYS:
        if replay not in inventory:
            raise ValidationError(f"missing shared replay inventory marker in {path.as_posix()}: {replay}")


def validate_parity_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    if manifest.get("packet") != "phase6-helper-parity":
        raise ValidationError(f"unexpected packet id in {path.as_posix()}")
    if manifest.get("phase") != "Phase 6":
        raise ValidationError(f"unexpected phase id in {path.as_posix()}")
    if manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("helper-parity surveyed_head drifted")
    if manifest.get("lane_scope") != EXPECTED_PARITY_LANE_SCOPE:
        raise ValidationError("helper-parity lane_scope drifted")

    shared_direct_evidence = manifest.get("shared_direct_evidence")
    if not isinstance(shared_direct_evidence, list):
        raise ValidationError("helper-parity shared_direct_evidence missing")
    for surface in REQUIRED_SHARED_DIRECT_EVIDENCE:
        if surface not in shared_direct_evidence:
            raise ValidationError(f"helper-parity shared_direct_evidence drifted: {surface}")

    checksum = get_helper(manifest, "checksum")
    hexdump = get_helper(manifest, "hexdump")

    if checksum.get("dedicated_slowdown_replay") != "zigux/tests/phase6_checksum_perf.zig":
        raise ValidationError("checksum parity dedicated_slowdown_replay drifted")
    if hexdump.get("dedicated_slowdown_replay") != "zigux/tests/phase6_hexdump_perf.zig":
        raise ValidationError("hexdump parity dedicated_slowdown_replay drifted")

    checksum_perf = checksum.get("current_perf_evidence")
    hexdump_perf = hexdump.get("current_perf_evidence")
    if not isinstance(checksum_perf, dict):
        raise ValidationError("checksum current_perf_evidence missing")
    if not isinstance(hexdump_perf, dict):
        raise ValidationError("hexdump current_perf_evidence missing")
    require_checker_surfaces(checksum, "checksum", REQUIRED_CHECKSUM_CHECKER_SURFACES)
    require_checker_surfaces(hexdump, "hexdump", REQUIRED_HEXDUMP_CHECKER_SURFACES)
    if checksum.get("still_missing_direct_companions") != EXPECTED_CHECKSUM_NO_DIRECT_COMPANION_GAPS:
        raise ValidationError("checksum parity still_missing_direct_companions drifted")
    if hexdump.get("still_missing_direct_companions") != EXPECTED_HEXDUMP_NO_DIRECT_COMPANION_GAPS:
        raise ValidationError("hexdump parity still_missing_direct_companions drifted")
    if hexdump.get("perf_matrix_preflight") != EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT:
        raise ValidationError("hexdump perf_matrix_preflight drifted")

    validate_case_matrix("checksum", checksum_perf.get("cases"), EXPECTED_CHECKSUM_CASES)
    if checksum_perf.get("payload_case_labels") != list(EXPECTED_CHECKSUM_CASES):
        raise ValidationError("checksum payload_case_labels drifted")
    validate_case_matrix("checksum ipv4 fast path", checksum_perf.get("ipv4_fast_path_cases"), EXPECTED_CHECKSUM_IPV4_FAST_PATH_CASES)
    if checksum_perf.get("ipv4_fast_path_case_labels") != EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS:
        raise ValidationError("checksum ipv4_fast_path_case_labels drifted")

    validate_case_matrix("hexdump", hexdump_perf.get("cases"), EXPECTED_HEXDUMP_CASES)

    checksum_routes = checksum_perf.get("linux_style_rerun_routes")
    hexdump_routes = hexdump_perf.get("linux_style_rerun_routes")
    validate_unique_routes("checksum", checksum_routes, REQUIRED_CHECKSUM_LINUX_STYLE_RERUN_ROUTES)
    validate_unique_routes("hexdump", hexdump_routes, REQUIRED_HEXDUMP_LINUX_STYLE_RERUN_ROUTES)


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(repo_root / PHASE6_BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / CHECKSUM_PERF_PATH, REQUIRED_CHECKSUM_PERF_SNIPPETS)
    validate_evidence_manifest(repo_root / EVIDENCE_MANIFEST_PATH)
    validate_parity_manifest(repo_root / PARITY_MANIFEST_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / SURVEY_PATH, "\n".join(REQUIRED_SURVEY_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / PHASE6_BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / CHECKSUM_PERF_PATH, "\n".join(REQUIRED_CHECKSUM_PERF_SNIPPETS) + "\n")
    write(root / EVIDENCE_MANIFEST_PATH, json.dumps({
        "packet": "phase6-helper-evidence",
        "phase": "Phase 6",
        "surveyed_head": EXPECTED_SURVEYED_HEAD,
        "lane_scope": EXPECTED_EVIDENCE_LANE_SCOPE,
        "current_direct_readback_companions": [REQUIRED_DIRECT_READBACK_COMPANION],
        "helpers": [
            {"key": "checksum", "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig", "checker_surfaces": REQUIRED_CHECKSUM_CHECKER_SURFACES, "still_missing_direct_companions": EXPECTED_CHECKSUM_NO_DIRECT_COMPANION_GAPS, "current_perf_evidence": {"cases": [{"label": "64B", "iterations": 200000, "max_slowdown_pct": 150}, {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150}], "payload_case_labels": ["64B", "1501B"], "ipv4_fast_path_cases": [{"label": "IPV4_20B", "iterations": 600000, "max_slowdown_pct": 100}, {"label": "IPV4_20B_UPDATED", "iterations": 600000, "max_slowdown_pct": 100}, {"label": "IPV4_24B", "iterations": 500000, "max_slowdown_pct": 100}, {"label": "IPV4_60B", "iterations": 250000, "max_slowdown_pct": 100}], "ipv4_fast_path_case_labels": EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS, "linux_style_rerun_routes": REQUIRED_CHECKSUM_EVIDENCE_LINUX_STYLE_RERUN_ROUTES}},
            {"key": "hexdump", "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig", "perf_matrix_preflight": EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT, "checker_surfaces": REQUIRED_HEXDUMP_CHECKER_SURFACES, "still_missing_direct_companions": EXPECTED_HEXDUMP_NO_DIRECT_COMPANION_GAPS, "current_perf_evidence": {"cases": [{"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175}, {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550}, {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550}, {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600}], "linux_style_rerun_routes": REQUIRED_HEXDUMP_EVIDENCE_LINUX_STYLE_RERUN_ROUTES}}
        ],
        "current_shared_replay_inventory": REQUIRED_EVIDENCE_REPLAYS,
    }, indent=2) + "\n")
    write(root / PARITY_MANIFEST_PATH, json.dumps({
        "packet": "phase6-helper-parity",
        "phase": "Phase 6",
        "surveyed_head": EXPECTED_SURVEYED_HEAD,
        "lane_scope": EXPECTED_PARITY_LANE_SCOPE,
        "shared_direct_evidence": REQUIRED_SHARED_DIRECT_EVIDENCE,
        "helpers": [
            {"key": "checksum", "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig", "checker_surfaces": REQUIRED_CHECKSUM_CHECKER_SURFACES, "still_missing_direct_companions": EXPECTED_CHECKSUM_NO_DIRECT_COMPANION_GAPS, "current_perf_evidence": {"cases": [{"label": "64B", "iterations": 200000, "max_slowdown_pct": 150}, {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150}], "payload_case_labels": ["64B", "1501B"], "ipv4_fast_path_cases": [{"label": "IPV4_20B", "iterations": 600000, "max_slowdown_pct": 100}, {"label": "IPV4_20B_UPDATED", "iterations": 600000, "max_slowdown_pct": 100}, {"label": "IPV4_24B", "iterations": 500000, "max_slowdown_pct": 100}, {"label": "IPV4_60B", "iterations": 250000, "max_slowdown_pct": 100}], "ipv4_fast_path_case_labels": EXPECTED_CHECKSUM_IPV4_FAST_PATH_LABELS, "linux_style_rerun_routes": ["make -C zigux phase6-checksum-perf-matrix-test", "make -C zigux phase6-checksum-perf", "make -C zigux phase6-perf"]}},
            {"key": "hexdump", "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig", "checker_surfaces": REQUIRED_HEXDUMP_CHECKER_SURFACES, "still_missing_direct_companions": EXPECTED_HEXDUMP_NO_DIRECT_COMPANION_GAPS, "perf_matrix_preflight": EXPECTED_HEXDUMP_PERF_MATRIX_PREFLIGHT, "current_perf_evidence": {"cases": [{"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175}, {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550}, {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550}, {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600}], "linux_style_rerun_routes": ["make -C zigux phase6-hexdump-review", "make -C zigux phase6-hexdump-perf-matrix-test", "make -C zigux phase6-hexdump-perf", "make -C zigux phase6-perf"]}}
        ],
    }, indent=2) + "\n")


def mutate_text(path: Path, old: str, new: str) -> None:
    content = read_text(path)
    if old not in content:
        raise AssertionError(f"self-test marker not found: {old}")
    write(path, content.replace(old, new, 1))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        cases = [
            (SCRIPTS_README_PATH, "`make -C zigux phase6-checksum-perf`", "`make -C zigux phase6-checksum-test`", "phase6-checksum-perf"),
            (CATALOG_PATH, "zigux/tests/phase6_hexdump_perf.zig", "zigux/tests/phase6_hexdump.zig", "phase6_hexdump"),
            (CATALOG_PATH, "`IPV4_20B_UPDATED`", "`IPV4_20B_STALE`", "IPV4_20B_UPDATED"),
            (CATALOG_PATH, "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`", "- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`", "check-phase6-checksum-hexdump-perf-markers.py"),
            (SURVEY_PATH, "`64B` at `iterations = 200_000` with `max_slowdown_pct = 150`", "`64B` at `iterations = 180_000` with `max_slowdown_pct = 150`", "64B"),
            (SURVEY_PATH, "`1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`", "`1501B` at `iterations = 16_000` with `max_slowdown_pct = 150`", "1501B"),
            (SURVEY_PATH, "`IPV4_20B` with `iterations = 600_000` and `max_slowdown_pct = 100`", "`IPV4_20B` with `iterations = 550_000` and `max_slowdown_pct = 100`", "IPV4_20B"),
            (SURVEY_PATH, "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`", "`16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 650`", "16B-ascii-g8"),
            (SURVEY_PATH, "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`", "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 575`", "32B-ascii-g2"),
            (MAKEFILE_PATH, "phase6-hexdump-review:", "phase6-hexdump-scan:", "phase6-hexdump-review:"),
            (MAKEFILE_PATH, "phase6-hexdump-perf:", "phase6-hexdump-test:", "phase6-hexdump-perf:"),
            (PHASE6_BUILD_PATH, 'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");', 'const checksum_perf_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper perf gate");', "phase6-checksum-perf"),
            (PHASE6_BUILD_PATH, 'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");', 'const hexdump_review_step = b.step("phase6-hexdump-scan", "Run Phase 6 hexdump perf-matrix review preflight");', "phase6-hexdump-review"),
            (PHASE6_BUILD_PATH, '        "phase6-hexdump-perf-matrix-test",', '        "phase6-hexdump-perf-test",', "phase6-hexdump-perf-matrix-test"),
            (PHASE6_BUILD_PATH, 'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");', 'const hexdump_perf_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper perf gate");', "phase6-hexdump-perf"),
            (CHECKSUM_PERF_PATH, "PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT", "PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT", "PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT"),
            (CHECKSUM_PERF_PATH, "error.ChecksumPerfRegression", "error.ChecksumPerfDrift", "error.ChecksumPerfRegression"),
            (CHECKSUM_PERF_PATH, 'std.debug.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});', 'std.debug.print("PHASE6_CHECKSUM_GATE={s}\\n", .{if (failed) "fail" else "pass"});', "PHASE6_CHECKSUM_PERF={s}"),
            (EVIDENCE_MANIFEST_PATH, '"packet": "phase6-helper-evidence"', '"packet": "phase6-helper-parity"', "unexpected packet id"),
            (EVIDENCE_MANIFEST_PATH, '"phase": "Phase 6"', '"phase": "Phase 5"', "unexpected phase id"),
            (EVIDENCE_MANIFEST_PATH, '"lane_scope": "shared helper-evidence rows and machine-readable manifest only"', '"lane_scope": "shared helper-evidence rows only"', "helper-evidence lane_scope drifted"),
            (EVIDENCE_MANIFEST_PATH, '"scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"', '"scripts/zigux/check-phase6-present-entrypoints.py"', "check-phase6-checksum-hexdump-perf-markers.py"),
            (EVIDENCE_MANIFEST_PATH, '"surveyed_head": "current-master-readback-2026-05-22"', '"surveyed_head": "current-master-readback-2026-05-21"', "helper-evidence surveyed_head drifted"),
            (EVIDENCE_MANIFEST_PATH, '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig"', '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum.zig"', "checksum dedicated_slowdown_replay drifted"),
            (EVIDENCE_MANIFEST_PATH, '"scripts/zigux/check-phase6-checksum-corpus-evidence.py"', '"scripts/zigux/check-phase6-present-entrypoints.py"', "checksum checker surface drifted"),
            (EVIDENCE_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-packet.py"', '"scripts/zigux/check-phase6-hexdump-route.py"', "hexdump checker surface drifted"),
            (EVIDENCE_MANIFEST_PATH, '"still_missing_direct_companions": []', '"still_missing_direct_companions": ["zigux/tests/phase6_checksum_c_parity.zig"]', "checksum evidence still_missing_direct_companions drifted"),
            (
                EVIDENCE_MANIFEST_PATH,
                '"key": "hexdump",\n      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",\n      "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",\n      "checker_surfaces": [\n        "scripts/zigux/check-phase6-hexdump-packet.py",\n        "scripts/zigux/check-phase6-hexdump-route.py"\n      ],\n      "still_missing_direct_companions": []',
                '"key": "hexdump",\n      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",\n      "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",\n      "checker_surfaces": [\n        "scripts/zigux/check-phase6-hexdump-packet.py",\n        "scripts/zigux/check-phase6-hexdump-route.py"\n      ],\n      "still_missing_direct_companions": ["zigux/tests/phase6_hexdump_route_refresh.zig"]',
                "hexdump evidence still_missing_direct_companions drifted",
            ),
            (EVIDENCE_MANIFEST_PATH, '"perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig"', '"perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf.zig"', "hexdump evidence perf_matrix_preflight drifted"),
            (EVIDENCE_MANIFEST_PATH, '"zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig"', '"zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig"', "checksum evidence rerun route missing zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig"),
            (EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-checksum-perf"', '"make -C zigux phase6-checksum-test"', "checksum evidence rerun route missing make -C zigux phase6-checksum-perf"),
            (EVIDENCE_MANIFEST_PATH, '"zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig"', '"zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig"', "hexdump evidence rerun route missing zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig"),
            (EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-hexdump-perf"', '"make -C zigux phase6-hexdump-test"', "hexdump evidence rerun route missing make -C zigux phase6-hexdump-perf"),
            (EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-hexdump-review"', '"make -C zigux phase6-hexdump-scan"', "phase6-hexdump-review"),
            (EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-hexdump-perf-matrix-test"', '"make -C zigux phase6-hexdump-test"', "phase6-hexdump-perf-matrix-test"),
            (EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-hexdump-perf"', '"make -C zigux phase6-hexdump-test"', "phase6-hexdump-perf"),
            (EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-perf"', '"make -C zigux phase6-perf-gate"', "phase6-perf"),
            (EVIDENCE_MANIFEST_PATH, '"python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"', '"python3 scripts/zigux/check-phase6-checksum-c-parity.py"', "check-phase6-checksum-hexdump-perf-markers.py"),
            (EVIDENCE_MANIFEST_PATH, '"label": "1501B"', '"label": "1500B"', "checksum evidence perf case drift"),
            (EVIDENCE_MANIFEST_PATH, '"iterations": 12000', '"iterations": 16000', "checksum evidence 1501B iterations drifted"),
            (EVIDENCE_MANIFEST_PATH, '"payload_case_labels": [\n          "64B",\n          "1501B"\n        ],', '"payload_case_labels": ["64B", "1500B"],', "checksum evidence payload_case_labels drifted"),
            (EVIDENCE_MANIFEST_PATH, '"label": "IPV4_60B"', '"label": "IPV4_64B"', "checksum evidence ipv4 fast path perf case drift"),
            (EVIDENCE_MANIFEST_PATH, '"ipv4_fast_path_case_labels": [\n          "IPV4_20B",\n          "IPV4_20B_UPDATED",\n          "IPV4_24B",\n          "IPV4_60B"\n        ]', '"ipv4_fast_path_case_labels": ["IPV4_20B", "IPV4_24B", "IPV4_64B"]', "checksum evidence ipv4_fast_path_case_labels drifted"),
            (EVIDENCE_MANIFEST_PATH, '"reps": 10000', '"reps": 8000', "hexdump evidence 32B-ascii-g2 reps drifted"),
            (PARITY_MANIFEST_PATH, '"packet": "phase6-helper-parity"', '"packet": "phase6-helper-evidence"', "unexpected packet id"),
            (PARITY_MANIFEST_PATH, '"phase": "Phase 6"', '"phase": "Phase 5"', "unexpected phase id"),
            (PARITY_MANIFEST_PATH, '"lane_scope": "shared helper-parity rows and machine-readable manifest only"', '"lane_scope": "shared helper-parity rows only"', "helper-parity lane_scope drifted"),
            (PARITY_MANIFEST_PATH, '"Documentation/zigux/phase6-perf-gate-survey.md"', '"Documentation/zigux/phase6-hexdump-slice.md"', "helper-parity shared_direct_evidence drifted: Documentation/zigux/phase6-perf-gate-survey.md"),
            (PARITY_MANIFEST_PATH, '"scripts/zigux/validate-phase6.py"', '"scripts/zigux/check-phase6-present-entrypoints.py"', "helper-parity shared_direct_evidence drifted: scripts/zigux/validate-phase6.py"),
            (PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"', '"scripts/zigux/check-phase6-checksum-c-parity.py"', "helper-parity shared_direct_evidence drifted: scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"),
            (PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-perf-threshold-markers.py"', '"scripts/zigux/check-phase6-base64-bsearch-perf-markers.py"', "helper-parity shared_direct_evidence drifted: scripts/zigux/check-phase6-perf-threshold-markers.py"),
            (PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-packet.py"', '"scripts/zigux/check-phase6-checksum-c-parity.py"', "helper-parity shared_direct_evidence drifted: scripts/zigux/check-phase6-hexdump-packet.py"),
            (PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-route.py"', '"scripts/zigux/check-phase6-hexdump-packet.py"', "helper-parity shared_direct_evidence drifted: scripts/zigux/check-phase6-hexdump-route.py"),
            (PARITY_MANIFEST_PATH, '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig"', '"dedicated_slowdown_replay": "zigux/tests/phase6_checksum.zig"', "checksum parity dedicated_slowdown_replay drifted"),
            (PARITY_MANIFEST_PATH, '"dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig"', '"dedicated_slowdown_replay": "zigux/tests/phase6_hexdump.zig"', "hexdump parity dedicated_slowdown_replay drifted"),
            (PARITY_MANIFEST_PATH, '"checker_surfaces": [\n        "scripts/zigux/check-phase6-checksum-corpus-evidence.py",\n        "scripts/zigux/check-phase6-checksum-c-parity.py"\n      ]', '"checker_surfaces": ["scripts/zigux/check-phase6-checksum-corpus-evidence.py"]', "checksum checker surface drifted"),
            (PARITY_MANIFEST_PATH, '"checker_surfaces": [\n        "scripts/zigux/check-phase6-hexdump-packet.py",\n        "scripts/zigux/check-phase6-hexdump-route.py"\n      ]', '"checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"]', "hexdump checker surface drifted"),
            (PARITY_MANIFEST_PATH, '"still_missing_direct_companions": []', '"still_missing_direct_companions": ["zigux/tests/phase6_checksum_c_parity.zig"]', "checksum parity still_missing_direct_companions drifted"),
            (
                PARITY_MANIFEST_PATH,
                '"key": "hexdump",\n      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",\n      "checker_surfaces": [\n        "scripts/zigux/check-phase6-hexdump-packet.py",\n        "scripts/zigux/check-phase6-hexdump-route.py"\n      ],\n      "still_missing_direct_companions": [],',
                '"key": "hexdump",\n      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",\n      "checker_surfaces": [\n        "scripts/zigux/check-phase6-hexdump-packet.py",\n        "scripts/zigux/check-phase6-hexdump-route.py"\n      ],\n      "still_missing_direct_companions": ["zigux/tests/phase6_hexdump_route_refresh.zig"],',
                "hexdump parity still_missing_direct_companions drifted",
            ),
            (PARITY_MANIFEST_PATH, '"surveyed_head": "current-master-readback-2026-05-22"', '"surveyed_head": "current-master-readback-2026-05-21"', "helper-parity surveyed_head drifted"),
            (PARITY_MANIFEST_PATH, '"label": "1501B"', '"label": "1500B"', "checksum perf case drift"),
            (PARITY_MANIFEST_PATH, '"iterations": 12000', '"iterations": 16000', "checksum 1501B iterations drifted"),
            (PARITY_MANIFEST_PATH, '"label": "IPV4_24B"', '"label": "IPV4_28B"', "checksum ipv4 fast path perf case drift"),
            (PARITY_MANIFEST_PATH, '"iterations": 500000', '"iterations": 450000', "checksum ipv4 fast path IPV4_24B iterations drifted"),
            (PARITY_MANIFEST_PATH, '"IPV4_60B"', '"IPV4_64B"', "checksum ipv4 fast path perf case drift"),
            (PARITY_MANIFEST_PATH, '"perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig"', '"perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf.zig"', "hexdump perf_matrix_preflight drifted"),
            (PARITY_MANIFEST_PATH, '"label": "32B-ascii-g2"', '"label": "32B-ascii-g4"', "hexdump perf case drift"),
            (PARITY_MANIFEST_PATH, '"reps": 10000', '"reps": 8000', "hexdump 32B-ascii-g2 reps drifted"),
            (PARITY_MANIFEST_PATH, '"max_slowdown_pct": 600', '"max_slowdown_pct": 650', "hexdump 16B-ascii-g8 max_slowdown_pct drifted"),
            (PARITY_MANIFEST_PATH, '"make -C zigux phase6-checksum-perf-matrix-test"', '"make -C zigux phase6-checksum-test"', "phase6-checksum-perf-matrix-test"),
            (PARITY_MANIFEST_PATH, '"make -C zigux phase6-checksum-perf"', '"make -C zigux phase6-checksum-test"', "phase6-checksum-perf"),
            (PARITY_MANIFEST_PATH, '"linux_style_rerun_routes": [\n          "make -C zigux phase6-checksum-perf-matrix-test",\n          "make -C zigux phase6-checksum-perf",\n          "make -C zigux phase6-perf"\n        ]', '"linux_style_rerun_routes": [\n          "make -C zigux phase6-checksum-perf-matrix-test",\n          "make -C zigux phase6-checksum-perf",\n          "make -C zigux phase6-checksum-test"\n        ]', "phase6-perf"),
            (PARITY_MANIFEST_PATH, '"make -C zigux phase6-hexdump-review"', '"make -C zigux phase6-hexdump-scan"', "phase6-hexdump-review"),
            (PARITY_MANIFEST_PATH, '"make -C zigux phase6-hexdump-perf-matrix-test"', '"make -C zigux phase6-hexdump-test"', "phase6-hexdump-perf-matrix-test"),
            (PARITY_MANIFEST_PATH, '"make -C zigux phase6-hexdump-perf"', '"make -C zigux phase6-hexdump-test"', "phase6-hexdump-perf"),
            (PARITY_MANIFEST_PATH, '"linux_style_rerun_routes": [\n          "make -C zigux phase6-hexdump-review",\n          "make -C zigux phase6-hexdump-perf-matrix-test",\n          "make -C zigux phase6-hexdump-perf",\n          "make -C zigux phase6-perf"\n        ]', '"linux_style_rerun_routes": [\n          "make -C zigux phase6-hexdump-review",\n          "make -C zigux phase6-hexdump-perf-matrix-test",\n          "make -C zigux phase6-hexdump-perf",\n          "make -C zigux phase6-hexdump-test"\n        ]', "phase6-perf"),
            (SURVEY_PATH, "`IPV4_60B` with `iterations = 250_000` and `max_slowdown_pct = 100`", "`IPV4_60B` with `iterations = 200_000` and `max_slowdown_pct = 100`", "IPV4_60B"),
            (SURVEY_PATH, "`16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`", "`16B-plain-g1` at `reps = 20_000` with `max_slowdown_pct = 175`", "16B-plain-g1"),
        ]
        for rel_path, old, new, expected in cases:
            mutate_text(root / rel_path, old, new)
            try:
                validate(root)
            except ValidationError as exc:
                if expected not in str(exc):
                    raise AssertionError(f"expected {expected!r} in {str(exc)!r}") from exc
            else:
                raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
            finally:
                scaffold_repo(root)
            cases_run += 1
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=fail: {exc}")
        return 1
    print("PHASE6_CHECKSUM_HEXDUMP_PERF_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())