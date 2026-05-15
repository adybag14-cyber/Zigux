#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 exact perf-threshold packet."""

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
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

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
    {
        "label": "IMAP_PAD",
        "variant_name": "imap",
        "padding": True,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
    },
    {
        "label": "IMAP_NO_PAD",
        "variant_name": "imap",
        "padding": False,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
    },
]

CHECKSUM_CASES = [
    {
        "label": "64",
        "len": 64,
        "reps": 20000,
        "seed": 0,
        "max_slowdown_pct": 150,
    },
    {
        "label": "1501",
        "len": 1501,
        "reps": 4000,
        "seed": 0x1234_5678,
        "max_slowdown_pct": 150,
    },
]

HEXDUMP_CASES = [
    {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
    {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
]

REQUIRED_SNIPPETS = {
    SURVEY_PATH.as_posix(): [
        "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-base64-perf` build step again; that slowdown gate is directly reviewable from the committed tree even though the broader `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` readbacks still expose the wrapper name only through shared route inventory surfaces",
        "* base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` now pins six perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, and `zigux/tests/phase6_base64_perf.zig` keeps that same six-case helper-owned replay aligned with the committed fixture packet today",
        "* checksum shared posture: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-checksum-perf` build step again; that slowdown gate is directly reviewable from the committed tree, `zigux/Makefile` now exposes a committed `phase6-checksum-perf` target body, and only the broader bootstrap workflow plus aggregate wrapper summaries still lag the checksum packet",
        "* checksum exact thresholds: `zigux/tests/phase6_checksum_perf.zig` now keeps two helper-local slowdown cases, `64` at `reps = 20_000` and `1501` at `reps = 4_000`, each capped at `max_slowdown_pct = 150`, so the checksum perf packet is reviewable from committed evidence today even while the Linux-style wrapper inventory still lags that direct build route",
        "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
    ],
    CATALOG_PATH.as_posix(): [
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `24` direct C parity cases and preserves the dedicated slowdown packet as six case labels, `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
        "- exact current-file evidence: `lib/checksum.zig` now covers one's-complement add/subtract, block add/subtract, fold and unfold, replacement helpers, seeded `partial()` and `compute()` paths, and IPv4 plus IPv6 pseudo-header accumulation; `zigux/tests/phase6_checksum.zig` now replays fixture-backed compute parity, split-composition, seeded partials, KUnit-inspired carry discipline, random-prefix coverage, and pseudo-header cases; and `zigux/tests/phase6_checksum_perf.zig` now keeps two helper-local slowdown cases, `64` and `1501`, each capped at `max_slowdown_pct = 150` with `reps = 20_000` and `4_000`",
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "- current `master` keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`",
        "- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
        "- helper-local perf note: the dedicated perf replay now covers the shared committed payload plus the standard, URL-safe, and IMAP padded and unpadded branches under the same helper-local slowdown thresholds",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "- current `master` keeps `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- direct focused perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
        "- current review posture: parked reviewable; the checksum roadmap anchor now keeps the helper-owned replay, slowdown gate, and direct C parity scaffolding readable on current `master`, while the remaining gap has narrowed to shared route inventory truthfulness rather than a missing checksum helper packet",
    ],
    HEXDUMP_SLICE_PATH.as_posix(): [
        "- focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable",
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`",
    ],
    PHASE6_BUILD_PATH.as_posix(): [
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    ],
    MAKEFILE_PATH.as_posix(): [
        "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
        "phase6-checksum-perf:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    ],
    WORKFLOW_PATH.as_posix(): [
        "- name: Self-test Phase 6 perf-threshold checker",
        "- name: Check Phase 6 perf threshold markers",
        "- name: Run Phase 6 hexdump perf gate",
    ],
    BASE64_VECTORS_PATH.as_posix(): [
        '.{ .label = "STD_PAD", .payload = perf_payload, .padding = true, .variant_name = "std", .reference_kind = "std_padded", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "URLSAFE_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "urlsafe", .reference_kind = "urlsafe_no_pad", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_PAD", .payload = perf_payload, .padding = true, .variant_name = "imap", .reference_kind = "imap_padded", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .reference_kind = "imap_no_pad", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
    ],
    BASE64_PERF_PATH.as_posix(): [
        '.{ .label = "IMAP_PAD", .variant_name = "imap", .reference_kind = "imap_padded", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_NO_PAD", .variant_name = "imap", .reference_kind = "imap_no_pad", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
    ],
    CHECKSUM_VECTORS_PATH.as_posix(): [
        '.{ .label = "64", .len = 64, .reps = 20_000, .seed = 0, .max_slowdown_pct = 150 },',
        '.{ .label = "1501", .len = 1501, .reps = 4_000, .seed = 0x1234_5678, .max_slowdown_pct = 150 },',
    ],
    CHECKSUM_PERF_PATH.as_posix(): [
        '.{ .label = "64", .len = 64, .reps = 20_000, .seed = 0, .max_slowdown_pct = 150 },',
        '.{ .label = "1501", .len = 1501, .reps = 4_000, .seed = 0x1234_5678, .max_slowdown_pct = 150 },',
    ],
    HEXDUMP_MATRIX_PATH.as_posix(): [
        '.{ .label = "16B-plain-g1", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175, .expected_length = 47 },',
        '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550, .expected_length = 113 },',
        '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550, .expected_length = 53 },',
        '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600, .expected_length = 51 },',
    ],
}

ABSENT_WORKFLOW_SNIPPETS = [
    "- name: Run Phase 6 base64 perf gate",
    "- name: Run Phase 6 checksum perf gate",
]

EXPECTED_EXACT_CHECKS = {
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
}

EXPECTED_CHECKSUM_TESTS = {
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
}

EXPECTED_CHECKSUM_FIXTURES = {
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
}


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

    workflow_text = read_text(repo_root / WORKFLOW_PATH)
    for snippet in ABSENT_WORKFLOW_SNIPPETS:
        if snippet in workflow_text:
            raise ValidationError(f"unexpected workflow perf route in {WORKFLOW_PATH}: {snippet}")


def helper_row(manifest: dict[str, object], helper_id: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers in {MANIFEST_PATH}")
    rows = [item for item in helpers if isinstance(item, dict) and item.get("id") == helper_id]
    if len(rows) != 1:
        raise ValidationError(f"expected one {helper_id} helper row in {MANIFEST_PATH}")
    return rows[0]


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    if manifest.get("perf_posture") != EXPECTED_PERF_POSTURE:
        raise ValidationError(f"unexpected perf_posture in {MANIFEST_PATH}")

    thresholds = manifest.get("perf_thresholds")
    if not isinstance(thresholds, dict):
        raise ValidationError(f"missing perf_thresholds in {MANIFEST_PATH}")

    if thresholds.get("base64", {}).get("cases") != BASE64_CASES:
        raise ValidationError(f"unexpected base64 perf thresholds in {MANIFEST_PATH}")
    if thresholds.get("checksum", {}).get("cases") != CHECKSUM_CASES:
        raise ValidationError(f"unexpected checksum perf thresholds in {MANIFEST_PATH}")
    if thresholds.get("hexdump", {}).get("cases") != HEXDUMP_CASES:
        raise ValidationError(f"unexpected hexdump perf thresholds in {MANIFEST_PATH}")

    bsearch = thresholds.get("bsearch", {})
    if bsearch.get("typed_lookup_budget") != 4 or bsearch.get("raw_lookup_budget") != 4:
        raise ValidationError(f"unexpected bsearch perf posture in {MANIFEST_PATH}")

    checksum = helper_row(manifest, "checksum")
    if set(checksum.get("tests") or []) != EXPECTED_CHECKSUM_TESTS:
        raise ValidationError(f"unexpected checksum tests list in {MANIFEST_PATH}")
    if set(checksum.get("fixtures") or []) != EXPECTED_CHECKSUM_FIXTURES:
        raise ValidationError(f"unexpected checksum fixtures list in {MANIFEST_PATH}")
    if checksum.get("external_parity") != "scripts/zigux/check-phase6-checksum-c-parity.py":
        raise ValidationError(f"unexpected checksum external_parity in {MANIFEST_PATH}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH}")
    if not EXPECTED_EXACT_CHECKS.issubset(set(exact_checks)):
        raise ValidationError(f"missing expected exact_checks in {MANIFEST_PATH}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {MANIFEST_PATH}")
    base64 = determinism.get("base64", {})
    if base64.get("perf_replay_cases") != 6 or base64.get("transient_generated_include_committed") is not False:
        raise ValidationError(f"unexpected base64 determinism evidence in {MANIFEST_PATH}")
    if determinism.get("hexdump", {}).get("perf_replay_cases") != 4:
        raise ValidationError(f"unexpected hexdump determinism evidence in {MANIFEST_PATH}")


def validate_paths(repo_root: Path) -> None:
    required = {
        MANIFEST_PATH.as_posix(),
        SURVEY_PATH.as_posix(),
        CATALOG_PATH.as_posix(),
        BASE64_SLICE_PATH.as_posix(),
        CHECKSUM_SLICE_PATH.as_posix(),
        HEXDUMP_SLICE_PATH.as_posix(),
        BASE64_VECTORS_PATH.as_posix(),
        BASE64_PERF_PATH.as_posix(),
        CHECKSUM_VECTORS_PATH.as_posix(),
        CHECKSUM_PERF_PATH.as_posix(),
        HEXDUMP_VECTORS_PATH.as_posix(),
        HEXDUMP_MATRIX_PATH.as_posix(),
        PHASE6_BUILD_PATH.as_posix(),
        MAKEFILE_PATH.as_posix(),
        WORKFLOW_PATH.as_posix(),
    }
    for rel_path in sorted(required):
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write(root / rel_path, "\n".join(snippets) + "\n")
    write(root / HEXDUMP_VECTORS_PATH, "pub const perf_cases = .{};\n")

    manifest = {
        "perf_posture": dict(EXPECTED_PERF_POSTURE),
        "perf_thresholds": {
            "base64": {"cases": list(BASE64_CASES)},
            "checksum": {"cases": list(CHECKSUM_CASES)},
            "bsearch": {"typed_lookup_budget": 4, "raw_lookup_budget": 4},
            "hexdump": {"cases": list(HEXDUMP_CASES)},
        },
        "helpers": [
            {
                "id": "checksum",
                "tests": sorted(EXPECTED_CHECKSUM_TESTS),
                "fixtures": sorted(EXPECTED_CHECKSUM_FIXTURES),
                "external_parity": "scripts/zigux/check-phase6-checksum-c-parity.py",
            }
        ],
        "exact_checks": sorted(EXPECTED_EXACT_CHECKS),
        "determinism_evidence": {
            "base64": {"perf_replay_cases": 6, "transient_generated_include_committed": False},
            "hexdump": {"perf_replay_cases": 4},
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


def assert_unexpected_workflow_step(root: Path) -> None:
    path = root / WORKFLOW_PATH
    original = path.read_text(encoding="utf-8")
    path.write_text(original + "- name: Run Phase 6 checksum perf gate\n", encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if WORKFLOW_PATH.as_posix() not in str(exc):
            raise AssertionError(f"unexpected workflow failure: {exc}") from exc
    else:
        raise AssertionError("expected workflow absence failure")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        assert_failure(
            root,
            MANIFEST_PATH,
            '"perf_replay_cases": 6',
            '"perf_replay_cases": 5',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"reps": 4000',
            '"reps": 8000',
        )
        assert_failure(
            root,
            SURVEY_PATH,
            "`IMAP_PAD`, and `IMAP_NO_PAD`",
            "`IMAP_PAD`",
        )
        assert_failure(
            root,
            CHECKSUM_PERF_PATH,
            '.{ .label = "1501", .len = 1501, .reps = 4_000, .seed = 0x1234_5678, .max_slowdown_pct = 150 },',
            '.{ .label = "1501", .len = 1501, .reps = 8_000, .seed = 0x1234_5678, .max_slowdown_pct = 150 },',
        )
        assert_failure(
            root,
            PHASE6_BUILD_PATH,
            'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
            'const checksum_perf_step = b.step("phase6-checksum-perf-missing", "Run Phase 6 checksum perf gate");',
        )
        assert_failure(
            root,
            MAKEFILE_PATH,
            "phase6-checksum-perf:",
            "phase6-checksum-perf-missing:",
        )
        assert_failure(
            root,
            WORKFLOW_PATH,
            "- name: Run Phase 6 hexdump perf gate",
            "- name: Run Phase 6 hex gate",
        )
        assert_unexpected_workflow_step(root)
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
    print("Phase 6 perf threshold markers look aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
