#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_VALIDATOR_PATH = ROOT / "scripts" / "zigux" / "validate-phase1.py"
DEFAULT_MANIFEST_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase1_helper_manifest.json"

BITMAP_HELPER = "tools/lib/bitmap.zig"
EXPECTED_REPLAY_ANCHOR = 'test "phase 1 helper ports match committed parity fixture"'
EXPECTED_COPY_ALIAS_ANCHOR = 'test "bitmap copy aliases preserve tail clearing and extension semantics"'
EXPECTED_REVIEW_SUMMARY = (
    "shared Phase 1 fixture keys now own bitmap scnprintf output, tiny-buffer, and partial-window xor replay, "
    "while helper-local anchors keep allocator sizing and zero-fill behavior, predicate tail-mask, first-word "
    "and final-partial range boundaries, cross-word scnprintf collapse, truncation, copy alias, raw copy alias, "
    "zero-and-aligned copy-and-extend behavior, zero-sized destination-view, zero-bit no-op, zero-bit binary "
    "identity, and Linux-style alias behavior review-visible on current master"
)

REQUIRED_VALIDATOR_MARKERS = (
    '"phase1_helper_replay_anchor": \'test "phase 1 helper ports match committed parity fixture"\'',
    f'"review_packet_summary": "{EXPECTED_REVIEW_SUMMARY}"',
    'assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:phase1_helper_replay_anchor" in missing',
    'assert "phase1_manifest_review_anchor:value=tools/lib/bitmap.zig:review_packet_summary" in missing',
    'print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=25")',
)

FORBIDDEN_VALIDATOR_MARKERS = (
    'print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=23")',
    "review-visible only through the closure note",
)


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> list[str]:
    problems: list[str] = []

    review_anchors = manifest.get("review_anchors", {})
    bitmap = review_anchors.get(BITMAP_HELPER)
    if not isinstance(bitmap, dict):
        return [f"missing_manifest_helper:{BITMAP_HELPER}"]

    replay_anchor = bitmap.get("phase1_helper_replay_anchor")
    if replay_anchor != EXPECTED_REPLAY_ANCHOR:
        problems.append(
            "phase1_manifest_review_anchor_mismatch:"
            f"{BITMAP_HELPER}:phase1_helper_replay_anchor:expected={EXPECTED_REPLAY_ANCHOR!r}:actual={replay_anchor!r}"
        )

    copy_alias_anchor = bitmap.get("copy_alias_anchor")
    if copy_alias_anchor != EXPECTED_COPY_ALIAS_ANCHOR:
        problems.append(
            "phase1_manifest_review_anchor_mismatch:"
            f"{BITMAP_HELPER}:copy_alias_anchor:expected={EXPECTED_COPY_ALIAS_ANCHOR!r}:actual={copy_alias_anchor!r}"
        )

    review_summary = bitmap.get("review_packet_summary")
    if review_summary != EXPECTED_REVIEW_SUMMARY:
        problems.append(
            "phase1_manifest_review_anchor_mismatch:"
            f"{BITMAP_HELPER}:review_packet_summary:expected={EXPECTED_REVIEW_SUMMARY!r}:actual={review_summary!r}"
        )

    return problems


def validate_validator_text(text: str) -> list[str]:
    problems: list[str] = []

    for marker in REQUIRED_VALIDATOR_MARKERS:
        if marker not in text:
            problems.append(f"missing_validator_marker:{marker}")

    for marker in FORBIDDEN_VALIDATOR_MARKERS:
        if marker in text:
            problems.append(f"forbidden_validator_marker:{marker}")

    return problems


def run_self_test() -> int:
    manifest = {
        "review_anchors": {
            BITMAP_HELPER: {
                "phase1_helper_replay_anchor": EXPECTED_REPLAY_ANCHOR,
                "copy_alias_anchor": EXPECTED_COPY_ALIAS_ANCHOR,
                "review_packet_summary": EXPECTED_REVIEW_SUMMARY,
            }
        }
    }
    assert validate_manifest(manifest) == []

    bad_manifest = json.loads(json.dumps(manifest))
    bad_manifest["review_anchors"][BITMAP_HELPER]["phase1_helper_replay_anchor"] = "wrong"
    replay_anchor_problems = validate_manifest(bad_manifest)
    assert any("phase1_helper_replay_anchor" in item for item in replay_anchor_problems)

    bad_manifest = json.loads(json.dumps(manifest))
    bad_manifest["review_anchors"][BITMAP_HELPER]["copy_alias_anchor"] = "wrong"
    copy_alias_problems = validate_manifest(bad_manifest)
    assert any("copy_alias_anchor" in item for item in copy_alias_problems)

    bad_manifest = json.loads(json.dumps(manifest))
    bad_manifest["review_anchors"][BITMAP_HELPER]["review_packet_summary"] = "wrong"
    review_summary_problems = validate_manifest(bad_manifest)
    assert any("review_packet_summary" in item for item in review_summary_problems)

    good_validator = "\n".join(REQUIRED_VALIDATOR_MARKERS)
    assert validate_validator_text(good_validator) == []

    bad_validator = good_validator + '\nprint("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=23")\n'
    forbidden_problems = validate_validator_text(bad_validator)
    assert 'forbidden_validator_marker:print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=23")' in forbidden_problems

    missing_problems = validate_validator_text('print("PHASE1_VALIDATION_SELF_TEST_CASE_COUNT=25")')
    assert any(problem.startswith("missing_validator_marker:") for problem in missing_problems)

    print("PHASE1_BITMAP_MANIFEST_ANCHOR_CHECK_SELF_TEST=pass")
    print("PHASE1_BITMAP_MANIFEST_ANCHOR_CHECK_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when validate-phase1.py stops enforcing the current bitmap manifest replay anchor "
            "and when phase1_helper_manifest.json stops naming the shipped bitmap copy-alias review anchor "
            "or review-packet summary."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests.")
    parser.add_argument(
        "--validator",
        default=str(DEFAULT_VALIDATOR_PATH),
        help="Path to scripts/zigux/validate-phase1.py.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to zigux/tests/fixtures/phase1_helper_manifest.json.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    manifest_problems = validate_manifest(load_manifest(Path(args.manifest)))
    validator_problems = validate_validator_text(Path(args.validator).read_text(encoding="utf-8"))
    problems = manifest_problems + validator_problems

    if problems:
        print("PHASE1_BITMAP_MANIFEST_ANCHOR_CHECK=fail")
        for problem in problems:
            print(problem)
        return 1

    print("PHASE1_BITMAP_MANIFEST_ANCHOR_CHECK=pass")
    print(f"VALIDATOR={args.validator}")
    print(f"MANIFEST={args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
