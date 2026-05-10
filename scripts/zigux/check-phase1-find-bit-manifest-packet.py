#!/usr/bin/env python3
"""Fail-close the current Phase 1 find_bit manifest review packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


REQUIRED_FILE = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

FIND_BIT_REVIEW_PATH = ("review_anchors", "tools/lib/find_bit.zig")

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "single-word next scans honor start masks"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "zero-bit windows return without reading bitmap words"',
    'test "zero-sized scans ignore populated backing words"',
    'test "next scans past nbits return without reading bitmap words"',
    'test "tail-word next set scans skip earlier in-range matches before clamping"',
    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    'test "low-level underscore aliases mirror the primary find helpers"',
]

EXPECTED_PARITY_FIXTURE_KEYS = [
    "inclusive_boundary_next",
    "inclusive_boundary_zero",
    "inclusive_boundary_and",
    "past_nbits_next",
    "past_nbits_zero",
    "past_nbits_and",
    "tail_clamped_first",
    "tail_clamped_next",
    "tail_zero_clamped_first",
    "tail_zero_clamped_next",
    "tail_and_clamped_first",
    "tail_and_clamped_next",
    "tail_clamped_last",
    "tail_clamped_empty_last",
]

EXPECTED_REVIEW_FIELDS = {
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "zero_bit_window": 'test "zero-bit windows return without reading bitmap words"',
    "zero_sized_short_circuit": 'test "zero-sized scans ignore populated backing words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "past_nbits_owner_summary": "the shared Phase 1 replay now consumes the committed past_nbits_* fixture fields directly, while the direct helper-local past-nbits test remains a review-visible boundary anchor for that path",
    "tail_word_set_skip_anchor": 'test "tail-word next set scans skip earlier in-range matches before clamping"',
    "underscore_alias_anchor": 'test "low-level underscore aliases mirror the primary find helpers"',
    "tail_word_skip_anchor": 'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    "review_packet_summary": "shared Phase 1 fixture keys now own the inclusive-boundary, past-nbits, and tail-clamped find_bit replay, while helper-local anchors keep same-word start-mask, zero-window, zero-sized short-circuit, tail-word set or zero or shared skip, and underscore-alias behavior review-visible on current master",
}


class CheckError(Exception):
    pass


def load_review(root: Path) -> dict:
    manifest_path = root / REQUIRED_FILE
    if not manifest_path.is_file():
        raise CheckError(f"missing_file:{REQUIRED_FILE.as_posix()}")

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid_json:{REQUIRED_FILE.as_posix()}:{exc}") from exc

    cursor = payload
    for key in FIND_BIT_REVIEW_PATH:
        if not isinstance(cursor, dict) or key not in cursor:
            raise CheckError(f"missing_review_path:{'.'.join(FIND_BIT_REVIEW_PATH)}")
        cursor = cursor[key]

    if not isinstance(cursor, dict):
        raise CheckError("invalid_review_entry:tools/lib/find_bit.zig")

    return cursor


def check_equal(review: dict, key: str, expected) -> None:
    actual = review.get(key)
    if actual != expected:
        raise CheckError(f"manifest_find_bit:{key}:mismatch")


def run_check(root: Path) -> None:
    review = load_review(root)
    check_equal(review, "helper_test_anchors", EXPECTED_HELPER_TEST_ANCHORS)
    check_equal(review, "parity_fixture_keys", EXPECTED_PARITY_FIXTURE_KEYS)
    check_equal(review, "tail_clamp_fixture_keys", EXPECTED_PARITY_FIXTURE_KEYS[6:])
    for key, expected in EXPECTED_REVIEW_FIELDS.items():
        check_equal(review, key, expected)


def write_fixture(root: Path) -> None:
    manifest_path = root / REQUIRED_FILE
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/find_bit.zig": {
                        "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
                        "same_word_start_masks": EXPECTED_REVIEW_FIELDS["same_word_start_masks"],
                        "inclusive_boundary_start": EXPECTED_REVIEW_FIELDS["inclusive_boundary_start"],
                        "zero_bit_window": EXPECTED_REVIEW_FIELDS["zero_bit_window"],
                        "zero_sized_short_circuit": EXPECTED_REVIEW_FIELDS["zero_sized_short_circuit"],
                        "past_nbits_short_circuit": EXPECTED_REVIEW_FIELDS["past_nbits_short_circuit"],
                        "past_nbits_owner_summary": EXPECTED_REVIEW_FIELDS["past_nbits_owner_summary"],
                        "tail_word_set_skip_anchor": EXPECTED_REVIEW_FIELDS["tail_word_set_skip_anchor"],
                        "underscore_alias_anchor": EXPECTED_REVIEW_FIELDS["underscore_alias_anchor"],
                        "tail_word_skip_anchor": EXPECTED_REVIEW_FIELDS["tail_word_skip_anchor"],
                        "parity_fixture_keys": EXPECTED_PARITY_FIXTURE_KEYS,
                        "tail_clamp_fixture_keys": EXPECTED_PARITY_FIXTURE_KEYS[6:],
                        "review_packet_summary": EXPECTED_REVIEW_FIELDS["review_packet_summary"],
                    }
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def expect_failure(root: Path, expected: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        assert str(exc) == expected, f"expected {expected!r}, got {str(exc)!r}"
    else:
        raise AssertionError(f"expected failure {expected!r}")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_find_bit_manifest_") as tmp_dir:
        root = Path(tmp_dir)

        expect_failure(root, f"missing_file:{REQUIRED_FILE.as_posix()}")
        cases += 1

        write_fixture(root)
        run_check(root)
        cases += 1

        manifest_path = root / REQUIRED_FILE
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        del payload["review_anchors"]["tools/lib/find_bit.zig"]["helper_test_anchors"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "manifest_find_bit:helper_test_anchors:mismatch")
        cases += 1

        write_fixture(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["review_anchors"]["tools/lib/find_bit.zig"]["tail_word_skip_anchor"] = "wrong"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "manifest_find_bit:tail_word_skip_anchor:mismatch")
        cases += 1

        write_fixture(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["review_anchors"]["tools/lib/find_bit.zig"]["review_packet_summary"] = "wrong"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "manifest_find_bit:review_packet_summary:mismatch")
        cases += 1

        write_fixture(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["review_anchors"]["tools/lib/find_bit.zig"]["parity_fixture_keys"] = EXPECTED_PARITY_FIXTURE_KEYS[:-1]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "manifest_find_bit:parity_fixture_keys:mismatch")
        cases += 1

        write_fixture(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["review_anchors"]["tools/lib/find_bit.zig"]["tail_clamp_fixture_keys"] = EXPECTED_PARITY_FIXTURE_KEYS[6:-1]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "manifest_find_bit:tail_clamp_fixture_keys:mismatch")
        cases += 1

        write_fixture(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        del payload["review_anchors"]["tools/lib/find_bit.zig"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        expect_failure(root, "missing_review_path:review_anchors.tools/lib/find_bit.zig")
        cases += 1

    print(f"PHASE1_FIND_BIT_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path.cwd())
    except CheckError as exc:
        print(str(exc))
        return 1

    print("phase1_find_bit_manifest_packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
