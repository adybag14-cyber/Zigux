#!/usr/bin/env python3
"""Guard the Phase 1 helper lane-sequencing packet against manifest and reminder drift."""

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
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
)

TESTS_README_MARKERS = (
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
)

MANIFEST_EXPECTATIONS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): len(EXPECTED_HELPERS),
    ("helpers",): EXPECTED_HELPERS,
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
    ("lane_sequencing", "rule_summary"): EXPECTED_RULE_SUMMARY,
    ("lane_sequencing", "anti_overlap_rule"): EXPECTED_ANTI_OVERLAP_RULE,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_json(root: Path, relative_path: Path) -> object:
    return json.loads(read_text(root, relative_path))


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
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    lane_note_text = read_text(root, LANE_NOTE_REL)
    scripts_readme_text = read_text(root, SCRIPTS_README_REL)
    tests_readme_text = read_text(root, TESTS_README_REL)
    manifest = read_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    for idx, marker in enumerate(LANE_NOTE_MARKERS):
        failures.extend(require_exact_line(lane_note_text, f"{LANE_NOTE_REL.as_posix()}:line_{idx}", marker))
    for idx, marker in enumerate(SCRIPTS_README_MARKERS):
        failures.extend(
            require_exact_line(scripts_readme_text, f"{SCRIPTS_README_REL.as_posix()}:line_{idx}", marker)
        )
    for idx, marker in enumerate(TESTS_README_MARKERS):
        failures.extend(
            require_exact_line(tests_readme_text, f"{TESTS_README_REL.as_posix()}:line_{idx}", marker)
        )

    for path, expected in MANIFEST_EXPECTATIONS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}",
                nested_value(manifest, path),
                expected,
            )
        )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
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
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    write_text(root, LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root, TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(root, MANIFEST_REL, sample_manifest())


def mutate_json_path(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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


def mutate_line(root: Path, relative_path: Path, line: str, duplicate: bool) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    if duplicate:
        text = text.replace(line + "\n", line + "\n" + line + "\n", 1)
    else:
        text = text.replace(line + "\n", "", 1)
    target.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str, object, object]] = [("success", "none", None, None)]

    for relative_path, markers in (
        (LANE_NOTE_REL, LANE_NOTE_MARKERS),
        (SCRIPTS_README_REL, SCRIPTS_README_MARKERS),
        (TESTS_README_REL, TESTS_README_MARKERS),
    ):
        for marker in markers:
            cases.append((f"remove_{relative_path.name}_{abs(hash(marker))}", "line_remove", relative_path, marker))
            cases.append((f"duplicate_{relative_path.name}_{abs(hash(marker))}", "line_duplicate", relative_path, marker))

    for path in MANIFEST_EXPECTATIONS:
        cases.append((f"manifest_{'_'.join(path)}", "manifest", path, None))

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file_{relative_path.name}", "missing_file", relative_path, None))

    for name, kind, target, payload in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-helper-lane-sequencing-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if kind == "line_remove":
                mutate_line(root, target, payload, duplicate=False)
            elif kind == "line_duplicate":
                mutate_line(root, target, payload, duplicate=True)
            elif kind == "manifest":
                mutate_json_path(root, target)
            elif kind == "missing_file":
                (root / target).unlink()

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
                continue
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("phase1-helper-lane-sequencing:self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-helper-lane-sequencing:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
