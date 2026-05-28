#!/usr/bin/env python3
"""Guard the shared Phase 1 helper fixture packet across docs, manifest, fixture, and smoke."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_CLOSURE_MARKERS = [
    "`PHASE1_HELPER_COUNT=13`",
    "- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "The bounded Phase 1 helper tranche is still the same thirteen helper ports named in the committed manifest, but the broader closure-side validator and replay stack is only partially promoted into the narrow current reminder packet on current `master`.",
    "Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only: `zigux/tests/fixtures/phase1_helpers.json` still records the exact cached-root erase, replacement, and detach transition packet, and `zigux/tests/phase1_host_tools_smoke.zig` already rechecks the same `[0, 0, 4, 2]` sequence beside the parked `cached_leftmost_return_serials` witness. Treat that transition packet as landed shared closure evidence for future cached-root rereads, while still leaving the remaining insert-miss, leftmost-sync, alias, singleton-erase, replacement, detach, and reseed anchors helper-local until another broader replay field lands.",
]

EXPECTED_LANE_MARKERS = [
    "- `zigux/tests/fixtures/phase1_helper_manifest.json` is the authoritative owner-map split for all thirteen closed Phase 1 helpers",
    "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped findFirstAndNotBit(), findNextAndNotBit(), find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`",
]

EXPECTED_SMOKE_MARKERS = [
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
]

EXPECTED_MANIFEST_FIELDS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): 13,
    ("helpers",): EXPECTED_HELPERS,
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
    ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
    ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
}

EXPECTED_FIXTURE_FIELDS = {
    ("argv_split", "argc"): 3,
    ("argv_split", "blank_argc"): 0,
    ("bitmap", "copy_clear_tail_values"): [18446744073709551615, 31],
    ("bitmap", "partial_xor_masked_values"): [14],
    ("cmdline", "decimal_k", "value"): 65536,
    ("cmdline", "second_arg", "value"): "/dev/sda1 quiet",
    ("ctype", "mask_A"): 65,
    ("ctype", "toupper_z"): 90,
    ("find_bit", "first_and"): 9,
    ("find_bit", "last"): 71,
    ("hweight", "w64"): 32,
    ("list_sort", "tri_sorted_ordinals"): [1, 3, 0, 2, 4],
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("rbtree", "cached_root_transition_serials"): [0, 0, 4, 2],
    ("slab", "alloc_count_after_kmalloc"): 1,
    ("slab", "alloc_count_after_kmalloc_free"): 0,
    ("str_error_r", "enoent"): "No such file or directory",
    ("string", "replace_char_cstr_bytes"): [97, 95, 0, 45, 122],
    ("string", "memchr_inv_none"): True,
    ("vsprintf", "scnprintf_text"): "zigux:7",
    ("vsprintf", "pad_text"): "id=7    ",
    ("zalloc", "zeroed"): True,
    ("zalloc", "value_freed_is_null"): True,
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
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

    for relative_path in (
        PHASE1_CLOSURE_REL,
        PHASE1_LANE_NOTE_REL,
        MANIFEST_REL,
        FIXTURE_REL,
        SMOKE_REL,
    ):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = read_text(root, PHASE1_CLOSURE_REL)
    lane_text = read_text(root, PHASE1_LANE_NOTE_REL)
    smoke_text = read_text(root, SMOKE_REL)

    try:
        manifest = load_json_with_duplicate_tracking(read_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    try:
        fixture = load_json_with_duplicate_tracking(read_text(root, FIXTURE_REL))
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

    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_exact_occurrence(closure_text, f"closure:{marker}", marker))
    for marker in EXPECTED_LANE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"lane:{marker}", marker))
    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(smoke_text, f"smoke:{marker}", marker))

    for path, expected in EXPECTED_MANIFEST_FIELDS.items():
        failures.extend(require_exact_value(f"manifest:{'.'.join(path)}", nested_value(manifest, path), expected))
    for path, expected in EXPECTED_FIXTURE_FIELDS.items():
        failures.extend(require_exact_value(f"fixture:{'.'.join(path)}", nested_value(fixture, path), expected))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return json.dumps(
        {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": 13,
            "helpers": EXPECTED_HELPERS,
            "lane_sequencing": {
                "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                "rule_summary": EXPECTED_RULE_SUMMARY,
                "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
            },
        },
        indent=2,
    ) + "\n"


def sample_fixture() -> str:
    data: dict[str, Any] = {}
    for path, value in EXPECTED_FIXTURE_FIELDS.items():
        cursor = data
        for key in path[:-1]:
            cursor = cursor.setdefault(key, {})
        cursor[path[-1]] = value
    return json.dumps(data, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(root, PHASE1_CLOSURE_REL, "# sample\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n")
    write_text(root, PHASE1_LANE_NOTE_REL, "# sample\n\n" + "\n".join(EXPECTED_LANE_MARKERS) + "\n")
    write_text(root, MANIFEST_REL, sample_manifest())
    write_text(root, FIXTURE_REL, sample_fixture())
    write_text(root, SMOKE_REL, "\n".join(EXPECTED_SMOKE_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        "baseline",
        "missing_fixture",
        "missing_closure_marker",
        "missing_lane_marker",
        "missing_smoke_marker",
        "manifest_helper_count_drift",
        "manifest_direct_anchor_set_drift",
        "fixture_rbtree_drift",
        "fixture_string_drift",
        "manifest_invalid_json",
        "fixture_invalid_json",
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-helper-fixture-packet-") as tmpdir:
        root = Path(tmpdir)

        write_sample_root(root)
        assert collect_failures(root) == []

        (root / FIXTURE_REL).unlink()
        assert f"missing_file:{FIXTURE_REL.as_posix()}" in collect_failures(root)

        write_sample_root(root)
        closure_path = root / PHASE1_CLOSURE_REL
        closure_text = closure_path.read_text(encoding="utf-8").replace(EXPECTED_CLOSURE_MARKERS[2] + "\n", "", 1)
        closure_path.write_text(closure_text, encoding="utf-8")
        assert any(item.startswith("closure:") for item in collect_failures(root))

        write_sample_root(root)
        lane_path = root / PHASE1_LANE_NOTE_REL
        lane_text = lane_path.read_text(encoding="utf-8").replace(EXPECTED_LANE_MARKERS[3] + "\n", "", 1)
        lane_path.write_text(lane_text, encoding="utf-8")
        assert any(item.startswith("lane:") for item in collect_failures(root))

        write_sample_root(root)
        smoke_path = root / SMOKE_REL
        smoke_text = smoke_path.read_text(encoding="utf-8").replace(EXPECTED_SMOKE_MARKERS[4] + "\n", "", 1)
        smoke_path.write_text(smoke_text, encoding="utf-8")
        assert any(item.startswith("smoke:") for item in collect_failures(root))

        write_sample_root(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["helper_count"] = 12
        (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "manifest:helper_count:expected=13:actual=12" in collect_failures(root)

        write_sample_root(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/bitmap.zig"]
        (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert any(item.startswith("manifest:lane_sequencing.direct_anchor_followup_helpers") for item in collect_failures(root))

        write_sample_root(root)
        fixture = json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))
        fixture["rbtree"]["cached_root_transition_serials"] = [0, 0, 4, 3]
        (root / FIXTURE_REL).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert any(item.startswith("fixture:rbtree.cached_root_transition_serials") for item in collect_failures(root))

        write_sample_root(root)
        fixture = json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))
        fixture["string"]["replace_char_cstr_bytes"] = [97, 95, 0]
        (root / FIXTURE_REL).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert any(item.startswith("fixture:string.replace_char_cstr_bytes") for item in collect_failures(root))

        write_sample_root(root)
        (root / MANIFEST_REL).write_text("{\n", encoding="utf-8")
        assert any(item.startswith("manifest:invalid_json:") for item in collect_failures(root))

        write_sample_root(root)
        (root / FIXTURE_REL).write_text("{\n", encoding="utf-8")
        assert any(item.startswith("fixture:invalid_json:") for item in collect_failures(root))

    print("PHASE1_HELPER_FIXTURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HELPER_FIXTURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_HELPER_FIXTURE_PACKET_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_FIXTURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_FIXTURE_PACKET=pass")
    print(f"PHASE1_HELPER_FIXTURE_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_HELPER_FIXTURE_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_HELPER_FIXTURE_PACKET_REQUIRED_FILE_COUNT=5")
    print(f"PHASE1_HELPER_FIXTURE_PACKET_REQUIRED_FIXTURE_FIELD_COUNT={len(EXPECTED_FIXTURE_FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
