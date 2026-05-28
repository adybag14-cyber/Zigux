#!/usr/bin/env python3
"""Guard the Phase 1 lane-sequencing helper split against note or manifest drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

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

REQUIRED_LINE_MARKERS = [
    "Current `master` keeps the closed Phase 1 helper packet split into two non-overlapping follow-up families.",
    "- `tools/lib/argv_split.zig`",
    "- `tools/lib/cmdline.zig`",
    "- `tools/lib/ctype.zig`",
    "- `tools/lib/hweight.zig`",
    "- `tools/lib/list_sort.zig`",
    "- `tools/lib/slab.zig`",
    "- `tools/lib/str_error_r.zig`",
    "- `tools/lib/vsprintf.zig`",
    "- `tools/lib/zalloc.zig`",
    "- `tools/lib/bitmap.zig`",
    "- `tools/lib/find_bit.zig`",
    "- `tools/lib/rbtree.zig`",
    "- `tools/lib/string.zig`",
    "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    f"- `PHASE1_LANE_RULE_SUMMARY={EXPECTED_RULE_SUMMARY}`",
    f"- `PHASE1_LANE_ANTI_OVERLAP_RULE={EXPECTED_ANTI_OVERLAP_RULE}`",
    "- Do not batch helpers across the shared-replay parked and direct-anchor follow-up families in one run.",
    "- Shared-replay parked helpers reopen only for packet drift, fixture drift, build-route drift, or review-surface truthfulness.",
    "- Direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
    "- Even inside the direct-anchor set, pick one helper family per run; do not batch `bitmap`, `find_bit`, `rbtree`, and `string` together in the same reopen step.",
]

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
    ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
    ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
}


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


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    want = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == want)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (LANE_NOTE_REL, MANIFEST_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_note_text = load_text(root, LANE_NOTE_REL)
    for idx, line in enumerate(REQUIRED_LINE_MARKERS):
        failures.extend(
            require_exact_line(
                lane_note_text,
                f"{LANE_NOTE_REL.as_posix()}:line_{idx}",
                line,
            )
        )

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [
            f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ]
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    for path, expected in MANIFEST_EXPECTATIONS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}",
                nested_value(manifest, path),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_lane_note() -> str:
    return """# Phase 1 Host-Helper Lane Sequencing

## Current Split

Current `master` keeps the closed Phase 1 helper packet split into two non-overlapping follow-up families.

### Shared-Replay Parked Helpers

- `tools/lib/argv_split.zig`
- `tools/lib/cmdline.zig`
- `tools/lib/ctype.zig`
- `tools/lib/hweight.zig`
- `tools/lib/list_sort.zig`
- `tools/lib/slab.zig`
- `tools/lib/str_error_r.zig`
- `tools/lib/vsprintf.zig`
- `tools/lib/zalloc.zig`

### Direct-Anchor Follow-Up Helpers

- `tools/lib/bitmap.zig`
- `tools/lib/find_bit.zig`
- `tools/lib/rbtree.zig`
- `tools/lib/string.zig`

- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`
- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`
- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`
- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`

## Anti-Overlap Rules

- Do not batch helpers across the shared-replay parked and direct-anchor follow-up families in one run.
- Shared-replay parked helpers reopen only for packet drift, fixture drift, build-route drift, or review-surface truthfulness.
- Direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.
- Even inside the direct-anchor set, pick one helper family per run; do not batch `bitmap`, `find_bit`, `rbtree`, and `string` together in the same reopen step.
"""


def sample_manifest() -> str:
    data = {
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        }
    }
    return json.dumps(data, indent=2) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, LANE_NOTE_REL, sample_lane_note())
    write_file(root, MANIFEST_REL, sample_manifest())


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_manifest_line(root: Path, needle: str, duplicate_line: str) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str, object | None]] = [("success", "none", None)]

    for relative_path in (LANE_NOTE_REL, MANIFEST_REL):
        cases.append((f"missing_file:{relative_path.as_posix()}", "remove_file", relative_path))

    for idx, line in enumerate(REQUIRED_LINE_MARKERS):
        cases.append((f"missing_line:{idx}", "remove_line", line))
        cases.append((f"duplicate_line:{idx}", "duplicate_line", line))

    for path in MANIFEST_EXPECTATIONS:
        cases.append((f"manifest_drift:{'.'.join(path)}", "mutate_manifest", path))

    cases.append(("duplicate_manifest_key", "duplicate_manifest_key", None))

    for name, mode, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mode == "remove_file" and isinstance(payload, Path):
                (root / payload).unlink()
            elif mode == "remove_line" and isinstance(payload, str):
                target = root / LANE_NOTE_REL
                lines = target.read_text(encoding="utf-8").splitlines()
                stripped = payload.strip()
                for index, line in enumerate(lines):
                    if line.strip() == stripped:
                        del lines[index]
                        target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                        break
            elif mode == "duplicate_line" and isinstance(payload, str):
                target = root / LANE_NOTE_REL
                lines = target.read_text(encoding="utf-8").splitlines()
                stripped = payload.strip()
                for index, line in enumerate(lines):
                    if line.strip() == stripped:
                        lines.insert(index + 1, line)
                        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
                        break
            elif mode == "mutate_manifest" and isinstance(payload, tuple):
                mutate_manifest(root, payload)
            elif mode == "duplicate_manifest_key":
                insert_duplicate_manifest_line(
                    root,
                    '    "rule_summary": "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",',
                    '    "rule_summary": "drifted rule summary",',
                )

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_LANE_SEQUENCING_SPLIT_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_SPLIT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(destination: Path) -> None:
    destination = destination.resolve()
    build_sample_repo(destination)
    print(f"PHASE1_LANE_SEQUENCING_SPLIT_SAMPLE_ROOT={destination}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-test")
    parser.add_argument("--write-sample-root", help="write a minimal passing sample repository root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root))
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_LANE_SEQUENCING_SPLIT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING_SPLIT=pass")
    print(f"PHASE1_LANE_SEQUENCING_SPLIT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}")
    print(f"PHASE1_LANE_SEQUENCING_SPLIT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_LANE_SEQUENCING_SPLIT_REQUIRED_LINE_COUNT={len(REQUIRED_LINE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
