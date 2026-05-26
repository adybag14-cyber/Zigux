#!/usr/bin/env python3
"""Guard the current Phase 1 lane-sequencing packet against drift."""

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
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    LANE_NOTE_REL,
    DOCS_ROOT_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    DIRECT_OWNER_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    MANIFEST_REL,
)

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

REQUIRED_EXACT_LINES = {
    LANE_NOTE_REL: [
        "Current `master` keeps the closed Phase 1 helper packet split into two non-overlapping follow-up families.",
        "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
        "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "- `PHASE1_LANE_RULE_SUMMARY=Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.`",
        "- `PHASE1_LANE_ANTI_OVERLAP_RULE=Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.`",
        "- the helper-specific direct-owner marker lines in this note are already exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py`, so reread them only if the note or its dedicated checker changes",
        "- current authenticated reads still recover `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so those are the trustworthy reminder surfaces for this lane on current `master`",
    ],
    DOCS_ROOT_REL: [
        "keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    ],
    SCRIPTS_README_REL: [
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    ],
    TESTS_README_REL: [
        "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
        "* current direct-readback Phase 1 reminder packet:",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    ],
    DIRECT_OWNER_CHECKER_REL: [
        'print("PHASE1_DIRECT_OWNER_MARKERS=pass")',
    ],
    SHARED_REMINDER_CHECKER_REL: [
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
    ],
}

MANIFEST_EXPECTATIONS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): 13,
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
    ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
    ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
}


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


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures = [
        f"missing_file:{relative_path.as_posix()}"
        for relative_path in REQUIRED_FILES
        if not (root / relative_path).exists()
    ]
    if failures:
        return failures

    for relative_path, lines in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for idx, line in enumerate(lines):
            failures.extend(
                require_exact_line(
                    text,
                    f"{relative_path.as_posix()}:line_{idx}",
                    line,
                )
            )

    try:
        manifest = load_json_with_duplicate_tracking(load_text(root, MANIFEST_REL))
    except json.JSONDecodeError as exc:
        return [
            f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"
        ]
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_key_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_key_paths:
        return [
            f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_key_paths
        ]

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


def sample_manifest() -> str:
    data = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    return json.dumps(data, indent=2) + "\n"


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == MANIFEST_REL:
            write_file(root, relative_path, sample_manifest())
            continue
        lines = REQUIRED_EXACT_LINES.get(relative_path, [])
        write_file(root, relative_path, "# sample\n" + "\n".join(lines) + "\n")


def mutate_remove_line(root: Path, relative_path: Path, line: str) -> None:
    target = root / relative_path
    lines = target.read_text(encoding="utf-8").splitlines()
    stripped = line.strip()
    for index, current in enumerate(lines):
        if current.strip() == stripped:
            del lines[index]
            target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return


def mutate_duplicate_line(root: Path, relative_path: Path, line: str) -> None:
    target = root / relative_path
    lines = target.read_text(encoding="utf-8").splitlines()
    stripped = line.strip()
    for index, current in enumerate(lines):
        if current.strip() == stripped:
            lines.insert(index + 1, current)
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[:-1]
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def insert_duplicate_manifest_key(root: Path) -> None:
    manifest_path = root / MANIFEST_REL
    text = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(
        text.replace(
            '  "lane_sequencing": {',
            '  "lane_sequencing": {},\n  "lane_sequencing": {',
            1,
        ),
        encoding="utf-8",
    )


def run_self_test() -> int:
    cases: list[tuple[str, str, object | None]] = [("success", "noop", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", "remove_file", relative_path))
    for relative_path, lines in REQUIRED_EXACT_LINES.items():
        for idx, line in enumerate(lines):
            cases.append((f"remove_line:{relative_path.as_posix()}:{idx}", "remove_line", (relative_path, line)))
            cases.append(
                (f"duplicate_line:{relative_path.as_posix()}:{idx}", "duplicate_line", (relative_path, line))
            )
    for path in MANIFEST_EXPECTATIONS:
        cases.append((f"manifest_drift:{'.'.join(path)}", "mutate_manifest", path))
    cases.append(("duplicate_manifest_key:lane_sequencing", "duplicate_manifest_key", None))

    for name, mode, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-lane-sequencing-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mode == "remove_file" and isinstance(payload, Path):
                (root / payload).unlink()
            elif mode == "remove_line" and isinstance(payload, tuple):
                relative_path, line = payload
                mutate_remove_line(root, relative_path, line)
            elif mode == "duplicate_line" and isinstance(payload, tuple):
                relative_path, line = payload
                mutate_duplicate_line(root, relative_path, line)
            elif mode == "mutate_manifest" and isinstance(payload, tuple):
                mutate_manifest(root, payload)
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

    print("PHASE1_LANE_SEQUENCING_PACKET_SELF_TEST=pass")
    print(f"PHASE1_LANE_SEQUENCING_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_LANE_SEQUENCING_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_LANE_SEQUENCING_PACKET=pass")
    print(f"PHASE1_LANE_SEQUENCING_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_LANE_SEQUENCING_PACKET_REQUIRED_LINE_COUNT={sum(len(v) for v in REQUIRED_EXACT_LINES.values())}")
    print("PHASE1_LANE_SEQUENCING_PACKET_FOLLOWUP_FAMILY_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
