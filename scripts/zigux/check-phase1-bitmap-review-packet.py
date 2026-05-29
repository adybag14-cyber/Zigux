#!/usr/bin/env python3
"""Guard the Phase 1 bitmap review packet against helper-local drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BITMAP_REL = Path("tools/lib/bitmap.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

BITMAP_HELPER = "tools/lib/bitmap.zig"

REQUIRED_HELPER_TESTS = [
    'test "bitmap range helpers preserve edges across whole-word spans"',
    'test "bitmap copy alias preserves raw source words without tail clearing"',
    'test "bitmap copy aliases preserve tail clearing and extension semantics"',
    'test "bitmap copy and extend handles zero and aligned counts"',
    'test "bitmap copy helpers keep zero-sized destination views untouched"',
    'test "bitmap zero-bit logical helpers stay explicit"',
    'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    'test "bitmap tail-masked helpers ignore out-of-range differences"',
    'test "bitmap full empty and weight ignore out-of-range tail bits"',
    'test "bitmap xor keeps caller-selected bit window"',
    'test "bitmap xor across a multiword tail still lets callers clamp the last word"',
    'test "bitmap or keeps caller-selected bit window"',
    'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    'test "bitmap weighted and andnot clamp counts to the declared tail window"',
    'test "bitmap complement clamps partial tails and leaves zero-sized caller views untouched"',
    'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    'test "bitmap scnprintf handles terminator-only and zero-length caller views"',
    'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    'test "bitmap Linux-style aliases mirror size state and allocation helpers"',
    'test "bitmap allocation helpers size zero fill and reset optionals"',
]

REQUIRED_MANIFEST_FIELDS: dict[str, Any] = {
    "first_word_boundary_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "final_partial_word_anchor": 'test "bitmap range helpers preserve edges across whole-word spans"',
    "fill_tail_clamp_anchor": 'test "bitmap full empty and weight ignore out-of-range tail bits"',
    "equal_fast_path_anchor": 'test "bitmap equal fast path ignores storage beyond an exact word boundary"',
    "predicate_tail_mask_anchor": 'test "bitmap tail-masked helpers ignore out-of-range differences"',
    "or_window_anchor": 'test "bitmap or keeps caller-selected bit window"',
    "or_multiword_tail_anchor": 'test "bitmap or across a multiword tail still lets callers clamp the last word"',
    "weighted_tail_count_anchor": 'test "bitmap weighted or and xor clamp counts to the declared tail window"',
    "scnprintf_cross_word_anchor": 'test "bitmap scnprintf keeps contiguous ranges merged across word boundaries"',
    "empty_buffer_anchor": 'test "bitmap scnprintf leaves the caller buffer untouched for an empty bitmap"',
    "copy_raw_alias_anchor": 'test "bitmap copy alias preserves raw source words without tail clearing"',
    "zero_bit_noop_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
    "zero_bit_binary_identity_anchor": 'test "bitmap zero-bit logical helpers stay explicit"',
    "linux_alias_anchor": 'test "bitmap Linux-style aliases mirror copy logical range and format helpers"',
    "partial_xor_review_fields": ["partial_xor_nbits", "partial_xor_masked_values"],
}

REQUIRED_FIXTURE_KEYS = [
    "weight",
    "scnprintf",
    "truncated_scnprintf_len",
    "truncated_scnprintf",
    "terminator_only_scnprintf_len",
    "terminator_only_nul",
    "zero_length_scnprintf_len",
    "alloc_words",
    "zalloc_words",
    "zalloc_values",
    "copy_values",
    "copy_clear_tail_values",
    "copy_and_extend_values",
    "complement_values",
    "and_result",
    "and_values",
    "andnot_result",
    "andnot_values",
    "or_values",
    "xor_values",
    "partial_xor_nbits",
    "partial_xor_masked_values",
    "equal",
    "intersects",
    "subset",
    "range_after_set",
    "range_after_clear",
    "full_after_fill",
    "empty_after_zero",
]

REQUIRED_CLOSURE_MARKERS = [
    "PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit",
    "PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp",
    "PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched",
    "PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit",
    "PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit",
]


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def load_text(root: Path, rel: Path, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"{rel.as_posix()}:missing")
        return ""


def load_json(root: Path, rel: Path, issues: list[str]) -> Any:
    text = load_text(root, rel, issues)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append(f"{rel.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}")
        return None


def require_text_once(text: str, rel: Path, markers: list[str], issues: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{rel.as_posix()}:{marker}:expected=1:actual={count}")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    bitmap_text = load_text(root, BITMAP_REL, issues)
    if bitmap_text:
        require_text_once(bitmap_text, BITMAP_REL, [marker + " {" for marker in REQUIRED_HELPER_TESTS], issues)

    manifest = load_json(root, MANIFEST_REL, issues)
    fixture = load_json(root, FIXTURE_REL, issues)
    closure_text = load_text(root, CLOSURE_REL, issues)

    if isinstance(manifest, dict):
        helpers = manifest.get("helpers")
        if not isinstance(helpers, list) or BITMAP_HELPER not in helpers:
            issues.append(f"{MANIFEST_REL.as_posix()}:helpers:missing:{BITMAP_HELPER}")

        anchors = manifest.get("review_anchors")
        if not isinstance(anchors, dict):
            issues.append(f"{MANIFEST_REL.as_posix()}:review_anchors:missing")
        else:
            bitmap_anchors = anchors.get(BITMAP_HELPER)
            if not isinstance(bitmap_anchors, dict):
                issues.append(f"{MANIFEST_REL.as_posix()}:review_anchors:{BITMAP_HELPER}:missing")
            else:
                helper_tests = bitmap_anchors.get("helper_test_anchors")
                if not isinstance(helper_tests, list):
                    issues.append(f"{MANIFEST_REL.as_posix()}:helper_test_anchors:missing")
                else:
                    for marker in REQUIRED_HELPER_TESTS:
                        if marker not in helper_tests:
                            issues.append(f"{MANIFEST_REL.as_posix()}:helper_test_anchors:missing:{marker}")
                for field, expected in REQUIRED_MANIFEST_FIELDS.items():
                    if bitmap_anchors.get(field) != expected:
                        issues.append(f"{MANIFEST_REL.as_posix()}:{field}:drift")

    if isinstance(fixture, dict):
        bitmap_fixture = fixture.get("bitmap")
        if not isinstance(bitmap_fixture, dict):
            issues.append(f"{FIXTURE_REL.as_posix()}:bitmap:missing")
        else:
            for key in REQUIRED_FIXTURE_KEYS:
                if key not in bitmap_fixture:
                    issues.append(f"{FIXTURE_REL.as_posix()}:bitmap:{key}:missing")

    if closure_text:
        require_text_once(closure_text, CLOSURE_REL, REQUIRED_CLOSURE_MARKERS, issues)

    return issues


def write_sample_root(root: Path) -> None:
    (root / BITMAP_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / CLOSURE_REL).parent.mkdir(parents=True, exist_ok=True)

    (root / BITMAP_REL).write_text("\n".join(marker + " {}" for marker in REQUIRED_HELPER_TESTS) + "\n", encoding="utf-8")
    (root / MANIFEST_REL).write_text(
        json.dumps(
            {
                "helpers": [BITMAP_HELPER],
                "review_anchors": {
                    BITMAP_HELPER: {
                        "helper_test_anchors": REQUIRED_HELPER_TESTS,
                        **REQUIRED_MANIFEST_FIELDS,
                    }
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / FIXTURE_REL).write_text(json.dumps({"bitmap": {key: True for key in REQUIRED_FIXTURE_KEYS}}, indent=2) + "\n", encoding="utf-8")
    (root / CLOSURE_REL).write_text("\n".join(REQUIRED_CLOSURE_MARKERS) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-review-packet-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        bitmap_path = root / BITMAP_REL
        bitmap_text = bitmap_path.read_text(encoding="utf-8")
        bitmap_path.write_text(bitmap_text.replace(REQUIRED_HELPER_TESTS[0] + " {}\n", "", 1), encoding="utf-8")
        assert any("helper_test" not in issue and "actual=0" in issue for issue in collect_issues(root))
        case_count += 1
        write_sample_root(root)

        manifest_path = root / MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"][BITMAP_HELPER]["zero_bit_noop_anchor"] = "drifted"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert f"{MANIFEST_REL.as_posix()}:zero_bit_noop_anchor:drift" in collect_issues(root)
        case_count += 1
        write_sample_root(root)

        fixture_path = root / FIXTURE_REL
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        del fixture["bitmap"]["partial_xor_masked_values"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert f"{FIXTURE_REL.as_posix()}:bitmap:partial_xor_masked_values:missing" in collect_issues(root)
        case_count += 1
        write_sample_root(root)

        closure_path = root / CLOSURE_REL
        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[-1], "drifted", 1), encoding="utf-8")
        assert any("PHASE1_BITMAP_LINUX_ALIAS_REVIEW" in issue and "actual=0" in issue for issue in collect_issues(root))
        case_count += 1

    print("PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run self-test cases")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_BITMAP_REVIEW_PACKET=fail")
        print("PHASE1_BITMAP_REVIEW_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_BITMAP_REVIEW_PACKET_ISSUES_END")
        return 1

    print("PHASE1_BITMAP_REVIEW_PACKET=pass")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_HELPER={BITMAP_HELPER}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_FIXTURE_KEY_COUNT={len(REQUIRED_FIXTURE_KEYS)}")
    print(f"PHASE1_BITMAP_REVIEW_PACKET_HELPER_TEST_COUNT={len(REQUIRED_HELPER_TESTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
