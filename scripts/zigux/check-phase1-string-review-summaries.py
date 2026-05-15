#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_HELPER = "tools/lib/string.zig"

EXPECTED_SUMMARIES = {
    "prefix_suffix_review_summary": (
        "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields, "
        "so strHasPrefix and str_has_prefix plus strstarts plus strEndsWith and str_ends_with plus strends remain review-visible at the helper surface"
    ),
    "lookup_review_summary": (
        "helper-local string lookup anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated matchString or match_string fixture keys, so C-string list lookup order and the Linux-style alias remain review-visible at the helper surface"
    ),
    "sysfs_review_summary": (
        "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface"
    ),
    "strscpy_review_summary": (
        "helper-local string copy-and-pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strscpy or strscpyPad fixture keys"
    ),
    "strnchr_review_summary": (
        "the direct counted-search follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search fixture keys, so strnchr() count-limited scanning and strnchrNul() or strnchrnul() match-or-NUL boundary behavior remain owned by the helper-local anchors"
    ),
    "trim_nul_review_summary": (
        "the direct trim follow-up stays explicit because the shared Phase 1 string fixture records the trimmed bytes but not the preserved tail bytes beyond the first embedded terminator"
    ),
    "phase1_trim_cstr_replay_summary": (
        "the shared Phase 1 string replay still only locks the plain trailing-whitespace trimSpaces bytes from the committed fixture, while the direct helper-local trim follow-up keeps embedded-NUL trimming for trimSpaces and strim plus strstrip and preserved tail-byte review explicit because the shared packet still does not exercise every trim alias or every post-NUL byte position"
    ),
    "memchr_moving_dirty_review_summary": (
        "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one fixed dirty index and the clean case, but not the moving earliest-mismatch ownership as later dirty bytes become the next live divergence"
    ),
    "memparse_review_summary": (
        "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation"
    ),
    "shared_replace_char_cstr_review_summary": (
        "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership"
    ),
}


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"missing:{path.as_posix()}"]
    except json.JSONDecodeError as exc:
        return None, [f"json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]


def collect_summary_issues(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    manifest, load_errors = load_json(manifest_path)
    if load_errors:
        return load_errors
    if not isinstance(manifest, dict):
        return ["phase1_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_manifest:review_anchors"]

    string_review_anchors = review_anchors.get(STRING_HELPER)
    if not isinstance(string_review_anchors, dict):
        return [f"phase1_manifest_review_anchor:shape={STRING_HELPER}"]

    issues: list[str] = []
    for key, expected in EXPECTED_SUMMARIES.items():
        if string_review_anchors.get(key) != expected:
            issues.append(f"phase1_manifest_review_anchor:value={STRING_HELPER}:{key}")
    return issues


def make_fixture_root(root: Path) -> None:
    manifest_path = root / MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "review_anchors": {
            STRING_HELPER: dict(EXPECTED_SUMMARIES),
        }
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_review_summary_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_summary_issues(root) == []
        case_count += 1

        manifest_path = root / MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key in EXPECTED_SUMMARIES:
            mutated = json.loads(json.dumps(manifest))
            mutated["review_anchors"][STRING_HELPER][key] = "drift"
            manifest_path.write_text(json.dumps(mutated, indent=2) + "\n", encoding="utf-8")
            assert collect_summary_issues(root) == [
                f"phase1_manifest_review_anchor:value={STRING_HELPER}:{key}"
            ]
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"][STRING_HELPER]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert collect_summary_issues(root) == [
            f"phase1_manifest_review_anchor:shape={STRING_HELPER}"
        ]
        case_count += 1

    print("PHASE1_STRING_REVIEW_SUMMARY_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_SUMMARY_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail-close on the Phase 1 string review-summary fields in the helper manifest."
    )
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    issues = collect_summary_issues(repo_root(args.root))
    if issues:
        print("PHASE1_STRING_REVIEW_SUMMARIES=fail")
        print("PHASE1_STRING_REVIEW_SUMMARY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_STRING_REVIEW_SUMMARY_ISSUES_END")
        return 1

    print("PHASE1_STRING_REVIEW_SUMMARIES=pass")
    print(f"PHASE1_STRING_REVIEW_SUMMARY_KEY_COUNT={len(EXPECTED_SUMMARIES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
