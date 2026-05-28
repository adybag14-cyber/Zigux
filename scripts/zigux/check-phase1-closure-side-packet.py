#!/usr/bin/env python3
"""Check the current Phase 1 closure-side reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
VALIDATE_PHASE1_CLOSURE_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    VALIDATE_PHASE1_CLOSURE_REL,
    TESTS_README_REL,
    MANIFEST_REL,
)

EXPECTED_CLOSURE_MARKERS = (
    "`PHASE1_STATUS=parked`",
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "`PHASE1_HELPER_COUNT=13`",
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
)

EXPECTED_LANE_NOTE_MARKERS = (
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
)

EXPECTED_DOCS_ROOT_MARKERS = (
    "Phase 1 notes - `Documentation/zigux/phase1-host-helper-lane-sequencing.md` - `Documentation/zigux/phase1-closure.md` - `Documentation/zigux/review-checklist.md` - `zigux/tests/README.md` - `zigux/tests/fixtures/phase1_helper_manifest.json` - `scripts/zigux/README.md` - `scripts/zigux/validate-phase1-closure.py` - `scripts/zigux/check-phase1-string-review-packet.py` - `scripts/zigux/check-phase1-direct-owner-markers.py` - `scripts/zigux/check-phase1-shared-reminder-packet.py` - `scripts/zigux/check-phase1-bench.py`",
    "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
)

EXPECTED_REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`zigux/tests/README.md`",
    "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`scripts/zigux/check-phase1-route-summary-counts.py`",
    "`make -C zigux phase1-route-summary`",
    "`zigux/Makefile`",
)

EXPECTED_SCRIPTS_README_MARKERS = (
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
)

EXPECTED_VALIDATOR_MARKERS = (
    "\"status\": \"`PHASE1_STATUS=parked`\"",
    "\"restore_state\": \"`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`\"",
    "\"helper_count\": \"`PHASE1_HELPER_COUNT=13`\"",
    "\"reminder_packet\": \"`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`\"",
    "\"closure_validator\": \"`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`\"",
    "\"route_summary_guard\": \"`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`\"",
    "\"shared_tests_route\": \"`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`\"",
    "\"validator_state\": \"`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`\"",
)

EXPECTED_TESTS_README_MARKERS = (
    "- `Documentation/zigux/phase1-closure.md`",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/README.md`",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "- `zigux/tests/build.zig`",
    "- `zigux/tests/phase1_helpers.zig`",
    "- `zigux/tests/phase1_helpers_build.zig`",
    "- `zigux/tests/phase1_host_tools_smoke.zig`",
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
)

EXPECTED_MANIFEST_PHASE = "Phase 1"
EXPECTED_MANIFEST_STATUS = "closed"
EXPECTED_MANIFEST_HELPER_COUNT = 13
EXPECTED_LANE_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)
EXPECTED_LANE_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    missing_files = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if missing_files:
        return missing_files

    failures: list[str] = []

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_exact_occurrence(closure_text, PHASE1_CLOSURE_REL.as_posix(), marker))

    lane_note_text = load_text(root, PHASE1_LANE_NOTE_REL)
    for marker in EXPECTED_LANE_NOTE_MARKERS:
        failures.extend(require_exact_occurrence(lane_note_text, PHASE1_LANE_NOTE_REL.as_posix(), marker))

    docs_root_text = load_text(root, DOCS_ROOT_REL)
    for marker in EXPECTED_DOCS_ROOT_MARKERS:
        failures.extend(require_exact_occurrence(docs_root_text, DOCS_ROOT_REL.as_posix(), marker))

    review_checklist_text = load_text(root, REVIEW_CHECKLIST_REL)
    for marker in EXPECTED_REVIEW_CHECKLIST_MARKERS:
        failures.extend(require_exact_occurrence(review_checklist_text, REVIEW_CHECKLIST_REL.as_posix(), marker))

    scripts_readme_text = load_text(root, SCRIPTS_README_REL)
    for marker in EXPECTED_SCRIPTS_README_MARKERS:
        failures.extend(require_exact_occurrence(scripts_readme_text, SCRIPTS_README_REL.as_posix(), marker))

    validator_text = load_text(root, VALIDATE_PHASE1_CLOSURE_REL)
    for marker in EXPECTED_VALIDATOR_MARKERS:
        failures.extend(require_exact_occurrence(validator_text, VALIDATE_PHASE1_CLOSURE_REL.as_posix(), marker))

    tests_readme_text = load_text(root, TESTS_README_REL)
    for marker in EXPECTED_TESTS_README_MARKERS:
        failures.extend(require_exact_occurrence(tests_readme_text, TESTS_README_REL.as_posix(), marker))

    manifest = json.loads(load_text(root, MANIFEST_REL))
    if manifest.get("phase") != EXPECTED_MANIFEST_PHASE:
        failures.append(f"{MANIFEST_REL.as_posix()}:phase:expected={EXPECTED_MANIFEST_PHASE!r}:actual={manifest.get('phase')!r}")
    if manifest.get("status") != EXPECTED_MANIFEST_STATUS:
        failures.append(f"{MANIFEST_REL.as_posix()}:status:expected={EXPECTED_MANIFEST_STATUS!r}:actual={manifest.get('status')!r}")
    if manifest.get("helper_count") != EXPECTED_MANIFEST_HELPER_COUNT:
        failures.append(f"{MANIFEST_REL.as_posix()}:helper_count:expected={EXPECTED_MANIFEST_HELPER_COUNT!r}:actual={manifest.get('helper_count')!r}")

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}")
    else:
        if lane_sequencing.get("rule_summary") != EXPECTED_LANE_RULE_SUMMARY:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:lane_sequencing.rule_summary:expected={EXPECTED_LANE_RULE_SUMMARY!r}:actual={lane_sequencing.get('rule_summary')!r}"
            )
        if lane_sequencing.get("anti_overlap_rule") != EXPECTED_LANE_ANTI_OVERLAP_RULE:
            failures.append(
                f"{MANIFEST_REL.as_posix()}:lane_sequencing.anti_overlap_rule:expected={EXPECTED_LANE_ANTI_OVERLAP_RULE!r}:actual={lane_sequencing.get('anti_overlap_rule')!r}"
            )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n")
    write_text(root / PHASE1_LANE_NOTE_REL, "# Lane Note\n\n" + "\n".join(EXPECTED_LANE_NOTE_MARKERS) + "\n")
    write_text(root / DOCS_ROOT_REL, "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_REL, "\n".join(EXPECTED_REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root / VALIDATE_PHASE1_CLOSURE_REL, "\n".join(EXPECTED_VALIDATOR_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": EXPECTED_MANIFEST_PHASE,
                "status": EXPECTED_MANIFEST_STATUS,
                "helper_count": EXPECTED_MANIFEST_HELPER_COUNT,
                "lane_sequencing": {
                    "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_LANE_ANTI_OVERLAP_RULE,
                },
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    make_fixture_tree(root)


def mutate_remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root / relative_path, text.replace(marker + "\n", "", 1))


def mutate_replace_marker(root: Path, relative_path: Path, old: str, new: str) -> None:
    text = load_text(root, relative_path)
    write_text(root / relative_path, text.replace(old, new, 1))


def mutate_manifest_value(root: Path, key: str, value: object) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[key] = value
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def mutate_manifest_lane_value(root: Path, key: str, value: object) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["lane_sequencing"][key] = value
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_closure_helper_count", lambda root: mutate_remove_marker(root, PHASE1_CLOSURE_REL, EXPECTED_CLOSURE_MARKERS[2])),
        ("stale_closure_reminder_packet", lambda root: mutate_replace_marker(root, PHASE1_CLOSURE_REL, EXPECTED_CLOSURE_MARKERS[3], "`PHASE1_CURRENT_REMINDER_PACKET=drifted`")),
        ("missing_lane_route_split", lambda root: mutate_remove_marker(root, PHASE1_LANE_NOTE_REL, EXPECTED_LANE_NOTE_MARKERS[1])),
        ("missing_lane_next_step", lambda root: mutate_remove_marker(root, PHASE1_LANE_NOTE_REL, EXPECTED_LANE_NOTE_MARKERS[2])),
        ("missing_docs_root_marker", lambda root: mutate_remove_marker(root, DOCS_ROOT_REL, EXPECTED_DOCS_ROOT_MARKERS[0])),
        ("missing_scripts_route_summary", lambda root: mutate_remove_marker(root, SCRIPTS_README_REL, EXPECTED_SCRIPTS_README_MARKERS[1])),
        ("missing_validator_state_marker", lambda root: mutate_remove_marker(root, VALIDATE_PHASE1_CLOSURE_REL, EXPECTED_VALIDATOR_MARKERS[7])),
        ("missing_tests_helper_replay_route", lambda root: mutate_remove_marker(root, TESTS_README_REL, EXPECTED_TESTS_README_MARKERS[16])),
        ("bad_manifest_status", lambda root: mutate_manifest_value(root, "status", "parked")),
        ("bad_manifest_lane_summary", lambda root: mutate_manifest_lane_value(root, "rule_summary", "drifted summary")),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-side-packet-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-side-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-side-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_SIDE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SIDE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample tree")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_SIDE_PACKET=fail")
        print("MISSING_PHASE1_CLOSURE_SIDE_PACKET_ITEMS_START")
        for failure in failures:
            print(failure)
        print("MISSING_PHASE1_CLOSURE_SIDE_PACKET_ITEMS_END")
        return 1

    print("PHASE1_CLOSURE_SIDE_PACKET=pass")
    print(f"PHASE1_CLOSURE_SIDE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_SIDE_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(EXPECTED_CLOSURE_MARKERS) + len(EXPECTED_LANE_NOTE_MARKERS) + len(EXPECTED_DOCS_ROOT_MARKERS) + len(EXPECTED_REVIEW_CHECKLIST_MARKERS) + len(EXPECTED_SCRIPTS_README_MARKERS) + len(EXPECTED_VALIDATOR_MARKERS) + len(EXPECTED_TESTS_README_MARKERS) + 5}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
