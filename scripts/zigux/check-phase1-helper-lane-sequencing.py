#!/usr/bin/env python3
"""Validate the current Phase 1 helper lane-sequencing reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    MANIFEST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
)

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

LANE_NOTE_MARKERS = (
    "- `zigux/tests/fixtures/phase1_helper_manifest.json` is the authoritative owner-map split for all thirteen closed Phase 1 helpers",
    "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
    "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`",
)

SCRIPTS_README_MARKERS = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

TESTS_README_MARKERS = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
)


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    wanted = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == wanted)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        full_path = root / relative_path
        if not full_path.exists():
            failures.append(f"missing:{relative_path.as_posix()}")
        elif full_path.is_dir():
            failures.append(f"directory:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_note_text = read_text(root / LANE_NOTE_REL)
    scripts_readme_text = read_text(root / SCRIPTS_README_REL)
    tests_readme_text = read_text(root / TESTS_README_REL)
    try:
        manifest = load_json_with_duplicate_tracking(read_text(root / MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"manifest:duplicate_json_key:{duplicate_path}" for duplicate_path in duplicate_paths]
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    for idx, marker in enumerate(LANE_NOTE_MARKERS):
        failures.extend(require_exact_line(lane_note_text, f"lane_note:line_{idx}", marker))
    for idx, marker in enumerate(SCRIPTS_README_MARKERS):
        failures.extend(require_exact_line(scripts_readme_text, f"scripts_readme:line_{idx}", marker))
    for idx, marker in enumerate(TESTS_README_MARKERS):
        failures.extend(require_exact_line(tests_readme_text, f"tests_readme:line_{idx}", marker))

    manifest_expectations = {
        ("phase",): "Phase 1",
        ("status",): "closed",
        ("helper_count",): len(EXPECTED_HELPERS),
        ("helpers",): EXPECTED_HELPERS,
        ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
        ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
    }
    for path, expected in manifest_expectations.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(f"manifest:{'.'.join(path)}:expected={expected!r}:actual={actual!r}")

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    write_text(root, LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root, TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")


def mutate_line(root: Path, relative_path: Path, line: str, *, duplicate: bool) -> None:
    path = root / relative_path
    text = read_text(path)
    if duplicate:
        text = text.replace(line + "\n", line + "\n" + line + "\n", 1)
    else:
        text = text.replace(line + "\n", "", 1)
    path.write_text(text, encoding="utf-8")


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(read_text(manifest_path))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, callable]] = [
        ("good", lambda root: None),
        ("lane_note_missing_owner_map", lambda root: mutate_line(root, LANE_NOTE_REL, LANE_NOTE_MARKERS[0], duplicate=False)),
        ("lane_note_duplicate_direct_helpers", lambda root: mutate_line(root, LANE_NOTE_REL, LANE_NOTE_MARKERS[2], duplicate=True)),
        ("scripts_readme_missing_tie_breaker", lambda root: mutate_line(root, SCRIPTS_README_REL, SCRIPTS_README_MARKERS[1], duplicate=False)),
        ("tests_readme_missing_truthful_line", lambda root: mutate_line(root, TESTS_README_REL, TESTS_README_MARKERS[1], duplicate=False)),
        ("manifest_shared_helper_drift", lambda root: mutate_manifest(root, ("lane_sequencing", "shared_replay_parked_helpers"))),
        ("manifest_direct_helper_drift", lambda root: mutate_manifest(root, ("lane_sequencing", "direct_anchor_followup_helpers"))),
        ("manifest_rule_summary_drift", lambda root: mutate_manifest(root, ("lane_sequencing", "rule_summary"))),
        ("manifest_invalid_json", lambda root: write_text(root, MANIFEST_REL, "{\n")),
        (
            "manifest_duplicate_key",
            lambda root: write_text(
                root,
                MANIFEST_REL,
                read_text(root / MANIFEST_REL).replace(
                    '  "status": "closed",\n',
                    '  "status": "open",\n  "status": "closed",\n',
                    1,
                ),
            ),
        ),
        ("missing_required_file", lambda root: (root / TESTS_README_REL).unlink()),
    ]

    failed_cases: list[str] = []
    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-helper-lane-sequencing-{name}-") as tmp_dir:
            root = Path(tmp_dir)
            build_sample_root(root)
            mutate(root)
            failures = collect_failures(root)
            if name == "good":
                if failures:
                    failed_cases.append(name)
            elif not failures:
                failed_cases.append(name)

    if failed_cases:
        print("PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST=fail")
        for name in failed_cases:
            print(f"PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={len(cases)}")
    print(
        "PHASE1_HELPER_LANE_SEQUENCING_SELF_TEST_CASES="
        + ",".join(name for name, _ in cases)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for focused validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_HELPER_LANE_SEQUENCING_SAMPLE_ROOT=written")
        return 0
    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_HELPER_LANE_SEQUENCING=fail")
        for failure in failures:
            print(f"PHASE1_HELPER_LANE_SEQUENCING_ISSUE={failure}")
        return 1

    print("PHASE1_HELPER_LANE_SEQUENCING=pass")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_HELPER_LANE_SEQUENCING_LANE_NOTE_MARKER_COUNT={len(LANE_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())