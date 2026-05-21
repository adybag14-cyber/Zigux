#!/usr/bin/env python3
"""Guard the Phase 1 host-helper lane note packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

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
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded direct "
    "helper-local follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or "
    "already-committed shared fixture keys."
)

EXPECTED_ACTIVE_PACKET = (
    "Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/review-checklist.md,zigux/tests/README.md,"
    "scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,"
    "scripts/zigux/check-phase1-bench.py,"
    "scripts/zigux/check-phase1-shared-reminder-packet.py"
)

EXPECTED_ROUTE_SPLIT = (
    "Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, "
    "zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped "
    "bench-checker wording, while Documentation/zigux/phase1-closure.md plus "
    "scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet "
    "explicit and the broader installer-backed, validator-first, bench-route, and "
    "replay names remain historical packet members until direct current-master "
    "rereads restore them"
)

EXPECTED_NEXT_STEP = (
    "leave the shared bench-checker wording and shared-reminder checker packet parked "
    "unless a fresh reread finds drift across Documentation/zigux/README.md, "
    "Documentation/zigux/review-checklist.md, zigux/tests/README.md, "
    "scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, "
    "scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, "
    "or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the "
    "smaller helper-specific next-safe-step markers below before reopening any "
    "shared reminder surface"
)

EXPECTED_LINE_MARKERS = [
    "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    f"- `PHASE1_LANE_RULE_SUMMARY={EXPECTED_RULE_SUMMARY}`",
    f"- `PHASE1_LANE_ANTI_OVERLAP_RULE={EXPECTED_ANTI_OVERLAP_RULE}`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json` is the authoritative owner-map split for all thirteen closed Phase 1 helpers",
    "- current authenticated reads still recover `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so those are the trustworthy reminder surfaces for this lane on current `master`",
    f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET={EXPECTED_ACTIVE_PACKET}`",
    f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT={EXPECTED_ROUTE_SPLIT}`",
    "- Do not batch helpers across the shared-replay parked and direct-anchor follow-up families in one run.",
    "- Shared-replay parked helpers reopen only for packet drift, fixture drift, build-route drift, or review-surface truthfulness.",
    "- Direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
    f"- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP={EXPECTED_NEXT_STEP}`",
]

REQUIRED_FILES = (
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
    DIRECT_OWNER_CHECKER_REL,
    STRING_REVIEW_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    MANIFEST_REL,
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


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg:
        return Path(root_arg).resolve()
    return Path(__file__).resolve().parents[2]


def load_json_without_duplicates(path: Path) -> dict:
    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def add_path_issue(path: Path, rel: Path, prefix: str, issues: list[str]) -> bool:
    if path.is_dir():
        issues.append(f"{prefix}:directory={rel.as_posix()}")
        return True
    if not path.is_file():
        issues.append(f"missing:{rel.as_posix()}")
        return True
    return False


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for relative in REQUIRED_FILES:
        if add_path_issue(root / relative, relative, "path", issues):
            return issues

    lane_note_lines = (root / LANE_NOTE_REL).read_text(encoding="utf-8").splitlines()
    lane_note_text = "\n".join(lane_note_lines)
    for marker in EXPECTED_LINE_MARKERS:
        count = sum(1 for line in lane_note_lines if line == marker)
        if count != 1:
            issues.append(f"lane_note:marker:{count}:{marker}")

    if "### Shared-Replay Parked Helpers" not in lane_note_text:
        issues.append("lane_note:missing_shared_replay_heading")
    if "### Direct-Anchor Follow-Up Helpers" not in lane_note_text:
        issues.append("lane_note:missing_direct_anchor_heading")
    if "## Anti-Overlap Rules" not in lane_note_text:
        issues.append("lane_note:missing_anti_overlap_heading")
    if "## Next Bounded Step" not in lane_note_text:
        issues.append("lane_note:missing_next_step_heading")

    try:
        manifest = load_json_without_duplicates(root / MANIFEST_REL)
    except Exception as exc:
        issues.append(f"manifest:parse={exc}")
        return issues

    for path, expected in MANIFEST_EXPECTATIONS.items():
        if nested_value(manifest, path) != expected:
            issues.append(
                f"manifest:{'.'.join(path)}:{nested_value(manifest, path)!r}!={expected!r}"
            )

    combined = (
        manifest.get("lane_sequencing", {}).get("shared_replay_parked_helpers", [])
        + manifest.get("lane_sequencing", {}).get("direct_anchor_followup_helpers", [])
    )
    if sorted(combined) != sorted(EXPECTED_HELPERS):
        issues.append("manifest:helper_partition")
    if len(set(combined)) != len(EXPECTED_HELPERS):
        issues.append("manifest:helper_partition_duplicates")

    return issues


def make_sample_root(root: Path) -> None:
    lane_note_path = root / LANE_NOTE_REL
    manifest_path = root / MANIFEST_REL
    lane_note_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    lane_note_path.write_text(
        "\n".join(
            [
                "# Phase 1 Host-Helper Lane Sequencing",
                "",
                "## Current Split",
                "",
                "### Shared-Replay Parked Helpers",
                "",
                "### Direct-Anchor Follow-Up Helpers",
                "",
                *EXPECTED_LINE_MARKERS,
                "",
                "## Anti-Overlap Rules",
                "",
                "## Next Bounded Step",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

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
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    for rel in (
        PHASE1_CLOSURE_REL,
        DOCS_ROOT_REL,
        REVIEW_CHECKLIST_REL,
        TESTS_README_REL,
        SCRIPTS_README_REL,
        PHASE1_CLOSURE_VALIDATOR_REL,
        DIRECT_OWNER_CHECKER_REL,
        STRING_REVIEW_CHECKER_REL,
        SHARED_REMINDER_CHECKER_REL,
    ):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# sample\n", encoding="utf-8")


def expect_failure(mutator) -> None:
    with tempfile.TemporaryDirectory(prefix="phase1-host-helper-lane-note-") as tmp_dir:
        root = Path(tmp_dir)
        make_sample_root(root)
        mutator(root)
        issues = collect_issues(root)
        if not issues:
            raise AssertionError("expected failure but checker passed")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase1-host-helper-lane-note-") as tmp_dir:
        root = Path(tmp_dir)
        make_sample_root(root)
        issues = collect_issues(root)
        if issues:
            raise AssertionError(f"sample root should pass, got {issues}")

    def remove_marker(root: Path) -> None:
        path = root / LANE_NOTE_REL
        marker = EXPECTED_LINE_MARKERS[0] + "\n"
        path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")

    expect_failure(remove_marker)

    def duplicate_marker(root: Path) -> None:
        path = root / LANE_NOTE_REL
        marker = EXPECTED_LINE_MARKERS[1]
        path.write_text(
            path.read_text(encoding="utf-8").replace(marker, marker + "\n" + marker, 1),
            encoding="utf-8",
        )

    expect_failure(duplicate_marker)

    def wrong_partition(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["shared_replay_parked_helpers"] = EXPECTED_SHARED_REPLAY_PARKED_HELPERS[:-1]
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(wrong_partition)

    def wrong_rule_summary(root: Path) -> None:
        path = root / MANIFEST_REL
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["lane_sequencing"]["rule_summary"] = "drifted summary"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    expect_failure(wrong_rule_summary)

    def lane_note_directory(root: Path) -> None:
        path = root / LANE_NOTE_REL
        path.unlink()
        path.mkdir()

    expect_failure(lane_note_directory)

    def manifest_directory(root: Path) -> None:
        path = root / MANIFEST_REL
        path.unlink()
        path.mkdir()

    expect_failure(manifest_directory)

    def invalid_manifest(root: Path) -> None:
        path = root / MANIFEST_REL
        path.write_text("{\n", encoding="utf-8")

    expect_failure(invalid_manifest)

    def duplicate_manifest_key(root: Path) -> None:
        path = root / MANIFEST_REL
        path.write_text('{"phase":"Phase 1","phase":"duplicate"}\n', encoding="utf-8")

    expect_failure(duplicate_manifest_key)

    def remove_heading(root: Path) -> None:
        path = root / LANE_NOTE_REL
        path.write_text(
            path.read_text(encoding="utf-8").replace("## Anti-Overlap Rules\n", "", 1),
            encoding="utf-8",
        )

    expect_failure(remove_heading)

    def missing_companion(root: Path) -> None:
        (root / DIRECT_OWNER_CHECKER_REL).unlink()

    expect_failure(missing_companion)

    print("PHASE1_HOST_HELPER_LANE_NOTE_SELF_TEST=pass")
    print("PHASE1_HOST_HELPER_LANE_NOTE_SELF_TEST_CASE_COUNT=10")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a current-master-shaped sample root for replay validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        make_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root_from_arg(args.root)
    issues = collect_issues(root)
    if issues:
        print("PHASE1_HOST_HELPER_LANE_NOTE=fail")
        for issue in issues:
            print(f"PHASE1_HOST_HELPER_LANE_NOTE_ISSUE={issue}")
        return 1

    print("PHASE1_HOST_HELPER_LANE_NOTE=pass")
    print(f"PHASE1_HOST_HELPER_LANE_NOTE_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_HOST_HELPER_LANE_NOTE_PARKED_COUNT={len(EXPECTED_SHARED_REPLAY_PARKED_HELPERS)}")
    print(f"PHASE1_HOST_HELPER_LANE_NOTE_DIRECT_COUNT={len(EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS)}")
    print(f"PHASE1_HOST_HELPER_LANE_NOTE_MARKER_COUNT={len(EXPECTED_LINE_MARKERS)}")
    print(f"PHASE1_HOST_HELPER_LANE_NOTE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
