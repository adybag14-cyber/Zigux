#!/usr/bin/env python3
"""Guard the Phase 1 string memtostr review-rule packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_HELPER_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "memcpy_and_pad mirrors memcpyAndPad padding semantics"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
]

EXPECTED_COPY_FILL_REVIEW_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
]

EXPECTED_COPY_FILL_REVIEW_SUMMARY = (
    "helper-local raw-copy and pad anchors stay explicit through the direct string tests because "
    "the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), strtomem(), or "
    "strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, and caller-selected pad "
    "behavior remain review-visible at the helper surface"
)

EXPECTED_MEMTOSTR_REVIEW_ANCHORS = [
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
]

EXPECTED_MEMTOSTR_REVIEW_SUMMARY = (
    "helper-local memtostr boundary and tail-padding anchors stay explicit through the direct "
    "string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), "
    "memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL "
    "stops, terminator insertion, and zero-padded destination tails remain review-visible at the "
    "helper surface"
)

EXPECTED_LANE_NOTE_MARKER = (
    "- the same string-local packet also keeps helper-local byte-copy and pad coverage explicit "
    "through `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, `strtomem_pad()`, "
    "`memtostr()`, `memtostrPad()`, and `memtostr_pad()`, with direct tests for requested-prefix "
    "copying, first-NUL truncation, terminator insertion, and destination-tail padding, so "
    "future string-only rereads should keep those anchors in the same helper-local packet until "
    "dedicated shared fixture keys land."
)

def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_files = (
        STRING_HELPER_REL,
        STRING_REVIEW_CHECKER_REL,
        PHASE1_LANE_NOTE_REL,
        MANIFEST_REL,
    )
    for rel in required_files:
        if not (root / rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    review_checker_text = load_text(root, STRING_REVIEW_CHECKER_REL)
    lane_note_text = load_text(root, PHASE1_LANE_NOTE_REL)

    try:
        manifest = load_json_with_duplicate_tracking(load_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    for anchor in EXPECTED_HELPER_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))

    for anchor in EXPECTED_COPY_FILL_REVIEW_ANCHORS:
        failures.extend(require_exact_occurrence(review_checker_text, f"review_checker:copy_fill_anchor:{anchor}", anchor))
    failures.extend(
        require_exact_occurrence(
            review_checker_text,
            "review_checker:copy_fill_summary",
            EXPECTED_COPY_FILL_REVIEW_SUMMARY,
        )
    )

    for anchor in EXPECTED_MEMTOSTR_REVIEW_ANCHORS:
        failures.extend(require_exact_occurrence(review_checker_text, f"review_checker:memtostr_anchor:{anchor}", anchor))
    failures.extend(
        require_exact_occurrence(
            review_checker_text,
            "review_checker:memtostr_summary",
            EXPECTED_MEMTOSTR_REVIEW_SUMMARY,
        )
    )

    failures.extend(require_exact_occurrence(lane_note_text, "lane_note:memtostr_rule", EXPECTED_LANE_NOTE_MARKER))

    review_anchor_prefix = ("review_anchors", "tools/lib/string.zig")
    failures.extend(
        require_exact_value(
            "manifest:copy_fill_review_anchors",
            nested_value(manifest, review_anchor_prefix + ("copy_fill_review_anchors",)),
            EXPECTED_COPY_FILL_REVIEW_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:copy_fill_review_summary",
            nested_value(manifest, review_anchor_prefix + ("copy_fill_review_summary",)),
            EXPECTED_COPY_FILL_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:memtostr_review_anchors",
            nested_value(manifest, review_anchor_prefix + ("memtostr_review_anchors",)),
            EXPECTED_MEMTOSTR_REVIEW_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:memtostr_review_summary",
            nested_value(manifest, review_anchor_prefix + ("memtostr_review_summary",)),
            EXPECTED_MEMTOSTR_REVIEW_SUMMARY,
        )
    )

    return failures


def write_text(root: Path, rel: Path, text: str) -> None:
    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def build_sample_tree(root: Path) -> None:
    write_text(root, STRING_HELPER_REL, "\n".join(EXPECTED_HELPER_ANCHORS) + "\n")
    write_text(
        root,
        STRING_REVIEW_CHECKER_REL,
        "\n".join(
            EXPECTED_COPY_FILL_REVIEW_ANCHORS
            + [EXPECTED_COPY_FILL_REVIEW_SUMMARY]
            + EXPECTED_MEMTOSTR_REVIEW_ANCHORS
            + [EXPECTED_MEMTOSTR_REVIEW_SUMMARY]
        )
        + "\n",
    )
    write_text(root, PHASE1_LANE_NOTE_REL, EXPECTED_LANE_NOTE_MARKER + "\n")
    write_text(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": {
                        "copy_fill_review_anchors": EXPECTED_COPY_FILL_REVIEW_ANCHORS,
                        "copy_fill_review_summary": EXPECTED_COPY_FILL_REVIEW_SUMMARY,
                        "memtostr_review_anchors": EXPECTED_MEMTOSTR_REVIEW_ANCHORS,
                        "memtostr_review_summary": EXPECTED_MEMTOSTR_REVIEW_SUMMARY,
                    }
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("missing_helper_anchor", "helper_anchor:test \"memtostrPad zero-pads the remaining tail after copying\":expected=1:actual=0"),
        ("duplicate_helper_anchor", "helper_anchor:test \"memtostr copies a bounded non-NUL source and adds one terminator\":expected=1:actual=2"),
        ("missing_review_summary", "review_checker:memtostr_summary:expected=1:actual=0"),
        ("missing_lane_note", "lane_note:memtostr_rule:expected=1:actual=0"),
        ("manifest_drift", "manifest:memtostr_review_summary:expected="),
        ("manifest_duplicate_key", "zigux/tests/fixtures/phase1_helper_manifest.json:duplicate_json_key:review_anchors.tools/lib/string.zig.memtostr_review_summary"),
    ]

    with tempfile.TemporaryDirectory(prefix="phase1_string_memtostr_review_rule_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_tree(root)
        baseline_failures = collect_failures(root)
        if baseline_failures:
            print(f"phase1-string-memtostr-review-rule:self-test:baseline:{baseline_failures}")
            return 1

        helper_path = root / STRING_HELPER_REL
        review_checker_path = root / STRING_REVIEW_CHECKER_REL
        lane_note_path = root / PHASE1_LANE_NOTE_REL
        manifest_path = root / MANIFEST_REL

        helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'test "memtostrPad zero-pads the remaining tail after copying"\n', "", 1
            ),
            encoding="utf-8",
        )
        if cases[0][1] not in collect_failures(root):
            print("phase1-string-memtostr-review-rule:self-test:missing_helper_anchor")
            return 1

        build_sample_tree(root)
        anchor = 'test "memtostr copies a bounded non-NUL source and adds one terminator"'
        helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(anchor + "\n", anchor + "\n" + anchor + "\n", 1),
            encoding="utf-8",
        )
        if cases[1][1] not in collect_failures(root):
            print("phase1-string-memtostr-review-rule:self-test:duplicate_helper_anchor")
            return 1

        build_sample_tree(root)
        review_checker_path.write_text(
            review_checker_path.read_text(encoding="utf-8").replace(EXPECTED_MEMTOSTR_REVIEW_SUMMARY + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[2][1] not in collect_failures(root):
            print("phase1-string-memtostr-review-rule:self-test:missing_review_summary")
            return 1

        build_sample_tree(root)
        lane_note_path.write_text("", encoding="utf-8")
        if cases[3][1] not in collect_failures(root):
            print("phase1-string-memtostr-review-rule:self-test:missing_lane_note")
            return 1

        build_sample_tree(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["memtostr_review_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        manifest_failures = collect_failures(root)
        if not any(item.startswith(cases[4][1]) for item in manifest_failures):
            print("phase1-string-memtostr-review-rule:self-test:manifest_drift")
            return 1

        build_sample_tree(root)
        manifest_text = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            manifest_text.replace(
                '      "memtostr_review_summary": ',
                '      "memtostr_review_summary": "drift",\n      "memtostr_review_summary": ',
                1,
            ),
            encoding="utf-8",
        )
        if cases[5][1] not in collect_failures(root):
            print("phase1-string-memtostr-review-rule:self-test:manifest_duplicate_key")
            return 1

    print("PHASE1_STRING_MEMTOSTR_REVIEW_RULE_SELF_TEST=pass")
    print(f"PHASE1_STRING_MEMTOSTR_REVIEW_RULE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", help="write a sample root for checker replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_tree(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-string-memtostr-review-rule:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
