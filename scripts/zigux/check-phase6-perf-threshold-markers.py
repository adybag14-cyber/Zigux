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
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

ABSENT_PATHS = [
    BASE64_PERF_PATH,
    BASE64_VECTORS_PATH,
    CHECKSUM_PERF_PATH,
    CHECKSUM_VECTORS_PATH,
]

PRESENT_PATHS = [
    MANIFEST_PATH,
    SURVEY_PATH,
    CATALOG_PATH,
    BASE64_SLICE_PATH,
    CHECKSUM_SLICE_PATH,
    HEXDUMP_SLICE_PATH,
    HEXDUMP_VECTORS_PATH,
]

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

EXPECTED_SHARED_NOTE = (
    "base64 still keeps lib/base64.zig plus the direct C parity packet while its focused replay "
    "and perf files remain absent, and checksum still lacks lib/checksum.zig plus its helper-owned "
    "replay, perf, and fixture files even though shared routes and reminder surfaces still need "
    "follow-up to stop advertising that broader packet as fully runnable."
)

REQUIRED_SNIPPETS = {
    SURVEY_PATH.as_posix(): [
        "* aggregated route note: `make -C zigux phase6-perf` still exists as a narrow convenience wrapper for `phase6-base64-perf`, `phase6-checksum-perf`, and `phase6-hexdump-perf`, but current `master` only keeps the hexdump leg runnable from the committed tree because the base64 and checksum replay files listed below are absent",
        "* base64 shared posture: `lib/base64.zig` still ships the helper, but current `master` no longer carries `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, or `zigux/tests/fixtures/phase6_base64_vectors.zig`, even though `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still advertise `phase6-base64-perf`; that slowdown gate is currently documentary rather than runnable from the committed tree",
        "* base64 exact thresholds: the last base64 packet documented four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, but current `master` no longer carries the base64 perf replay or fixture that would let this survey re-read those values from committed base64-owned evidence",
        "* checksum shared posture: `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, so that replay is currently not runnable from the committed tree",
        "* checksum exact thresholds: the last checksum packet documented `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`, but current `master` no longer carries the checksum perf replay or fixture that would let this survey re-read those values from committed checksum-owned evidence",
        "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
        "* the convenience `make -C zigux phase6-perf` route is not a fully truthful summary of shared perf posture on `master` until the base64 and checksum helper packets are restored or the shared route is rewritten to exclude those absent slowdown gates",
    ],
    CATALOG_PATH.as_posix(): [
        "- currently missing helper-local replay surfaces on `master`: `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- current perf-route posture: the shared perf survey above keeps the base64 and checksum slowdown routes documentary until their missing helper-owned replay files return, so the aggregate `phase6-perf` route should be read as inventory evidence rather than a truthful current-`master` replay summary",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "- `PHASE6_STATUS=blocked`",
        "- current `master` lacks `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "- this slice is documentary only until the missing focused replay and fixture-backed perf packet return, or the direct C parity runner is rewritten to stop depending on the absent fixture module",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "- `PHASE6_STATUS=blocked`",
        "- current `master` still lacks the broader checksum helper packet under `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "- this slice is blocked until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state",
    ],
    HEXDUMP_SLICE_PATH.as_posix(): [
        "- current review posture: focused helper formatting parity plus a four-case fixture-backed slowdown matrix keep the shipped hexdump packet reviewable without widening helper semantics or folding the helper-local perf route into the shared `phase6` bundle; `16B-plain-g1` stays capped at `max_slowdown_pct = 175`, `32B-ascii-g2` and `16B-ascii-g4` stay capped at `max_slowdown_pct = 550`, and `16B-ascii-g8` stays capped at `max_slowdown_pct = 600`, with `zigux/tests/phase6_hexdump_perf_matrix.zig` exact-checking the documented case labels, lengths, row sizes, group sizes, ascii flags, replay counts, slowdown caps, and buffer-fit guard before `zigux/tests/phase6_hexdump_perf.zig` times expected output and required length for every fixture-backed perf case",
    ],
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


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    if manifest.get("status") != "partially_blocked":
        raise ValidationError(f"unexpected status in {MANIFEST_PATH}: {manifest.get('status')!r}")

    if manifest.get("shared_route_truthfulness_note") != EXPECTED_SHARED_NOTE:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {MANIFEST_PATH}")

    perf_posture = manifest.get("perf_posture")
    if perf_posture != {
        "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
        "comparison_budget_helpers": ["bsearch"],
        "timing_sanity_only_helpers": [],
    }:
        raise ValidationError(f"unexpected perf_posture in {MANIFEST_PATH}")

    perf_thresholds = manifest.get("perf_thresholds")
    if not isinstance(perf_thresholds, dict):
        raise ValidationError(f"missing perf_thresholds in {MANIFEST_PATH}")

    base64 = perf_thresholds.get("base64")
    if not isinstance(base64, dict):
        raise ValidationError(f"missing perf_thresholds.base64 in {MANIFEST_PATH}")
    if base64.get("replay") != BASE64_PERF_PATH.as_posix():
        raise ValidationError(f"unexpected base64 replay in {MANIFEST_PATH}")
    if base64.get("fixture") != BASE64_VECTORS_PATH.as_posix():
        raise ValidationError(f"unexpected base64 fixture in {MANIFEST_PATH}")
    if base64.get("measurement_mode") != "relative_slowdown":
        raise ValidationError(f"unexpected base64 measurement_mode in {MANIFEST_PATH}")
    if base64.get("cases") != BASE64_CASES:
        raise ValidationError(f"unexpected base64 cases in {MANIFEST_PATH}")

    checksum = perf_thresholds.get("checksum")
    if not isinstance(checksum, dict):
        raise ValidationError(f"missing perf_thresholds.checksum in {MANIFEST_PATH}")
    if checksum.get("replay") != CHECKSUM_PERF_PATH.as_posix():
        raise ValidationError(f"unexpected checksum replay in {MANIFEST_PATH}")
    if checksum.get("fixture") != CHECKSUM_VECTORS_PATH.as_posix():
        raise ValidationError(f"unexpected checksum fixture in {MANIFEST_PATH}")
    if checksum.get("measurement_mode") != "relative_slowdown":
        raise ValidationError(f"unexpected checksum measurement_mode in {MANIFEST_PATH}")
    if checksum.get("cases") != CHECKSUM_CASES:
        raise ValidationError(f"unexpected checksum cases in {MANIFEST_PATH}")

    hexdump = perf_thresholds.get("hexdump")
    if not isinstance(hexdump, dict):
        raise ValidationError(f"missing perf_thresholds.hexdump in {MANIFEST_PATH}")
    if hexdump.get("replay") != "zigux/tests/phase6_hexdump_perf.zig":
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
    for command in [
        "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
        "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    ]:
        if command not in exact_checks:
            raise ValidationError(f"missing exact Phase 6 perf-threshold check in {MANIFEST_PATH}: {command}")


def validate_paths(repo_root: Path) -> None:
    for rel_path in PRESENT_PATHS:
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")
    for rel_path in ABSENT_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(f"Phase 6 perf path should stay absent in the current packet: {rel_path}")


def ensure_hexdump_case_markers(repo_root: Path) -> None:
    content = read_text(repo_root / HEXDUMP_VECTORS_PATH)
    for case in HEXDUMP_CASES:
        for fragment in (
            f'.label = "{case["label"]}"',
            f'.reps = {case["reps"]:_}',
            f'.max_slowdown_pct = {case["max_slowdown_pct"]}',
        ):
            if fragment not in content:
                raise ValidationError(
                    f"missing expected Phase 6 marker in {HEXDUMP_VECTORS_PATH} for {case['label']}: {fragment}"
                )


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root)
    ensure_hexdump_case_markers(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    manifest = {
        "phase": "Phase 6",
        "tranche": "leaf-helper-parity",
        "status": "partially_blocked",
        "shared_route_truthfulness_note": EXPECTED_SHARED_NOTE,
        "perf_posture": {
            "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
            "comparison_budget_helpers": ["bsearch"],
            "timing_sanity_only_helpers": [],
        },
        "perf_thresholds": {
            "base64": {
                "replay": BASE64_PERF_PATH.as_posix(),
                "fixture": BASE64_VECTORS_PATH.as_posix(),
                "measurement_mode": "relative_slowdown",
                "cases": BASE64_CASES,
            },
            "bsearch": {"measurement_mode": "comparison_budget"},
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
        "exact_checks": [
            "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
            "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
        ],
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        title = Path(rel_path).name
        write(root / rel_path, f"# {title}\n\n" + "\n".join(snippets) + "\n")
    write(
        root / HEXDUMP_VECTORS_PATH,
        "\n".join(
            f'.{{ .label = "{case["label"]}", .reps = {case["reps"]:_}, .max_slowdown_pct = {case["max_slowdown_pct"]}, }},'
            for case in HEXDUMP_CASES
        )
        + "\n",
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
            "only keeps the hexdump leg runnable",
            "keeps all three legs runnable",
        )
        assert_failure(
            root,
            CATALOG_PATH,
            "phase6-perf` route should be read as inventory evidence rather than a truthful current-`master` replay summary",
            "phase6-perf` route is a truthful current-`master` replay summary",
        )
        assert_failure(
            root,
            BASE64_SLICE_PATH,
            "this slice is documentary only until the missing focused replay and fixture-backed perf packet return, or the direct C parity runner is rewritten to stop depending on the absent fixture module",
            "this slice is fully runnable on current `master`",
        )
        assert_failure(
            root,
            CHECKSUM_SLICE_PATH,
            "this slice is blocked until the checksum helper packet is restored or the shared packet routes are rewritten to match the absent helper state",
            "this slice is now fully restored",
        )
        absent_path = root / BASE64_PERF_PATH
        write(absent_path, "unexpected\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if BASE64_PERF_PATH.as_posix() not in str(exc):
                raise AssertionError(f"unexpected absent-path failure: {exc}") from exc
        else:
            raise AssertionError("expected absent-path failure")
        absent_path.unlink()
        assert_failure(
            root,
            HEXDUMP_VECTORS_PATH,
            '.{ .label = "16B-ascii-g8", .reps = 20_000, .max_slowdown_pct = 600, },',
            '.{ .label = "16B-ascii-g8", .reps = 20_000, .max_slowdown_pct = 650, },',
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
    print("Phase 6 perf-threshold markers match the current partially blocked packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
