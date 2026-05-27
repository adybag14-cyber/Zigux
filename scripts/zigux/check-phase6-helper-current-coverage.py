#!/usr/bin/env python3
"""Validate the exact-current-coverage companion for the Phase 6 helper parity packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = Path("Documentation/zigux/phase6-helper-parity-current-coverage.md")
MANIFEST = Path("zigux/tests/phase6_helper_current_coverage_manifest.json")

EXPECTED_PACKET = "phase6-helper-parity-current-coverage"
EXPECTED_PHASE = "Phase 6"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-27"
EXPECTED_LANE_SCOPE = "exact helper coverage verification for the current Phase 6 parity packet"
EXPECTED_PARENT_CATALOG = "Documentation/zigux/phase6-helper-parity-catalog.md"
EXPECTED_COVERAGE_VERDICT = (
    "All four roadmap-backed Phase 6 helper destinations are present on current master, "
    "each helper body carries embedded tests, and each helper keeps a focused replay plus "
    "a dedicated parity, perf, or route-check companion."
)
EXPECTED_ROADMAP_ANCHORS = [
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
]
EXPECTED_HELPERS = [
    {
        "key": "base64",
        "roadmap_anchor": "lib/base64.c",
        "zig_helper": "lib/base64.zig",
        "helper_blob_sha": "844a091999aab9a1d78f90d7719450b4e590e962",
        "embedded_helper_test_count": 20,
        "selected_embedded_tests": [
            "variant-pinned convenience helpers mirror the generic api",
            "encode and decode sweep every one-byte and two-byte tail across variants and padding modes",
            "decode reverse maps classify every byte across all variants",
        ],
        "focused_replay": "zigux/tests/phase6_base64.zig",
        "exact_companions": [
            "zigux/tests/phase6_base64_perf.zig",
            "zigux/tests/phase6_base64_c_parity.zig",
            "zigux/tests/fixtures/phase6_base64_c_harness.c",
            "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
            "zigux/tests/phase6_base64_c_casegen.zig",
            "scripts/zigux/check-phase6-base64-c-parity.py",
        ],
    },
    {
        "key": "bsearch",
        "roadmap_anchor": "lib/bsearch.c",
        "zig_helper": "lib/bsearch.zig",
        "helper_blob_sha": "916a87eb91c0c3e620cf6e85c018180cdf772e58",
        "embedded_helper_test_count": 11,
        "selected_embedded_tests": [
            "typed and raw searches support duplicate spans and descending C ABI pointers",
            "native std.math.Order comparator pointers keep duplicate spans and insertion points aligned",
            "mutable wrappers keep write-through aliases with runtime-selected c abi comparator pointers",
        ],
        "focused_replay": "zigux/tests/phase6_bsearch.zig",
        "exact_companions": [
            "zigux/tests/phase6_bsearch_perf.zig",
            "zigux/tests/phase6_bsearch_c_parity.zig",
            "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
            "zigux/tests/phase6_bsearch_c_abi_budget.zig",
            "zigux/tests/fixtures/phase6_bsearch_c_harness.c",
            "scripts/zigux/check-phase6-bsearch-c-parity.py",
        ],
    },
    {
        "key": "checksum",
        "roadmap_anchor": "lib/checksum.c",
        "zig_helper": "lib/checksum.zig",
        "helper_blob_sha": "1cda59b1bd4e5d4e9989d2b9f4e84be62b8ccb7e",
        "embedded_helper_test_count": 12,
        "selected_embedded_tests": [
            "partial and compute match reference accumulation across seeded odd payloads",
            "pseudo-header helpers match direct checksum recomputation over pseudo-header bytes and payload",
            "ipFastCsum stays aligned with compute across aligned IPv4 headers",
        ],
        "focused_replay": "zigux/tests/phase6_checksum.zig",
        "exact_companions": [
            "zigux/tests/phase6_checksum_perf.zig",
            "zigux/tests/phase6_checksum_c_parity.zig",
            "zigux/tests/fixtures/phase6_checksum_c_harness.c",
            "scripts/zigux/check-phase6-checksum-c-parity.py",
        ],
    },
    {
        "key": "hexdump",
        "roadmap_anchor": "lib/hexdump.c",
        "zig_helper": "lib/hexdump.zig",
        "helper_blob_sha": "0fc9534ddf7e020ab00f981d5762b1703430170c",
        "embedded_helper_test_count": 17,
        "selected_embedded_tests": [
            "hexDumpToBuffer matches the kernel-style 16-byte line output",
            "hexDumpToBuffer uses native-endian grouping for 2, 4, and 8 byte groups",
            "hexDumpToBuffer follows kernel fixture normalization cases",
        ],
        "focused_replay": "zigux/tests/phase6_hexdump.zig",
        "exact_companions": [
            "zigux/tests/phase6_hexdump_perf.zig",
            "zigux/tests/phase6_hexdump_perf_matrix.zig",
            "scripts/zigux/check-phase6-hexdump-packet.py",
            "scripts/zigux/check-phase6-hexdump-route.py",
        ],
    },
]

SELF_TEST_CASE_COUNT = 4


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def validate_doc(content: str) -> None:
    required_snippets = [
        "# Phase 6 Helper Parity Current Coverage",
        "- surveyed head: `current-master-readback-2026-05-27`",
        "- parent parity catalog: `Documentation/zigux/phase6-helper-parity-catalog.md`",
        "All four roadmap-backed Phase 6 helper destinations are present on current `master`",
        "| `base64` | `lib/base64.c` | `lib/base64.zig` `844a091999aab9a1d78f90d7719450b4e590e962` | 20 | `zigux/tests/phase6_base64.zig` |",
        "| `bsearch` | `lib/bsearch.c` | `lib/bsearch.zig` `916a87eb91c0c3e620cf6e85c018180cdf772e58` | 11 | `zigux/tests/phase6_bsearch.zig` |",
        "| `checksum` | `lib/checksum.c` | `lib/checksum.zig` `1cda59b1bd4e5d4e9989d2b9f4e84be62b8ccb7e` | 12 | `zigux/tests/phase6_checksum.zig` |",
        "| `hexdump` | `lib/hexdump.c` | `lib/hexdump.zig` `0fc9534ddf7e020ab00f981d5762b1703430170c` | 17 | `zigux/tests/phase6_hexdump.zig` |",
        "Reopen this exact-current-coverage note only when one of the four roadmap-backed helper blobs changes",
    ]
    for snippet in required_snippets:
        if snippet not in content:
            raise ValidationError(f"documentation drifted: {snippet}")


def validate_manifest(data: dict[str, object]) -> None:
    if data.get("packet") != EXPECTED_PACKET:
        raise ValidationError("packet drift")
    if data.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase drift")
    if data.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise ValidationError("surveyed_head drift")
    if data.get("lane_scope") != EXPECTED_LANE_SCOPE:
        raise ValidationError("lane_scope drift")
    if data.get("parent_parity_catalog") != EXPECTED_PARENT_CATALOG:
        raise ValidationError("parent parity catalog drift")
    if data.get("coverage_verdict") != EXPECTED_COVERAGE_VERDICT:
        raise ValidationError("coverage verdict drift")
    if data.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("roadmap anchors drift")
    if data.get("helpers") != EXPECTED_HELPERS:
        raise ValidationError("helper snapshot drift")


def validate(root: Path) -> None:
    validate_doc(read_text(root / DOC))
    validate_manifest(read_json(root / MANIFEST))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold(root: Path) -> None:
    write(root / DOC, read_text(ROOT / DOC))
    write(root / MANIFEST, read_text(ROOT / MANIFEST))


def expect_failure(fn) -> None:
    try:
        fn()
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_current_coverage_") as tmpdir:
        root = Path(tmpdir)
        scaffold(root)
        validate(root)

        cases_run = 0

        def reset() -> None:
            scaffold(root)

        def mutate_and_expect_failure(mutator) -> None:
            nonlocal cases_run
            reset()
            mutator()
            expect_failure(lambda: validate(root))
            cases_run += 1

        mutate_and_expect_failure(
            lambda: write(
                root / MANIFEST,
                json.dumps(
                    {
                        **read_json(root / MANIFEST),
                        "surveyed_head": "current-master-readback-2026-05-26",
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        mutate_and_expect_failure(
            lambda: write(
                root / MANIFEST,
                json.dumps(
                    {
                        **read_json(root / MANIFEST),
                        "helpers": [
                            helper
                            if helper.get("key") != "bsearch"
                            else {**helper, "embedded_helper_test_count": 10}
                            for helper in read_json(root / MANIFEST)["helpers"]
                        ],
                    },
                    indent=2,
                )
                + "\n",
            )
        )
        mutate_and_expect_failure(
            lambda: write(
                root / DOC,
                read_text(root / DOC).replace(
                    "`lib/checksum.zig` `1cda59b1bd4e5d4e9989d2b9f4e84be62b8ccb7e`",
                    "`lib/checksum.zig` `deadbeef`",
                    1,
                ),
            )
        )
        mutate_and_expect_failure(lambda: (root / DOC).unlink())

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_HELPER_CURRENT_COVERAGE_SELF_TEST=pass")
    print(f"PHASE6_HELPER_CURRENT_COVERAGE_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
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
        print(f"PHASE6_HELPER_CURRENT_COVERAGE=fail: {exc}")
        return 1

    print("PHASE6_HELPER_CURRENT_COVERAGE=pass")
    print(f"PHASE6_HELPER_CURRENT_COVERAGE_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
