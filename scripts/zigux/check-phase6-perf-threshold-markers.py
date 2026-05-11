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
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

BASE64_CASES = [
    {
        "label": "STD_PAD",
        "variant_name": "std",
        "padding": True,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
        "file_marker": '.{ .label = "STD_PAD", .variant_name = "std", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325,',
    },
    {
        "label": "STD_NO_PAD",
        "variant_name": "std",
        "padding": False,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
        "file_marker": '.{ .label = "STD_NO_PAD", .variant_name = "std", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325,',
    },
    {
        "label": "URLSAFE_PAD",
        "variant_name": "urlsafe",
        "padding": True,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
        "file_marker": '.{ .label = "URLSAFE_PAD", .variant_name = "urlsafe", .padding = true, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325,',
    },
    {
        "label": "URLSAFE_NO_PAD",
        "variant_name": "urlsafe",
        "padding": False,
        "iterations": 12000,
        "max_encode_slowdown_pct": 150,
        "max_decode_slowdown_pct": 325,
        "file_marker": '.{ .label = "URLSAFE_NO_PAD", .variant_name = "urlsafe", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325,',
    },
]

CHECKSUM_CASES = [
    {
        "label": "64B",
        "iterations": 200000,
        "max_slowdown_pct": 150,
        "file_marker": '.{ .label = "64B", .bytes = &payload_64, .iterations = 200_000, .max_slowdown_pct = 150, },',
    },
    {
        "label": "1501B",
        "iterations": 12000,
        "max_slowdown_pct": 150,
        "file_marker": '.{ .label = "1501B", .bytes = &payload_1501, .iterations = 12_000, .max_slowdown_pct = 150, },',
    },
]

SURVEY_SNIPPETS = [
    "* base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
    "* checksum exact thresholds: `zigux/tests/fixtures/phase6_checksum_vectors.zig` still pins two perf cases, `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000`, with `max_slowdown_pct = 150` for both cases",
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


def ensure_text_markers(path: Path, markers: list[str], repo_root: Path) -> None:
    content = read_text(repo_root / path)
    for marker in markers:
        if marker not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path}: {marker}")


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    perf_thresholds = manifest.get("perf_thresholds")
    if not isinstance(perf_thresholds, dict):
        raise ValidationError(f"missing perf_thresholds in {MANIFEST_PATH}")

    base64 = perf_thresholds.get("base64")
    if not isinstance(base64, dict):
        raise ValidationError(f"missing perf_thresholds.base64 in {MANIFEST_PATH}")
    if base64.get("replay") != BASE64_PERF_PATH.as_posix():
        raise ValidationError(f"unexpected base64 replay in {MANIFEST_PATH}")
    if base64.get("fixture") != "zigux/tests/fixtures/phase6_base64_vectors.zig":
        raise ValidationError(f"unexpected base64 fixture in {MANIFEST_PATH}")
    if base64.get("measurement_mode") != "relative_slowdown":
        raise ValidationError(f"unexpected base64 measurement_mode in {MANIFEST_PATH}")
    base64_cases = base64.get("cases")
    if base64_cases != [
        {
            "label": case["label"],
            "variant_name": case["variant_name"],
            "padding": case["padding"],
            "iterations": case["iterations"],
            "max_encode_slowdown_pct": case["max_encode_slowdown_pct"],
            "max_decode_slowdown_pct": case["max_decode_slowdown_pct"],
        }
        for case in BASE64_CASES
    ]:
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
    checksum_cases = checksum.get("cases")
    if checksum_cases != [
        {
            "label": case["label"],
            "iterations": case["iterations"],
            "max_slowdown_pct": case["max_slowdown_pct"],
        }
        for case in CHECKSUM_CASES
    ]:
        raise ValidationError(f"unexpected checksum cases in {MANIFEST_PATH}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH}")
    for command in [
        "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
        "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    ]:
        if command not in exact_checks:
            raise ValidationError(f"missing exact Phase 6 perf-threshold check in {MANIFEST_PATH}: {command}")


def run_checks(repo_root: Path) -> None:
    validate_manifest(repo_root)
    ensure_text_markers(SURVEY_PATH, SURVEY_SNIPPETS, repo_root)
    ensure_text_markers(BASE64_PERF_PATH, [case["file_marker"] for case in BASE64_CASES], repo_root)
    ensure_text_markers(CHECKSUM_PERF_PATH, [case["file_marker"] for case in CHECKSUM_CASES], repo_root)
    ensure_text_markers(CHECKSUM_VECTORS_PATH, [case["file_marker"] for case in CHECKSUM_CASES], repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    manifest = {
        "phase": "Phase 6",
        "tranche": "leaf-helper-parity",
        "surveyed_commit": "277b3ab",
        "helpers": [],
        "shared_gates": [],
        "perf_posture": {
            "relative_slowdown_helpers": ["base64", "checksum", "hexdump"],
            "comparison_budget_helpers": ["bsearch"],
            "timing_sanity_only_helpers": [],
        },
        "perf_thresholds": {
            "base64": {
                "replay": BASE64_PERF_PATH.as_posix(),
                "fixture": "zigux/tests/fixtures/phase6_base64_vectors.zig",
                "measurement_mode": "relative_slowdown",
                "cases": [
                    {
                        "label": case["label"],
                        "variant_name": case["variant_name"],
                        "padding": case["padding"],
                        "iterations": case["iterations"],
                        "max_encode_slowdown_pct": case["max_encode_slowdown_pct"],
                        "max_decode_slowdown_pct": case["max_decode_slowdown_pct"],
                    }
                    for case in BASE64_CASES
                ],
            },
            "bsearch": {
                "replay": "zigux/tests/phase6_bsearch.zig",
                "measurement_mode": "comparison_budget",
                "typed_lookup_budget": 4,
                "raw_lookup_budget": 4,
                "representative_typed_cases": 10,
                "representative_raw_cases": 10,
                "lower_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                "upper_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                "equality_c_abi_replay": "zigux/tests/phase6_bsearch_c_abi_budget.zig",
                "lower_bound_budget_formula": "std.math.log2_int_ceil(len) + 1",
                "upper_bound_budget_formula": "std.math.log2_int_ceil(len) + 1",
                "equality_budget_formula": "std.math.log2_int_ceil(len) + 1",
            },
            "checksum": {
                "replay": CHECKSUM_PERF_PATH.as_posix(),
                "fixture": CHECKSUM_VECTORS_PATH.as_posix(),
                "measurement_mode": "relative_slowdown",
                "cases": [
                    {
                        "label": case["label"],
                        "iterations": case["iterations"],
                        "max_slowdown_pct": case["max_slowdown_pct"],
                    }
                    for case in CHECKSUM_CASES
                ],
            },
        },
        "exact_checks": [
            "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
            "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
        ],
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write(root / SURVEY_PATH, "# Phase 6 Perf Gate Survey\n\n" + "\n".join(SURVEY_SNIPPETS) + "\n")
    write(root / BASE64_PERF_PATH, "\n".join(case["file_marker"] for case in BASE64_CASES) + "\n")
    write(root / CHECKSUM_PERF_PATH, "\n".join(case["file_marker"] for case in CHECKSUM_CASES) + "\n")
    write(root / CHECKSUM_VECTORS_PATH, "\n".join(case["file_marker"] for case in CHECKSUM_CASES) + "\n")


def assert_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
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
            '"measurement_mode": "relative_slowdown"',
            '"measurement_mode": "wall_clock"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"label": "1501B"',
            '"label": "1500B"',
        )
        assert_failure(
            root,
            SURVEY_PATH,
            "max_decode_slowdown_pct = 325",
            "max_decode_slowdown_pct = 300",
        )
        assert_failure(
            root,
            BASE64_PERF_PATH,
            '.{ .label = "URLSAFE_NO_PAD", .variant_name = "urlsafe", .padding = false, .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325,',
            '.{ .label = "URLSAFE_NO_PAD", .variant_name = "urlsafe", .padding = false, .iterations = 16000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325,',
        )
        assert_failure(
            root,
            CHECKSUM_PERF_PATH,
            '.{ .label = "64B", .bytes = &payload_64, .iterations = 200_000, .max_slowdown_pct = 150, },',
            '.{ .label = "64B", .bytes = &payload_64, .iterations = 200_000, .max_slowdown_pct = 175, },',
        )
        assert_failure(
            root,
            CHECKSUM_VECTORS_PATH,
            '.{ .label = "64B", .bytes = &payload_64, .iterations = 200_000, .max_slowdown_pct = 150, },',
            '.{ .label = "64B", .bytes = &payload_64, .iterations = 200_000, .max_slowdown_pct = 175, },',
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
    print("Phase 6 perf-threshold markers look aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
