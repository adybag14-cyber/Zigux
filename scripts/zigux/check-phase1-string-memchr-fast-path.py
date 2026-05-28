#!/usr/bin/env python3
"""Guard the Phase 1 string memchrInv fast-path review anchors."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_HELPER_ANCHORS = [
    'test "memchrInv follows the earliest dirty byte as long buffers change"',
    'test "memchrInv finds a dirty byte in the unaligned prefix before the word fast path"',
    'test "memchrInv keeps aligned word hits stable after consuming an unaligned prefix"',
    'test "memchrInv keeps non-zero scans stable across the fast-path cutoff"',
]

EXPECTED_MANIFEST_FIELDS = {
    "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
    "memchr_moving_dirty_review_summary": (
        "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one fixed dirty index "
        "and the clean case, but not the moving earliest-mismatch ownership as later dirty bytes become the next live divergence"
    ),
}

EXPECTED_LANE_MARKERS = [
    (
        "direct_owner",
        "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, "
        "matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), "
        "sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and "
        "match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), "
        "strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, "
        "and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns "
        "embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    ),
    (
        "next_safe_step",
        "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() "
        "copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or "
        "lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors "
        "through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), "
        "strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for "
        "committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned "
        "across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not "
        "reopen missing closure-side validator names by default`",
    ),
]

EXPECTED_NEXT_STEP_SUBSTRING = "moving-earliest-dirty-byte memchrInv coverage"


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    text = load_text(root, relative_path)
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


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (STRING_HELPER_REL, STRING_MANIFEST_REL, STRING_LANE_NOTE_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    lane_text = load_text(root, STRING_LANE_NOTE_REL)
    try:
        manifest = load_json(root, STRING_MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_manifest_paths]

    for anchor in EXPECTED_HELPER_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper:{anchor}", anchor))

    for key, expected in EXPECTED_MANIFEST_FIELDS.items():
        failures.extend(
            require_exact_value(
                f"manifest:review_anchors.tools/lib/string.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/string.zig", key)),
                expected,
            )
        )

    next_safe_step = nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"))
    if not isinstance(next_safe_step, str):
        failures.append("manifest:review_anchors.tools/lib/string.zig.next_safe_step_note:expected=str")
    elif EXPECTED_NEXT_STEP_SUBSTRING not in next_safe_step:
        failures.append(
            "manifest:review_anchors.tools/lib/string.zig.next_safe_step_note:missing_substring:"
            + EXPECTED_NEXT_STEP_SUBSTRING
        )

    for label, marker in EXPECTED_LANE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"lane:{label}", marker))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return json.dumps(
        {
            "review_anchors": {
                "tools/lib/string.zig": {
                    **EXPECTED_MANIFEST_FIELDS,
                    "next_safe_step_note": EXPECTED_NEXT_STEP_SUBSTRING,
                }
            }
        },
        indent=2,
    ) + "\n"


def sample_helper() -> str:
    return "\n".join(EXPECTED_HELPER_ANCHORS) + "\n"


def sample_lane_note() -> str:
    return "# sample\n\n" + "\n".join(marker for _, marker in EXPECTED_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, sample_helper())
    write_file(root, STRING_MANIFEST_REL, sample_manifest())
    write_file(root, STRING_LANE_NOTE_REL, sample_lane_note())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_memchr_") as tmp_dir:
        root = Path(tmp_dir)

        if "missing_file:tools/lib/string.zig" not in collect_failures(root):
            raise SystemExit("phase1-string-memchr:self-test:missing-helper")

        build_sample_repo(root)
        if collect_failures(root):
            raise SystemExit("phase1-string-memchr:self-test:baseline")

        helper_path = root / STRING_HELPER_REL
        helper_text = helper_path.read_text(encoding="utf-8")
        helper_path.write_text(
            helper_text.replace(EXPECTED_HELPER_ANCHORS[1] + "\n", "", 1),
            encoding="utf-8",
        )
        if not any(item.startswith("helper:") for item in collect_failures(root)):
            raise SystemExit("phase1-string-memchr:self-test:helper-anchor")

        build_sample_repo(root)
        manifest_path = root / STRING_MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["memchr_moving_dirty_review_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any("memchr_moving_dirty_review_summary" in item for item in collect_failures(root)):
            raise SystemExit("phase1-string-memchr:self-test:manifest-summary")

        build_sample_repo(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any("next_safe_step_note:missing_substring" in item for item in collect_failures(root)):
            raise SystemExit("phase1-string-memchr:self-test:manifest-next-step")

        build_sample_repo(root)
        lane_path = root / STRING_LANE_NOTE_REL
        lane_path.write_text("# drift\n", encoding="utf-8")
        if not any(item.startswith("lane:") for item in collect_failures(root)):
            raise SystemExit("phase1-string-memchr:self-test:lane-marker")

    print("PHASE1_STRING_MEMCHR_FAST_PATH_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-memchr-fast-path:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
