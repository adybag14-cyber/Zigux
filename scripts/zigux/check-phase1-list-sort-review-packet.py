#!/usr/bin/env python3
"""Guard the Phase 1 list_sort review packet against helper, manifest, fixture, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
LIST_SORT_HELPER_REL = Path("tools/lib/list_sort.zig")
LIST_SORT_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
LIST_SORT_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
LIST_SORT_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_LIST_SORT_SOURCE_SYMBOLS = [
    "pub const ListHead = struct {",
    "pub const CmpFn = *const fn (?*anyopaque, *const ListHead, *const ListHead) i32;",
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
]

EXPECTED_HELPER_LOCAL_ONLY_ANCHORS = [
    'test "list sort accepts non-unit comparator magnitudes"',
    'test "list sort honors comparator context with non-unit magnitudes"',
    'test "list sort reuses non-unit comparator context across repeated reordering"',
    'test "list sort accepts signed subtractive comparator"',
    'test "list sort reuses signed subtractive comparator context across repeated reordering"',
    'test "list sort preserves current signed-subtractive order when a later pass ties everything"',
]

EXPECTED_LIST_SORT_PACKET = {
    "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
    "phase1_helper_replay_anchor": 'test "phase 1 helper ports match committed parity fixture"',
    "parity_fixture_keys": [
        "tri_sorted_keys",
        "tri_sorted_ordinals",
        "bool_sorted_keys",
        "bool_sorted_ordinals",
    ],
    "shared_replay_summary": "the committed Phase 1 fixture still owns the tri-state and boolean-style comparator parity keys for list_sort, while current master keeps comparator-context handling, repeat-sort circular-list integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, and empty-or-singleton handling explicit at the helper surface until the broader shared replay packet returns",
    "comparator_context_anchor": 'test "list sort honors comparator context"',
    "repeat_sort_anchor": 'test "list sort can reorder the same circular list twice"',
    "reverse_link_anchor": 'test "list sort keeps reverse links aligned after reordering"',
    "sorted_input_anchor": 'test "list sort preserves sorted unique input"',
    "parity_bucket_anchor": 'test "list sort preserves stable bucket order across parity groups"',
    "modulo_bucket_anchor": 'test "list sort preserves stable modulo bucket order across a longer merge path"',
    "all_ties_anchor": 'test "list sort preserves input order when every comparison ties"',
    "empty_singleton_anchor": 'test "list sort handles empty and singleton lists"',
    "review_packet_summary": "keep list_sort parked in the shared-replay helper family for fixture ownership, but reread the helper-local proof packet before reopening the lane: current master already names direct witnesses for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, and empty-or-singleton handling beside the committed parity keys",
    "next_safe_step_note": "If this helper lane reopens, keep list_sort parked unless a fresh reread finds drift in the committed `tri_sorted_*` or `bool_sorted_*` fixture keys, or in the current helper-local anchors for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, or empty-or-singleton handling; do not widen into the missing shared replay stack by default.",
}

EXPECTED_LIST_SORT_FIXTURE_VALUES = {
    "tri_sorted_keys": [1, 1, 2, 3, 3],
    "tri_sorted_ordinals": [1, 3, 0, 2, 4],
    "bool_sorted_keys": [1, 1, 2, 3, 3],
    "bool_sorted_ordinals": [1, 3, 0, 2, 4],
}

EXPECTED_LIST_SORT_LANE_MARKERS = [
    (
        "lane_helper_local_packet",
        "- `tools/lib/list_sort.zig` stays in the shared-replay parked family, but current `master` still keeps comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, non-unit comparator magnitude handling, signed subtractive comparator behavior, repeated reorder stability, and empty-or-singleton handling explicit in the helper-local proof packet beside the committed tri_sorted_* and bool_sorted_* fixture keys.",
    ),
    (
        "lane_next_safe_step",
        "- `PHASE1_LIST_SORT_NEXT_SAFE_STEP=list_sort reopens only for shared replay or reminder-surface drift in the committed tri_sorted_* or bool_sorted_* fixture keys, or for drift in the helper-local comparator-context, repeat-sort, reverse-link, sorted-input, parity-bucket, modulo-bucket, all-ties, non-unit comparator, signed subtractive comparator, repeated reorder, or empty-or-singleton anchors; do not widen into neighboring shared-replay parked helpers by default.`",
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(root: Path, relative_path: Path) -> object:
    return load_json_with_duplicate_tracking(load_text(root, relative_path))


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


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
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
    for relative_path in (
        LIST_SORT_HELPER_REL,
        LIST_SORT_MANIFEST_REL,
        LIST_SORT_FIXTURE_REL,
        LIST_SORT_LANE_NOTE_REL,
    ):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, LIST_SORT_HELPER_REL)
    lane_text = load_text(root, LIST_SORT_LANE_NOTE_REL)

    try:
        manifest = load_json(root, LIST_SORT_MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    try:
        fixture = load_json(root, LIST_SORT_FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [f"fixture:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_manifest_paths]

    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]
    duplicate_fixture_paths = collect_duplicate_json_key_paths(fixture)
    if duplicate_fixture_paths:
        return [f"fixture:duplicate_json_key:{path}" for path in duplicate_fixture_paths]

    for symbol in EXPECTED_LIST_SORT_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"list_sort_source:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"list_sort_helper:{anchor}", anchor))
    for anchor in EXPECTED_HELPER_LOCAL_ONLY_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"list_sort_helper_local:{anchor}", anchor))

    for label, marker in EXPECTED_LIST_SORT_LANE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"list_sort_lane:{label}", marker))

    failures.extend(
        require_exact_value(
            "list_sort_manifest:review_anchors.tools/lib/list_sort.zig.helper_test_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/list_sort.zig", "helper_test_anchors")),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_LIST_SORT_PACKET.items():
        if key == "helper_test_anchors":
            continue
        failures.extend(
            require_exact_value(
                f"list_sort_manifest:review_anchors.tools/lib/list_sort.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/list_sort.zig", key)),
                expected,
            )
        )

    list_sort_fixture = fixture.get("list_sort")
    if not isinstance(list_sort_fixture, dict):
        return [f"list_sort_fixture:expected=dict:actual={type(list_sort_fixture).__name__}"]
    for key, expected in EXPECTED_LIST_SORT_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"list_sort_fixture:{key}", list_sort_fixture.get(key), expected))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_helper_source() -> str:
    lines = EXPECTED_LIST_SORT_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS + EXPECTED_HELPER_LOCAL_ONLY_ANCHORS
    return "\n".join(lines) + "\n"


def sample_manifest() -> str:
    return json.dumps({"review_anchors": {"tools/lib/list_sort.zig": EXPECTED_LIST_SORT_PACKET}}, indent=2) + "\n"


def sample_fixture() -> str:
    return json.dumps({"list_sort": EXPECTED_LIST_SORT_FIXTURE_VALUES}, indent=2) + "\n"


def sample_lane_note() -> str:
    return "# sample\n\n" + "\n".join(marker for _, marker in EXPECTED_LIST_SORT_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, LIST_SORT_HELPER_REL, sample_helper_source())
    write_file(root, LIST_SORT_MANIFEST_REL, sample_manifest())
    write_file(root, LIST_SORT_FIXTURE_REL, sample_fixture())
    write_file(root, LIST_SORT_LANE_NOTE_REL, sample_lane_note())


def insert_duplicate_json_line(root: Path, relative_path: Path, needle: str, duplicate_line: str) -> None:
    json_path = root / relative_path
    text = json_path.read_text(encoding="utf-8")
    json_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_list_sort_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        if "missing_file:tools/lib/list_sort.zig" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:missing_helper_file")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:baseline")

        helper_path = tmp_root / LIST_SORT_HELPER_REL
        manifest_path = tmp_root / LIST_SORT_MANIFEST_REL
        fixture_path = tmp_root / LIST_SORT_FIXTURE_REL
        lane_path = tmp_root / LIST_SORT_LANE_NOTE_REL

        helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'test "list sort accepts signed subtractive comparator"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        if 'list_sort_helper_local:test "list sort accepts signed subtractive comparator":expected=1:actual=0' not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:signed_subtractive_anchor")

        build_sample_repo(tmp_root)
        helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'test "list sort accepts boolean-style comparator"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        if 'list_sort_helper:test "list sort accepts boolean-style comparator":expected=1:actual=0' not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:boolean_anchor")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/list_sort.zig"]["review_packet_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any(item.startswith("list_sort_manifest:review_anchors.tools/lib/list_sort.zig.review_packet_summary:expected=") for item in collect_failures(tmp_root)):
            raise SystemExit("phase1-list-sort-review:self-test:manifest_summary_drift")

        build_sampleRepo = build_sample_repo
        build_sampleRepo(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["list_sort"]["tri_sorted_ordinals"] = [0, 1, 2, 3, 4]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if "list_sort_fixture:tri_sorted_ordinals:expected=[1, 3, 0, 2, 4]:actual=[0, 1, 2, 3, 4]" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:fixture_drift")

        build_sampleRepo(tmp_root)
        lane_marker = EXPECTED_LIST_SORT_LANE_MARKERS[1][1]
        lane_path.write_text(lane_path.read_text(encoding="utf-8").replace(lane_marker + "\n", "", 1), encoding="utf-8")
        if f"list_sort_lane:{EXPECTED_LIST_SORT_LANE_MARKERS[1][0]}:expected=1:actual=0" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:lane_marker")

        build_sampleRepo(tmp_root)
        manifest_path.write_text("{\n", encoding="utf-8")
        if "manifest:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:manifest_invalid_json")

        build_sampleRepo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            LIST_SORT_MANIFEST_REL,
            '      "review_packet_summary": "keep list_sort parked in the shared-replay helper family for fixture ownership, but reread the helper-local proof packet before reopening the lane: current master already names direct witnesses for comparator-context ordering, repeat-sort circular integrity, reverse-link alignment, sorted-input idempotence, parity-bucket stability, longer modulo-bucket stability, all-ties stability, and empty-or-singleton handling beside the committed parity keys",',
            '      "review_packet_summary": "drift",',
        )
        if "manifest:duplicate_json_key:review_anchors.tools/lib/list_sort.zig.review_packet_summary" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:manifest_duplicate_json_key")

        build_sampleRepo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            LIST_SORT_FIXTURE_REL,
            '    "tri_sorted_keys": [',
            '    "tri_sorted_keys": [9],',
        )
        if "fixture:duplicate_json_key:list_sort.tri_sorted_keys" not in collect_failures(tmp_root):
            raise SystemExit("phase1-list-sort-review:self-test:fixture_duplicate_json_key")

    print("PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST=pass")
    print("PHASE1_LIST_SORT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=8")
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
