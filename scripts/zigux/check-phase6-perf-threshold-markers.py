#!/usr/bin/env python3
"""Fail-closed checks for the current partially blocked Phase 6 perf packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HEXDUMP_SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

PRESENT_PATHS = [
    MANIFEST_PATH,
    SURVEY_PATH,
    CATALOG_PATH,
    BASE64_SLICE_PATH,
    CHECKSUM_SLICE_PATH,
    HEXDUMP_SLICE_PATH,
    BASE64_VECTORS_PATH,
    HEXDUMP_VECTORS_PATH,
    HEXDUMP_MATRIX_PATH,
    PHASE6_BUILD_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
]

ABSENT_PATHS = [
    BASE64_PERF_PATH,
    CHECKSUM_HELPER_PATH,
    CHECKSUM_REPLAY_PATH,
    CHECKSUM_PERF_PATH,
    CHECKSUM_VECTORS_PATH,
]

EXPECTED_SHARED_ROUTE_NOTE = (
    "base64 now keeps lib/base64.zig, zigux/tests/phase6_base64.zig, and "
    "zigux/tests/fixtures/phase6_base64_vectors.zig plus the direct C parity packet "
    "while zigux/tests/phase6_base64_perf.zig remains absent, and checksum still lacks "
    "lib/checksum.zig plus its helper-owned replay, perf, and shared-vector files even "
    "though zigux/tests/phase6_checksum_c_parity.zig plus "
    "zigux/tests/fixtures/phase6_checksum_c_harness.c remain directly readable."
)

EXPECTED_PERF_POSTURE = {
    "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
    "comparison_budget_helpers": ["bsearch"],
    "timing_sanity_only_helpers": [],
}

BASE64_CASES = [
    {
        "label": "STD_PAD",
        "variant_name": "std",
        "padding": True,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
    },
    {
        "label": "STD_NO_PAD",
        "variant_name": "std",
        "padding": False,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
    },
    {
        "label": "URLSAFE_PAD",
        "variant_name": "urlsafe",
        "padding": True,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
    },
    {
        "label": "URLSAFE_NO_PAD",
        "variant_name": "urlsafe",
        "padding": False,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
    },
]

CHECKSUM_CASES = [
    {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
    {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
]

HEXDUMP_CASES = [
    {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
    {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
]

REQUIRED_SNIPPETS = {
    SURVEY_PATH.as_posix(): [
        "* shared replay note: the current Phase 6 route inventory still names `make -C zigux phase6`, `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, but the current `zigux/Makefile` readback on `master` exposed those names only in the `PHONY` inventory line and did not expose matching Phase 6 target bodies in the committed file text available to this survey",
        "* aggregated route note: `make -C zigux phase6-perf` still appears in the committed Phase 6 route inventory beside `phase6-base64-perf`, `phase6-checksum-perf`, and `phase6-hexdump-perf`, but the current survey can only treat that aggregate route as inventory evidence because the same `zigux/Makefile` readback did not expose a committed Phase 6 target body, `zigux/tests/phase6_base64_perf.zig` is still absent, and the checksum replay files listed below remain absent",
        "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` are directly readable on current `master`, and `zigux/Makefile` plus `.github/workflows/zigux-bootstrap.yml` still advertise `phase6-base64-perf`, but current `zigux/tests/phase6_build.zig` no longer defines that dedicated build step and `zigux/tests/phase6_base64_perf.zig` is still absent; that slowdown gate is currently documentary rather than runnable from the committed tree",
        "* base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, but current `master` lacks `zigux/tests/phase6_base64_perf.zig`, so this survey can re-read the helper-owned slowdown thresholds from committed evidence without claiming that the dedicated replay itself is runnable from the tree today",
        "* checksum shared posture: `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `zigux/tests/phase6_build.zig` no longer defines that dedicated build step and current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, so that replay is currently not runnable from the committed tree",
        "* checksum exact thresholds: the last checksum packet documented `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`, but current `master` no longer carries the checksum perf replay or fixture that would let this survey re-read those values from committed checksum-owned evidence",
        "* hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, and `.github/workflows/zigux-bootstrap.yml`, while the current `zigux/Makefile` readback exposes the matching route name only through the shared Phase 6 inventory line",
        "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
        "* the current bundled Phase 6 route inventory still advertises three dedicated helper-local perf gates beside the aggregate `phase6-perf` marker, but the base64 leg remains documentary because its committed perf replay file is absent and its direct `phase6_build.zig` step is gone, and the checksum leg remains documentary because its helper-local replay packet is absent and its direct `phase6_build.zig` step is gone from `master`",
    ],
    CATALOG_PATH.as_posix(): [
        "- currently missing helper-local perf replay on `master`: `zigux/tests/phase6_base64_perf.zig`",
        "- current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current perf-route posture: the shared perf survey above keeps the base64 and checksum slowdown routes documentary until their missing helper-owned replay files return, so the aggregate `phase6-perf` route should be read as inventory evidence rather than a truthful current-`master` replay summary",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "- `PHASE6_STATUS=partially_blocked`",
        "- current `master` still keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
        "- current `master` lacks `zigux/tests/phase6_base64_perf.zig`",
        "- shared route inventory still names `make -C zigux phase6-base64-perf`, but current `master` cannot honestly claim that dedicated slowdown gate until `zigux/tests/phase6_base64_perf.zig` returns",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "- `PHASE6_STATUS=blocked`",
        "- current `master` still lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current `master` still keeps `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- current review posture: blocked; the checksum roadmap anchor still belongs in the bounded Phase 6 helper packet, but current `master` only keeps the direct C parity scaffolding, and it cannot honestly claim the broader helper-local replay or slowdown gate until the missing checksum helper and fixture packet return",
    ],
    HEXDUMP_SLICE_PATH.as_posix(): [
        "- `zigux/tests/phase6_hexdump_perf.zig`",
        "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
        "- `scripts/zigux/check-phase6-hexdump-packet.py`",
        "- current review posture: focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle; `16B-plain-g1` stays capped at `max_slowdown_pct = 175`, `32B-ascii-g2` and `16B-ascii-g4` stay capped at `max_slowdown_pct = 550`, and `16B-ascii-g8` stays capped at `max_slowdown_pct = 600`, with `zigux/tests/phase6_hexdump_perf_matrix.zig` exact-checking the documented case labels, lengths, row sizes, group sizes, ascii flags, replay counts, slowdown caps, and buffer-fit guard before `zigux/tests/phase6_hexdump_perf.zig` times expected output and required length for every fixture-backed perf case",
    ],
    MAKEFILE_PATH.as_posix(): [
        "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    ],
    WORKFLOW_PATH.as_posix(): [
        "- name: Self-test Phase 6 perf-threshold checker",
        "run: python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
        "- name: Check Phase 6 perf threshold markers",
        "- name: Run Phase 6 base64 perf gate",
        "- name: Run Phase 6 checksum perf gate",
        "- name: Run Phase 6 hexdump perf gate",
    ],
}

BASE64_VECTOR_MARKERS = [
    '.{ .label = "STD_PAD",',
    '.{ .label = "STD_NO_PAD",',
    '.{ .label = "URLSAFE_PAD",',
    '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
]

HEXDUMP_MATRIX_MARKERS = [
    '.{ .label = "16B-plain-g1", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175, .expected_length = 47 },',
    '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550, .expected_length = 113 },',
    '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550, .expected_length = 53 },',
    '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600, .expected_length = 51 },',
    "if (expected_length > fixtures.test_hexdump_buf_size) return error.HexdumpPerfMatrixMismatch;",
]

REQUIRED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-hexdump-review",
]

REQUIRED_INVENTORY_ONLY_BLOCKED_ROUTES = [
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-perf",
]

ABSENT_BUILD_SNIPPETS = [
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
]

PRESENT_BUILD_SNIPPETS = [
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
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


def require_markers(path: Path, markers: list[str]) -> None:
    content = read_text(path)
    for marker in markers:
        if marker not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path}: {marker}")


def require_absent_markers(path: Path, markers: list[str]) -> None:
    content = read_text(path)
    for marker in markers:
        if marker in content:
            raise ValidationError(f"unexpected stale Phase 6 marker in {path}: {marker}")


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    if manifest.get("status") != "partially_blocked":
        raise ValidationError(f"unexpected status in {MANIFEST_PATH}: {manifest.get('status')!r}")
    if manifest.get("shared_route_truthfulness_note") != EXPECTED_SHARED_ROUTE_NOTE:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {MANIFEST_PATH}")
    if manifest.get("perf_posture") != EXPECTED_PERF_POSTURE:
        raise ValidationError(f"unexpected perf_posture in {MANIFEST_PATH}")

    perf_thresholds = manifest.get("perf_thresholds")
    if not isinstance(perf_thresholds, dict):
        raise ValidationError(f"missing perf_thresholds in {MANIFEST_PATH}")

    base64 = perf_thresholds.get("base64")
    checksum = perf_thresholds.get("checksum")
    hexdump = perf_thresholds.get("hexdump")

    if not isinstance(base64, dict) or base64.get("replay") != BASE64_PERF_PATH.as_posix():
        raise ValidationError(f"unexpected base64 replay in {MANIFEST_PATH}")
    if base64.get("fixture") != BASE64_VECTORS_PATH.as_posix():
        raise ValidationError(f"unexpected base64 fixture in {MANIFEST_PATH}")
    if base64.get("measurement_mode") != "relative_slowdown":
        raise ValidationError(f"unexpected base64 measurement_mode in {MANIFEST_PATH}")
    if base64.get("cases") != BASE64_CASES:
        raise ValidationError(f"unexpected base64 cases in {MANIFEST_PATH}")

    if not isinstance(checksum, dict) or checksum.get("replay") != CHECKSUM_PERF_PATH.as_posix():
        raise ValidationError(f"unexpected checksum replay in {MANIFEST_PATH}")
    if checksum.get("fixture") != CHECKSUM_VECTORS_PATH.as_posix():
        raise ValidationError(f"unexpected checksum fixture in {MANIFEST_PATH}")
    if checksum.get("measurement_mode") != "relative_slowdown":
        raise ValidationError(f"unexpected checksum measurement_mode in {MANIFEST_PATH}")
    if checksum.get("cases") != CHECKSUM_CASES:
        raise ValidationError(f"unexpected checksum cases in {MANIFEST_PATH}")

    if not isinstance(hexdump, dict) or hexdump.get("replay") != "zigux/tests/phase6_hexdump_perf.zig":
        raise ValidationError(f"unexpected hexdump replay in {MANIFEST_PATH}")
    if hexdump.get("fixture") != HEXDUMP_VECTORS_PATH.as_posix():
        raise ValidationError(f"unexpected hexdump fixture in {MANIFEST_PATH}")
    if hexdump.get("measurement_mode") != "relative_slowdown":
        raise ValidationError(f"unexpected hexdump measurement_mode in {MANIFEST_PATH}")
    if hexdump.get("cases") != HEXDUMP_CASES:
        raise ValidationError(f"unexpected hexdump cases in {MANIFEST_PATH}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH}")
    for command in REQUIRED_EXACT_CHECKS:
        if command not in exact_checks:
            raise ValidationError(f"missing exact perf-threshold check in {MANIFEST_PATH}: {command}")

    blocked_routes = manifest.get("inventory_only_blocked_routes")
    if not isinstance(blocked_routes, list):
        raise ValidationError(f"missing inventory_only_blocked_routes in {MANIFEST_PATH}")
    for route in REQUIRED_INVENTORY_ONLY_BLOCKED_ROUTES:
        if route not in blocked_routes:
            raise ValidationError(f"missing blocked perf route marker in {MANIFEST_PATH}: {route}")


def validate_paths(repo_root: Path) -> None:
    for rel_path in PRESENT_PATHS:
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")
    for rel_path in ABSENT_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(f"Phase 6 perf path should stay absent in the current packet: {rel_path}")


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root)
    require_markers(repo_root / BASE64_VECTORS_PATH, BASE64_VECTOR_MARKERS)
    require_markers(repo_root / HEXDUMP_MATRIX_PATH, HEXDUMP_MATRIX_MARKERS)
    require_markers(repo_root / PHASE6_BUILD_PATH, PRESENT_BUILD_SNIPPETS)
    require_absent_markers(repo_root / PHASE6_BUILD_PATH, ABSENT_BUILD_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    manifest = {
        "status": "partially_blocked",
        "shared_route_truthfulness_note": EXPECTED_SHARED_ROUTE_NOTE,
        "perf_posture": EXPECTED_PERF_POSTURE,
        "perf_thresholds": {
            "base64": {
                "replay": BASE64_PERF_PATH.as_posix(),
                "fixture": BASE64_VECTORS_PATH.as_posix(),
                "measurement_mode": "relative_slowdown",
                "cases": BASE64_CASES,
            },
            "checksum": {
                "replay": CHECKSUM_PERF_PATH.as_posix(),
                "fixture": CHECKSUM_VECTORS_PATH.as_posix(),
                "measurement_mode": "relative_slowdown",
                "cases": CHECKSUM_CASES,
            },
            "hexdump": {
                "replay": "zigux/tests/phase6_hexdump_perf.zig",
                "fixture": HEXDUMP_VECTORS_PATH.as_posix(),
                "measurement_mode": "relative_slowdown",
                "cases": HEXDUMP_CASES,
            },
        },
        "exact_checks": list(REQUIRED_EXACT_CHECKS),
        "inventory_only_blocked_routes": list(REQUIRED_INVENTORY_ONLY_BLOCKED_ROUTES),
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write(root / rel_path, "\n".join(snippets) + "\n")

    write(
        root / BASE64_VECTORS_PATH,
        "\n".join(
            [
                '.{ .label = "STD_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
                '.{ .label = "STD_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
                '.{ .label = "URLSAFE_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
                '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
            ]
        )
        + "\n",
    )
    write(root / HEXDUMP_VECTORS_PATH, "pub const perf_cases = .{};\n")
    write(root / HEXDUMP_MATRIX_PATH, "\n".join(HEXDUMP_MATRIX_MARKERS) + "\n")
    write(
        root / PHASE6_BUILD_PATH,
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");\n',
    )


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
            '"status": "parked"',
        )
        assert_failure(
            root,
            SURVEY_PATH,
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
            "`lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
            "`lib/checksum.zig`",
        )
        assert_failure(
            root,
            BASE64_VECTORS_PATH,
            '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
            '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 350 },',
        )
        assert_failure(
            root,
            HEXDUMP_MATRIX_PATH,
            '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550, .expected_length = 53 },',
            '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 2, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550, .expected_length = 53 },',
        )
        assert_failure(
            root,
            PHASE6_BUILD_PATH,
            'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
            'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
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
    print("Phase 6 perf-threshold markers match the current partially blocked packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
