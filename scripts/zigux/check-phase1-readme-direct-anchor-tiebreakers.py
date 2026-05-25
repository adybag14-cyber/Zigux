#!/usr/bin/env python3
"""Guard the Phase 1 scripts README direct-anchor tie-breaker packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SCRIPTS_README_REL = Path("scripts/zigux/README.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    SCRIPTS_README_REL,
    LANE_NOTE_REL,
    MANIFEST_REL,
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

README_DIRECT_TIEBREAKER_LINE = (
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, "
    "and string reopen only inside their existing helper-local anchors or already-committed "
    "shared fixture keys, while the other nine closed helpers stay parked unless the shared "
    "replay or reminder packet drifts"
)

LANE_NOTE_LINES = (
    "- bitmap, find_bit, rbtree, and string are the only helpers eligible for bounded direct-anchor "
    "follow-up, and even those should reopen only inside their existing helper-local anchors or "
    "already-committed shared fixture keys",
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,"
    "tools/lib/rbtree.zig,tools/lib/string.zig`",
    "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the "
    "nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct "
    "helper-local follow-up anchors on current master.`",
    "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two "
    "sets in one lane; shared-replay parked helpers reopen only for packet drift, while "
    "direct-anchor helpers reopen only for their existing helper-local anchors or "
    "already-committed shared fixture keys.`",
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    text = load_text(root, relative_path)
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


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

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    scripts_readme = load_text(root, SCRIPTS_README_REL)
    lane_note = load_text(root, LANE_NOTE_REL)

    failures.extend(
        require_exact_line(
            scripts_readme,
            f"{SCRIPTS_README_REL.as_posix()}:direct_tiebreaker",
            README_DIRECT_TIEBREAKER_LINE,
        )
    )
    for idx, line in enumerate(LANE_NOTE_LINES):
        failures.extend(
            require_exact_line(
                lane_note,
                f"{LANE_NOTE_REL.as_posix()}:line_{idx}",
                line,
            )
        )

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure(MANIFEST_REL.as_posix(), exc)]

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_paths]

    expectations = {
        ("phase",): "Phase 1",
        ("status",): "closed",
        ("helper_count",): len(EXPECTED_HELPERS),
        ("helpers",): EXPECTED_HELPERS,
        ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
        ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
        ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
    }

    for path, expected in expectations.items():
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


def sample_manifest() -> str:
    payload = {
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
    return json.dumps(payload, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    write_file(root, SCRIPTS_README_REL, "# scripts/zigux\n\n## Phase 1\n\n" + README_DIRECT_TIEBREAKER_LINE + "\n")
    write_file(root, LANE_NOTE_REL, "# Phase 1 Host-Helper Lane Sequencing\n\n" + "\n".join(LANE_NOTE_LINES) + "\n")
    write_file(root, MANIFEST_REL, sample_manifest())


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    leaf = path[-1]
    value = current[leaf]
    if isinstance(value, list):
        current[leaf] = value[1:]
    elif isinstance(value, int):
        current[leaf] = value + 1
    else:
        current[leaf] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_manifest_key(root: Path) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    needle = '  "lane_sequencing": {\n'
    duplicate = '  "lane_sequencing": {},\n'
    manifest_path.write_text(text.replace(needle, duplicate + needle, 1), encoding="utf-8")


def remove_exact_line(root: Path, relative_path: Path, target_line: str) -> None:
    path = root / relative_path
    kept: list[str] = []
    removed = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not removed and line.strip() == target_line.strip():
            removed = True
            continue
        kept.append(line)
    path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")


def duplicate_exact_line(root: Path, relative_path: Path, target_line: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == target_line.strip():
            lines.insert(idx + 1, line)
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("success", None),
        ("missing_file:scripts_readme", ("unlink", SCRIPTS_README_REL)),
        ("missing_file:lane_note", ("unlink", LANE_NOTE_REL)),
        ("missing_file:manifest", ("unlink", MANIFEST_REL)),
        ("missing_readme_line", ("remove_line", SCRIPTS_README_REL, README_DIRECT_TIEBREAKER_LINE)),
        ("duplicate_readme_line", ("duplicate_line", SCRIPTS_README_REL, README_DIRECT_TIEBREAKER_LINE)),
        ("missing_lane_line", ("remove_line", LANE_NOTE_REL, LANE_NOTE_LINES[0])),
        ("duplicate_lane_line", ("duplicate_line", LANE_NOTE_REL, LANE_NOTE_LINES[1])),
        ("manifest_drift:direct", ("mutate_manifest", ("lane_sequencing", "direct_anchor_followup_helpers"))),
        ("manifest_drift:shared", ("mutate_manifest", ("lane_sequencing", "shared_replay_parked_helpers"))),
        ("duplicate_manifest_key", ("duplicate_manifest_key",)),
    ]

    for name, action in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-readme-direct-anchor-") as tmpdir:
            root = Path(tmpdir)
            write_sample_root(root)
            if action is not None:
                mode = action[0]
                if mode == "unlink":
                    (root / action[1]).unlink()
                elif mode == "remove_line":
                    remove_exact_line(root, action[1], action[2])
                elif mode == "duplicate_line":
                    duplicate_exact_line(root, action[1], action[2])
                elif mode == "mutate_manifest":
                    mutate_manifest(root, action[1])
                elif mode == "duplicate_manifest_key":
                    insert_duplicate_manifest_key(root)

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

    print("PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS_SELF_TEST=pass")
    print(f"PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checker coverage")
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal current-like sample root for focused replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        write_sample_root(sample_root)
        print(f"PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS_SAMPLE_ROOT={sample_root}")
        return 0

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS=pass")
    print(f"PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(
        "PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS_SHARED_COUNT="
        f"{len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}"
    )
    print(
        "PHASE1_README_DIRECT_ANCHOR_TIEBREAKERS_DIRECT_COUNT="
        f"{len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
