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
STRING_REL = Path("tools/lib/string.zig")

EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS = [
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "strstarts mirrors the header-level prefix helper"',
    'test "strEndsWith honors C-string boundaries"',
]

EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY = (
    "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests "
    "because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than "
    "dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix plus strstarts plus "
    "strEndsWith and str_ends_with plus strends remain review-visible at the helper surface"
)


def repo_root(root_arg: str | None) -> Path:
    return DEFAULT_ROOT if root_arg is None else Path(root_arg).resolve()


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(load_text(path)), []
    except json.JSONDecodeError as exc:
        return None, [f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in (MANIFEST_REL, STRING_REL):
        if not (root / rel).exists():
            missing.append(rel.as_posix())
    return missing


def extract_test_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('test "'):
            continue
        closing_quote = stripped.find('"', len('test "'))
        if closing_quote == -1:
            continue
        titles.append(stripped[: closing_quote + 1])
    return titles


def collect_missing_markers(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    string_path = root / STRING_REL
    manifest, manifest_errors = load_json(manifest_path, "phase1_string_prefix_suffix_manifest")
    if manifest_errors:
        return manifest_errors

    if not isinstance(manifest, dict):
        return ["phase1_string_prefix_suffix_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_string_prefix_suffix_manifest:review_anchors"]

    string_review = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_review, dict):
        return ["phase1_string_prefix_suffix_manifest:tools/lib/string.zig"]

    missing: list[str] = []
    if string_review.get("prefix_suffix_review_anchors") != EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS:
        missing.append("phase1_string_prefix_suffix_manifest:prefix_suffix_review_anchors")
    if string_review.get("prefix_suffix_review_summary") != EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY:
        missing.append("phase1_string_prefix_suffix_manifest:prefix_suffix_review_summary")

    source_titles = extract_test_titles(load_text(string_path))
    for anchor in EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS:
        count = source_titles.count(anchor)
        if count != 1:
            missing.append(f"phase1_string_prefix_suffix_source:{anchor}:expected=1:actual={count}")
    return missing


def make_fixture_root(root: Path) -> None:
    (root / MANIFEST_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / STRING_REL).parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "review_anchors": {
            "tools/lib/string.zig": {
                "prefix_suffix_review_anchors": EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS,
                "prefix_suffix_review_summary": EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY,
            }
        }
    }
    (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / STRING_REL).write_text(
        "\n".join(EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_prefix_suffix_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 2

        (root / MANIFEST_REL).unlink()
        assert collect_missing_files(root) == [MANIFEST_REL.as_posix()]
        case_count += 1
        make_fixture_root(root)

        (root / STRING_REL).unlink()
        assert collect_missing_files(root) == [STRING_REL.as_posix()]
        case_count += 1
        make_fixture_root(root)

        manifest_path = root / MANIFEST_REL
        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["prefix_suffix_review_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_prefix_suffix_manifest:prefix_suffix_review_summary" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        manifest = json.loads(load_text(manifest_path))
        manifest["review_anchors"]["tools/lib/string.zig"]["prefix_suffix_review_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_prefix_suffix_manifest:prefix_suffix_review_anchors" in collect_missing_markers(root)
        case_count += 1
        make_fixture_root(root)

        string_path = root / STRING_REL
        string_path.write_text(
            load_text(string_path).replace(EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS[1] + "\n", "", 1),
            encoding="utf-8",
        )
        assert any(item.startswith("phase1_string_prefix_suffix_source:") for item in collect_missing_markers(root))
        case_count += 1
        make_fixture_root(root)

        manifest_path.write_text("{\n", encoding="utf-8")
        assert any(item.startswith("phase1_string_prefix_suffix_manifest:json_decode_error:") for item in collect_missing_markers(root))
        case_count += 1

    print("PHASE1_STRING_PREFIX_SUFFIX_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_PREFIX_SUFFIX_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 1 string prefix/suffix review packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_STRING_PREFIX_SUFFIX_PACKET=fail")
        print("MISSING_PHASE1_STRING_PREFIX_SUFFIX_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_STRING_PREFIX_SUFFIX_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_STRING_PREFIX_SUFFIX_PACKET=fail")
        print("MISSING_PHASE1_STRING_PREFIX_SUFFIX_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_STRING_PREFIX_SUFFIX_MARKERS_END")
        return 1

    print("PHASE1_STRING_PREFIX_SUFFIX_PACKET=pass")
    print("PHASE1_STRING_PREFIX_SUFFIX_REQUIRED_FILE_COUNT=2")
    print(
        "PHASE1_STRING_PREFIX_SUFFIX_REQUIRED_MARKER_COUNT="
        f"{len(EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS) + 1}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
