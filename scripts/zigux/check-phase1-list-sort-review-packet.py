#!/usr/bin/env python3
"""Guard the Phase 1 list_sort review packet against helper, fixture, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/list_sort.zig")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_SOURCE_SYMBOLS = [
    "pub fn listEmpty(head: *const ListHead) bool {",
    "pub fn listAdd(new: *ListHead, head: *ListHead) void {",
    "pub fn listAddTail(new: *ListHead, head: *ListHead) void {",
    "pub fn listDel(entry: *ListHead) void {",
    "pub fn listSort(priv: ?*anyopaque, head: *ListHead, cmp: CmpFn) void {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "list sort keeps stable ordering for tri-state comparator"',
    'test "list sort accepts boolean-style comparator"',
    'test "list sort honors comparator context"',
    'test "list sort can reorder the same circular list twice"',
    'test "list sort keeps reverse links aligned after reordering"',
    'test "list sort preserves sorted unique input"',
    'test "list sort preserves stable bucket order across parity groups"',
    'test "list sort preserves stable modulo bucket order across a longer merge path"',
    'test "list sort preserves input order when every comparison ties"',
    'test "list sort handles empty and singleton lists"',
    'test "list sort accepts non-unit comparator magnitudes"',
    'test "list sort honors comparator context with non-unit magnitudes"',
    'test "list sort reuses non-unit comparator context across repeated reordering"',
    'test "list sort accepts signed subtractive comparator"',
    'test "list sort reuses signed subtractive comparator context across repeated reordering"',
    'test "list sort preserves current signed-subtractive order when a later pass ties everything"',
]

EXPECTED_FIXTURE_VALUES = {
    "tri_sorted_keys": [1, 1, 2, 3, 3],
    "tri_sorted_ordinals": [1, 3, 0, 2, 4],
    "bool_sorted_keys": [1, 1, 2, 3, 3],
    "bool_sorted_ordinals": [1, 3, 0, 2, 4],
}

EXPECTED_LANE_MARKERS = [
    (
        "list_sort_owner_note",
        "- `tools/lib/list_sort.zig` stays in the shared-replay parked family, but current `master` still keeps comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, non-unit comparator magnitude handling, signed subtractive comparator behavior, repeated reorder stability, and empty-or-singleton handling explicit in the helper-local proof packet beside the committed tri_sorted_* and bool_sorted_* fixture keys.",
    ),
    (
        "list_sort_next_safe_step",
        "- `PHASE1_LIST_SORT_NEXT_SAFE_STEP=list_sort reopens only for shared replay or reminder-surface drift in the committed tri_sorted_* or bool_sorted_* fixture keys, or for drift in the helper-local comparator-context, repeat-sort, reverse-link, sorted-input, parity-bucket, modulo-bucket, all-ties, non-unit comparator, signed subtractive comparator, repeated reorder, or empty-or-singleton anchors; do not widen into neighboring shared-replay parked helpers by default.`",
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


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


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (HELPER_REL, FIXTURE_REL, LANE_NOTE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    try:
        fixture = load_json_with_duplicate_tracking(load_text(root, FIXTURE_REL))
    except json.JSONDecodeError as exc:
        return [f"fixture:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]
    duplicate_fixture_paths = collect_duplicate_json_key_paths(fixture)
    if duplicate_fixture_paths:
        return [f"fixture:duplicate_json_key:{path}" for path in duplicate_fixture_paths]

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"list_sort_source:{symbol}", symbol))
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"list_sort_helper:{anchor}", anchor))
    for label, marker in EXPECTED_LANE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"list_sort_lane:{label}", marker))
    fixture_list_sort = fixture.get("list_sort")
    if not isinstance(fixture_list_sort, dict):
        return ["list_sort_fixture:expected=dict:actual=missing"]
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"list_sort_fixture:{key}", fixture_list_sort.get(key), expected))
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_helper_source() -> str:
    return "\n".join(EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, sample_helper_source())
    write_file(root, FIXTURE_REL, json.dumps({"list_sort": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n")
    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(marker for _, marker in EXPECTED_LANE_MARKERS) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_list_sort_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        if "missing_file:tools/lib/list_sort.zig" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:missing_helper_file")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:baseline")

        helper_path = tmp_root / HELPER_REL
        lane_path = tmp_root / LANE_NOTE_REL
        fixture_path = tmp_root / FIXTURE_REL

        helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'test "list sort accepts signed subtractive comparator"\n', "", 1
            ),
            encoding="utf-8",
        )
        if not any(
            item.startswith('list_sort_helper:test "list sort accepts signed subtractive comparator"')
            for item in collect_failures(tmp_root)
        ):
            raise SystemExit("phase1-list-sort-review:self-test:signed_subtractive_anchor")

        build_sample_repo(tmp_root)
        lane_marker = EXPECTED_LANE_MARKERS[1][1]
        lane_path.write_text(
            lane_path.read_text(encoding="utf-8").replace(lane_marker + "\n", "", 1),
            encoding="utf-8",
        )
        if not any(
            item.startswith("list_sort_lane:list_sort_next_safe_step")
            for item in collect_failures(tmp_root)
        ):
            raise SystemExit("phase1-list-sort-review:self-test:lane_note")

        build_sample_repo(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["list_sort"]["bool_sorted_ordinals"] = [0, 1]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if "list_sort_fixture:bool_sorted_ordinals:expected=[1, 3, 0, 2, 4]:actual=[0, 1]" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:fixture_drift")

    print("PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=4")
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

    print("phase1-list-sort-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())