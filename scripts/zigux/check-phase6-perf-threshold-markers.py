#!/usr/bin/env python3
"""Guard the current Phase 6 helper perf-threshold packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
BASE64_FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BSEARCH_FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
CHECKSUM_FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
HEXDUMP_FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
BSEARCH_PERF_PATH = Path("zigux/tests/phase6_bsearch_perf.zig")
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

REQUIRED_SURVEY_SNIPPETS = [
    "the exact posture below was re-read from current `master` on `2026-05-27`",
    "`iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
    "`len15` at `reps = 4_000`, `len64` at `reps = 2_000`, and `len1024` at `reps = 250`",
    "`query_count = 16`",
    "`std.math.log2_int_ceil(usize, case.len) + 1`",
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

REQUIRED_BASE64_FIXTURE_SNIPPETS = [
    '.label = "STD_PAD"',
    '.label = "STD_NO_PAD"',
    '.label = "URLSAFE_PAD"',
    '.label = "URLSAFE_NO_PAD"',
    '.label = "IMAP_PAD"',
    '.label = "IMAP_NO_PAD"',
    ".iterations = 12000",
    ".max_encode_slowdown_pct = 150",
    ".max_decode_slowdown_pct = 325",
]

REQUIRED_BSEARCH_FIXTURE_SNIPPETS = [
    '.{ .label = "len15", .len = representative_ascending_values.len, .reps = 4_000 }',
    '.{ .label = "len64", .len = 64, .reps = 2_000 }',
    '.{ .label = "len1024", .len = 1_024, .reps = 250 }',
    "pub const query_count: usize = 16;",
]

REQUIRED_CHECKSUM_FIXTURE_SNIPPETS = [
    '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 }',
    '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 }',
    '.{ .label = "IPV4_20B", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 }',
    '.{ .label = "IPV4_20B_UPDATED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 }',
    '.{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 }',
    '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 }',
]

REQUIRED_HEXDUMP_FIXTURE_SNIPPETS = [
    '.label = "16B-plain-g1"',
    ".reps = 40_000",
    ".max_slowdown_pct = 175",
    '.label = "32B-ascii-g2"',
    ".reps = 10_000",
    ".max_slowdown_pct = 550",
    '.label = "16B-ascii-g4"',
    ".reps = 20_000",
    '.label = "16B-ascii-g8"',
    ".max_slowdown_pct = 600",
]

REQUIRED_BSEARCH_PERF_SNIPPETS = [
    "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
    "const average_budget = max_compare_budget;",
    "const worst_case_budget = max_compare_budget;",
]

EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_EVIDENCE_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_BASE64_LABELS = [
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
]
EXPECTED_BSEARCH_CASES = [
    {"label": "len15", "reps": 4000},
    {"label": "len64", "reps": 2000},
    {"label": "len1024", "reps": 250},
]
EXPECTED_BSEARCH_LABELS = ["len15", "len64", "len1024"]
EXPECTED_BSEARCH_FORMULA = "std.math.log2_int_ceil(len) + 1"
EXPECTED_CHECKSUM_CASES = [
    {"label": "64B", "iterations": 200000, "max_slowdown_pct": 150},
    {"label": "1501B", "iterations": 12000, "max_slowdown_pct": 150},
]
EXPECTED_CHECKSUM_IPV4_CASES = [
    {"label": "IPV4_20B", "iterations": 600000, "max_slowdown_pct": 100},
    {"label": "IPV4_20B_UPDATED", "iterations": 600000, "max_slowdown_pct": 100},
    {"label": "IPV4_24B", "iterations": 500000, "max_slowdown_pct": 100},
    {"label": "IPV4_60B", "iterations": 250000, "max_slowdown_pct": 100},
]
EXPECTED_HEXDUMP_CASES = [
    {"label": "16B-plain-g1", "reps": 40000, "max_slowdown_pct": 175},
    {"label": "32B-ascii-g2", "reps": 10000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g4", "reps": 20000, "max_slowdown_pct": 550},
    {"label": "16B-ascii-g8", "reps": 20000, "max_slowdown_pct": 600},
]

SELF_TEST_CASE_COUNT = 20


class ValidationError(RuntimeError):
    """Raised when the Phase 6 perf-threshold packet drifts."""



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
                f"missing expected Phase 6 perf-threshold marker in {path.as_posix()}: {snippet}"
            )



def load_manifest(path: Path) -> dict[str, object]:
    try:
        manifest = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValidationError(f"manifest root is not an object: {path.as_posix()}")
    return manifest



def get_helper(manifest: dict[str, object], key: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"manifest helpers missing for {key}")
    for helper in helpers:
        if isinstance(helper, dict) and helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper row in manifest: {key}")



def require_routes(routes: object, label: str, expected_routes: list[str]) -> None:
    if not isinstance(routes, list):
        raise ValidationError(f"{label} rerun routes missing")
    for route in expected_routes:
        if route not in routes:
            raise ValidationError(f"{label} rerun route missing {route}")



def require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise ValidationError(f"{label} drifted")



def validate_manifest_common(manifest: dict[str, object], packet: str, lane_scope: str, path: Path) -> None:
    require_equal(manifest.get("packet"), packet, f"{path.as_posix()} packet")
    require_equal(manifest.get("phase"), "Phase 6", f"{path.as_posix()} phase")
    require_equal(manifest.get("surveyed_head"), EXPECTED_SURVEYED_HEAD, f"{path.as_posix()} surveyed_head")
    require_equal(manifest.get("lane_scope"), lane_scope, f"{path.as_posix()} lane_scope")



def validate_base64_perf(perf: dict[str, object], label: str) -> None:
    require_equal(perf.get("case_labels"), EXPECTED_BASE64_LABELS, f"{label} case_labels")
    require_equal(perf.get("iterations"), 12000, f"{label} iterations")
    require_equal(perf.get("max_encode_slowdown_pct"), 150, f"{label} max_encode_slowdown_pct")
    require_equal(perf.get("max_decode_slowdown_pct"), 325, f"{label} max_decode_slowdown_pct")
    require_routes(
        perf.get("linux_style_rerun_routes"),
        label,
        [
            "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-base64-perf",
            "make -C zigux phase6-perf",
        ],
    )



def validate_bsearch_perf(perf: dict[str, object], label: str, *, bound_field: str) -> None:
    require_equal(perf.get("cases"), EXPECTED_BSEARCH_CASES, f"{label} cases")
    require_equal(perf.get("case_labels"), EXPECTED_BSEARCH_LABELS, f"{label} case_labels")
    require_equal(perf.get("query_count"), 16, f"{label} query_count")
    require_equal(perf.get(bound_field), EXPECTED_BSEARCH_FORMULA, f"{label} {bound_field}")
    require_routes(
        perf.get("linux_style_rerun_routes"),
        label,
        [
            "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-bsearch-perf",
            "make -C zigux phase6-perf",
        ],
    )



def validate_checksum_perf(perf: dict[str, object], label: str) -> None:
    require_equal(perf.get("cases"), EXPECTED_CHECKSUM_CASES, f"{label} cases")
    require_equal(perf.get("ipv4_fast_path_cases"), EXPECTED_CHECKSUM_IPV4_CASES, f"{label} ipv4_fast_path_cases")
    require_routes(
        perf.get("linux_style_rerun_routes"),
        label,
        [
            "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-checksum-perf",
            "make -C zigux phase6-perf",
        ],
    )



def validate_hexdump_perf(perf: dict[str, object], label: str) -> None:
    require_equal(perf.get("cases"), EXPECTED_HEXDUMP_CASES, f"{label} cases")
    require_routes(
        perf.get("linux_style_rerun_routes"),
        label,
        [
            "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-hexdump-review",
            "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-hexdump-perf-matrix-test",
            "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
            "make -C zigux phase6-hexdump-perf",
            "make -C zigux phase6-perf",
        ],
    )



def validate_evidence_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    validate_manifest_common(
        manifest, "phase6-helper-evidence", EXPECTED_EVIDENCE_LANE_SCOPE, path
    )

    validate_base64_perf(
        get_helper(manifest, "base64").get("current_perf_evidence"), "helper-evidence base64"
    )
    validate_bsearch_perf(
        get_helper(manifest, "bsearch").get("current_perf_evidence"),
        "helper-evidence bsearch",
        bound_field="budget_formula",
    )
    validate_checksum_perf(
        get_helper(manifest, "checksum").get("current_perf_evidence"),
        "helper-evidence checksum",
    )
    validate_hexdump_perf(
        get_helper(manifest, "hexdump").get("current_perf_evidence"), "helper-evidence hexdump"
    )



def validate_parity_manifest(path: Path) -> None:
    manifest = load_manifest(path)
    validate_manifest_common(
        manifest, "phase6-helper-parity", EXPECTED_PARITY_LANE_SCOPE, path
    )

    validate_base64_perf(
        get_helper(manifest, "base64").get("current_perf_evidence"), "helper-parity base64"
    )
    bsearch_perf = get_helper(manifest, "bsearch").get("current_perf_evidence")
    require_equal(
        bsearch_perf.get("budget_model"), "comparison_budget", "helper-parity bsearch budget_model"
    )
    validate_bsearch_perf(bsearch_perf, "helper-parity bsearch", bound_field="bound_budget_formula")
    validate_checksum_perf(
        get_helper(manifest, "checksum").get("current_perf_evidence"),
        "helper-parity checksum",
    )
    validate_hexdump_perf(
        get_helper(manifest, "hexdump").get("current_perf_evidence"), "helper-parity hexdump"
    )



def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SURVEY_PATH, REQUIRED_SURVEY_SNIPPETS)
    require_snippets(repo_root / BASE64_FIXTURES_PATH, REQUIRED_BASE64_FIXTURE_SNIPPETS)
    require_snippets(repo_root / BSEARCH_FIXTURES_PATH, REQUIRED_BSEARCH_FIXTURE_SNIPPETS)
    require_snippets(repo_root / CHECKSUM_FIXTURES_PATH, REQUIRED_CHECKSUM_FIXTURE_SNIPPETS)
    require_snippets(repo_root / HEXDUMP_FIXTURES_PATH, REQUIRED_HEXDUMP_FIXTURE_SNIPPETS)
    require_snippets(repo_root / BSEARCH_PERF_PATH, REQUIRED_BSEARCH_PERF_SNIPPETS)
    validate_evidence_manifest(repo_root / EVIDENCE_MANIFEST_PATH)
    validate_parity_manifest(repo_root / PARITY_MANIFEST_PATH)



def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def scaffold_manifest(packet: str, lane_scope: str, *, parity: bool) -> dict[str, object]:
    bsearch_perf: dict[str, object] = {
        "cases": EXPECTED_BSEARCH_CASES,
        "case_labels": EXPECTED_BSEARCH_LABELS,
        "query_count": 16,
        "linux_style_rerun_routes": [
            "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
            "make -C zigux phase6-bsearch-perf",
            "make -C zigux phase6-perf",
        ],
    }
    if parity:
        bsearch_perf["budget_model"] = "comparison_budget"
        bsearch_perf["bound_budget_formula"] = EXPECTED_BSEARCH_FORMULA
    else:
        bsearch_perf["budget_formula"] = EXPECTED_BSEARCH_FORMULA

    return {
        "packet": packet,
        "phase": "Phase 6",
        "surveyed_head": EXPECTED_SURVEYED_HEAD,
        "lane_scope": lane_scope,
        "helpers": [
            {
                "key": "base64",
                "current_perf_evidence": {
                    "case_labels": EXPECTED_BASE64_LABELS,
                    "iterations": 12000,
                    "max_encode_slowdown_pct": 150,
                    "max_decode_slowdown_pct": 325,
                    "linux_style_rerun_routes": [
                        "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
                        "make -C zigux phase6-base64-perf",
                        "make -C zigux phase6-perf",
                    ],
                },
            },
            {
                "key": "bsearch",
                "current_perf_evidence": bsearch_perf,
            },
            {
                "key": "checksum",
                "current_perf_evidence": {
                    "cases": EXPECTED_CHECKSUM_CASES,
                    "ipv4_fast_path_cases": EXPECTED_CHECKSUM_IPV4_CASES,
                    "linux_style_rerun_routes": [
                        "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
                        "make -C zigux phase6-checksum-perf",
                        "make -C zigux phase6-perf",
                    ],
                },
            },
            {
                "key": "hexdump",
                "current_perf_evidence": {
                    "cases": EXPECTED_HEXDUMP_CASES,
                    "linux_style_rerun_routes": [
                        "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
                        "make -C zigux phase6-hexdump-review",
                        "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
                        "make -C zigux phase6-hexdump-perf-matrix-test",
                        "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
                        "make -C zigux phase6-hexdump-perf",
                        "make -C zigux phase6-perf",
                    ],
                },
            },
        ],
    }



def scaffold_repo(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join(REQUIRED_SURVEY_SNIPPETS) + "\n")
    write(root / BASE64_FIXTURES_PATH, "\n".join(REQUIRED_BASE64_FIXTURE_SNIPPETS) + "\n")
    write(root / BSEARCH_FIXTURES_PATH, "\n".join(REQUIRED_BSEARCH_FIXTURE_SNIPPETS) + "\n")
    write(root / CHECKSUM_FIXTURES_PATH, "\n".join(REQUIRED_CHECKSUM_FIXTURE_SNIPPETS) + "\n")
    write(root / HEXDUMP_FIXTURES_PATH, "\n".join(REQUIRED_HEXDUMP_FIXTURE_SNIPPETS) + "\n")
    write(root / BSEARCH_PERF_PATH, "\n".join(REQUIRED_BSEARCH_PERF_SNIPPETS) + "\n")
    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            scaffold_manifest(
                "phase6-helper-evidence", EXPECTED_EVIDENCE_LANE_SCOPE, parity=False
            ),
            indent=2,
        )
        + "\n",
    )
    write(
        root / PARITY_MANIFEST_PATH,
        json.dumps(
            scaffold_manifest(
                "phase6-helper-parity", EXPECTED_PARITY_LANE_SCOPE, parity=True
            ),
            indent=2,
        )
        + "\n",
    )



def mutate_text(path: Path, old: str, new: str) -> None:
    write(path, read_text(path).replace(old, new, 1))



def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_perf_thresholds_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        cases = [
            (
                SURVEY_PATH,
                "the exact posture below was re-read from current `master` on `2026-05-27`",
                "the exact posture below was re-read from current `master` on `2026-05-26`",
                "phase6-perf-gate-survey.md",
            ),
            (
                SURVEY_PATH,
                "`std.math.log2_int_ceil(usize, case.len) + 1`",
                "`std.math.log2_int_floor(usize, case.len) + 1`",
                "phase6-perf-gate-survey.md",
            ),
            (
                BASE64_FIXTURES_PATH,
                '.label = "IMAP_NO_PAD"',
                '.label = "IMAP_NOPAD"',
                "phase6_base64_vectors.zig",
            ),
            (
                BSEARCH_FIXTURES_PATH,
                "pub const query_count: usize = 16;",
                "pub const query_count: usize = 32;",
                "phase6_bsearch_vectors.zig",
            ),
            (
                CHECKSUM_FIXTURES_PATH,
                '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 }',
                '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 16_000, .max_slowdown_pct = 150 }',
                "phase6_checksum_vectors.zig",
            ),
            (
                HEXDUMP_FIXTURES_PATH,
                ".max_slowdown_pct = 600",
                ".max_slowdown_pct = 650",
                "phase6_hexdump_vectors.zig",
            ),
            (
                BSEARCH_PERF_PATH,
                "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
                "const max_compare_budget = std.math.log2_int_floor(usize, case.len) + 1;",
                "phase6_bsearch_perf.zig",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"surveyed_head": "current-master-readback-2026-05-22"',
                '"surveyed_head": "current-master-readback-2026-05-21"',
                "surveyed_head drifted",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"budget_formula": "std.math.log2_int_ceil(len) + 1"',
                '"budget_formula": "std.math.log2_int_floor(len) + 1"',
                "helper-evidence bsearch budget_formula drifted",
            ),
            (
                PARITY_MANIFEST_PATH,
                '"bound_budget_formula": "std.math.log2_int_ceil(len) + 1"',
                '"bound_budget_formula": "std.math.log2_int_floor(len) + 1"',
                "helper-parity bsearch bound_budget_formula drifted",
            ),
            (
                PARITY_MANIFEST_PATH,
                '"budget_model": "comparison_budget"',
                '"budget_model": "comparison_count"',
                "helper-parity bsearch budget_model drifted",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"max_decode_slowdown_pct": 325',
                '"max_decode_slowdown_pct": 350',
                "helper-evidence base64 max_decode_slowdown_pct drifted",
            ),
            (
                PARITY_MANIFEST_PATH,
                '"max_encode_slowdown_pct": 150',
                '"max_encode_slowdown_pct": 175',
                "helper-parity base64 max_encode_slowdown_pct drifted",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"label": "IPV4_60B"',
                '"label": "IPV4_64B"',
                "helper-evidence checksum ipv4_fast_path_cases drifted",
            ),
            (
                PARITY_MANIFEST_PATH,
                '"label": "32B-ascii-g2"',
                '"label": "32B-ascii-g4"',
                "helper-parity hexdump cases drifted",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"make -C zigux phase6-bsearch-perf"',
                '"make -C zigux phase6-bsearch-test"',
                "helper-evidence bsearch rerun route missing make -C zigux phase6-bsearch-perf",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"make -C zigux phase6-hexdump-review"',
                '"make -C zigux phase6-hexdump-test"',
                "helper-evidence hexdump rerun route missing make -C zigux phase6-hexdump-review",
            ),
            (
                PARITY_MANIFEST_PATH,
                '"make -C zigux phase6-hexdump-perf"',
                '"make -C zigux phase6-hexdump-test"',
                "helper-parity hexdump rerun route missing make -C zigux phase6-hexdump-perf",
            ),
            (
                EVIDENCE_MANIFEST_PATH,
                '"len1024"',
                '"len2048"',
                "helper-evidence bsearch cases drifted",
            ),
            (
                PARITY_MANIFEST_PATH,
                '"1501B"',
                '"1500B"',
                "helper-parity checksum cases drifted",
            ),
        ]

        for rel_path, old, new, expected in cases:
            mutate_text(root / rel_path, old, new)
            try:
                validate(root)
            except ValidationError as exc:
                if expected not in str(exc):
                    raise AssertionError(
                        f"expected {expected!r} in {str(exc)!r}"
                    ) from exc
            else:
                raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
            finally:
                scaffold_repo(root)
            cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_PERF_THRESHOLD_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_PERF_THRESHOLD_MARKERS_SELF_TEST_CASE_COUNT={cases_run}")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()



def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_PERF_THRESHOLD_MARKERS=fail: {exc}")
        return 1

    print("PHASE6_PERF_THRESHOLD_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
