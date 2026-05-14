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
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")

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
        "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-base64-perf` build step again; that slowdown gate is directly reviewable from the committed tree even though the broader `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` readbacks still expose the wrapper name only through shared route inventory surfaces",
        "* base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, and current `master` now keeps `zigux/tests/phase6_base64_perf.zig`, so this survey can re-read both the helper-owned slowdown thresholds and the dedicated replay from committed evidence today",
        "* checksum shared posture: `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `zigux/tests/phase6_build.zig` no longer defines that dedicated build step and current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, so that replay is currently not runnable from the committed tree",
        "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
    ],
    CATALOG_PATH.as_posix(): [
        "- dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_base64_perf.zig`",
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `24` direct C parity cases and preserves the dedicated slowdown packet as four case labels, `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`, each at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `27` direct C parity cases and preserves the last blocked slowdown packet as `64B` at `iterations = 200000` and `1501B` at `iterations = 12000`, both with `max_slowdown_pct = 150`",
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`",
    ],
    BASE64_SLICE_PATH.as_posix(): [
        "- current `master` keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`",
        "- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    ],
    CHECKSUM_SLICE_PATH.as_posix(): [
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `27` direct C parity cases and preserves the last blocked slowdown packet as `64B` at `iterations = 200000` and `1501B` at `iterations = 12000`, both with `max_slowdown_pct = 150`",
    ],
    HEXDUMP_SLICE_PATH.as_posix(): [
        "- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`",
        "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`",
    ],
    PHASE6_BUILD_PATH.as_posix(): [
        "const base64_perf_step = b.step(\"phase6-base64-perf\", \"Run Phase 6 base64 perf gate\");",
        "const hexdump_perf_step = b.step(\"phase6-hexdump-perf\", \"Run Phase 6 hexdump perf gate\");",
    ],
    MAKEFILE_PATH.as_posix(): [
        "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    ],
    WORKFLOW_PATH.as_posix(): [
        "- name: Self-test Phase 6 perf-threshold checker",
        "- name: Check Phase 6 perf threshold markers",
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
]

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
            raise ValidationError(f"unexpected checksum perf build route in {PHASE6_BUILD_PATH}: {snippet}")

    vectors_text = read_text(repo_root / BASE64_VECTORS_PATH)
    for marker in BASE64_VECTOR_MARKERS:
        if marker not in vectors_text:
            raise ValidationError(f"missing base64 perf marker in {BASE64_VECTORS_PATH}: {marker}")

    matrix_text = read_text(repo_root / HEXDUMP_MATRIX_PATH)
    for marker in HEXDUMP_MATRIX_MARKERS:
        if marker not in matrix_text:
            raise ValidationError(f"missing hexdump perf marker in {HEXDUMP_MATRIX_PATH}: {marker}")


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

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {MANIFEST_PATH}")
    base64 = determinism.get("base64", {})
    if base64.get("perf_replay_cases") != 4 or base64.get("transient_generated_include_committed") is not False:
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
        HEXDUMP_VECTORS_PATH.as_posix(),
        HEXDUMP_MATRIX_PATH.as_posix(),
        PHASE6_BUILD_PATH.as_posix(),
        MAKEFILE_PATH.as_posix(),
        WORKFLOW_PATH.as_posix(),
    }
    for rel_path in sorted(required):
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")
    for rel_path in [CHECKSUM_HELPER_PATH, CHECKSUM_REPLAY_PATH, CHECKSUM_PERF_PATH, CHECKSUM_VECTORS_PATH]:
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
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write(root / rel_path, "\n".join(snippets) + "\n")
    write(root / BASE64_VECTORS_PATH, "\n".join(BASE64_VECTOR_MARKERS) + "\n")
    write(root / BASE64_PERF_PATH, "pub fn main() void {}\n")
    write(root / HEXDUMP_VECTORS_PATH, "pub const cases = .{};\n")
    write(root / HEXDUMP_MATRIX_PATH, "\n".join(HEXDUMP_MATRIX_MARKERS) + "\n")

    manifest = {
        "perf_posture": dict(EXPECTED_PERF_POSTURE),
        "perf_thresholds": {
            "base64": {"cases": list(BASE64_CASES)},
            "bsearch": {"typed_lookup_budget": 4, "raw_lookup_budget": 4},
            "checksum": {"cases": list(CHECKSUM_CASES)},
            "hexdump": {"cases": list(HEXDUMP_CASES)},
        },
        "determinism_evidence": {
            "base64": {
                "perf_replay_cases": 4,
                "transient_generated_include_committed": False,
            },
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


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        assert_failure(
            root,
            MANIFEST_PATH,
            '"perf_replay_cases": 4',
            '"perf_replay_cases": 3',
        )
        assert_failure(
            root,
            SURVEY_PATH,
            "zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`",
            "zigux/tests/phase6_base64_perf.zig` are not directly readable on current `master`",
        )
        assert_failure(
            root,
            BASE64_VECTORS_PATH,
            '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
            '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150 },',
        )
        assert_failure(
            root,
            PHASE6_BUILD_PATH,
            'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
            'const base64_perf_step = b.step("phase6-base64-perf-missing", "Run Phase 6 base64 perf gate");',
        )
        assert_failure(
            root,
            WORKFLOW_PATH,
            '- name: Run Phase 6 hexdump perf gate',
            '- name: Run Phase 6 hex perf missing',
        )
        (root / CHECKSUM_PERF_PATH).parent.mkdir(parents=True, exist_ok=True)
        write(root / CHECKSUM_PERF_PATH, "unexpected\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if CHECKSUM_PERF_PATH.as_posix() not in str(exc):
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
    print("Phase 6 perf threshold markers look aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
