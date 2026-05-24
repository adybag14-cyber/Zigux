#!/usr/bin/env python3
"""Fail closed if the current Phase 1 closure note and closure validator drift apart."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    SCRIPTS_README_REL,
    VALIDATOR_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
)

EXPECTED_CLOSURE_MARKERS = (
    "`PHASE1_STATUS=parked`",
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)

EXPECTED_VALIDATOR_MARKERS = (
    'PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")',
    'PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")',
    'SCRIPTS_README_REL = Path("scripts/zigux/README.md")',
    'WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")',
    'MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")',
    '"closure_validator": "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",',
    '"validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",',
    '"next_step": "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",',
    '(DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),',
    '(BENCH_CHECKER_REL, "phase1-bench"),',
    '(SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
)

EXPECTED_README_MARKERS = (
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` are back on current `master`, so bitmap-side follow-through can use that restored closure packet as live reminder evidence instead of replaying older missing validator-first or make-route names by default",
)

EXPECTED_WORKFLOW_MARKERS = (
    "- name: Validate Phase 1 closure",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
)

EXPECTED_LANE_NOTE_MARKERS = (
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
)

FORBIDDEN_MARKERS = (
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_once(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    if count == 1:
        return []
    return [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    if count == 0:
        return []
    return [f"{label}:forbidden_marker:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    validator_text = load_text(root, VALIDATOR_REL)
    readme_text = load_text(root, SCRIPTS_README_REL)
    workflow_text = load_text(root, WORKFLOW_REL)
    lane_note_text = load_text(root, PHASE1_LANE_NOTE_REL)

    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_once(closure_text, PHASE1_CLOSURE_REL.as_posix(), marker))
    for marker in EXPECTED_VALIDATOR_MARKERS:
        failures.extend(require_once(validator_text, VALIDATOR_REL.as_posix(), marker))
    for marker in EXPECTED_README_MARKERS:
        failures.extend(require_once(readme_text, SCRIPTS_README_REL.as_posix(), marker))
    for marker in EXPECTED_WORKFLOW_MARKERS:
        failures.extend(require_once(workflow_text, WORKFLOW_REL.as_posix(), marker))
    for marker in EXPECTED_LANE_NOTE_MARKERS:
        failures.extend(require_once(lane_note_text, PHASE1_LANE_NOTE_REL.as_posix(), marker))
    for marker in FORBIDDEN_MARKERS:
        failures.extend(require_absent(closure_text, PHASE1_CLOSURE_REL.as_posix(), marker))
        failures.extend(require_absent(readme_text, SCRIPTS_README_REL.as_posix(), marker))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(
        root / PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n"
        + "\n".join(EXPECTED_CLOSURE_MARKERS)
        + "\n",
    )
    write_text(
        root / VALIDATOR_REL,
        "\n".join(EXPECTED_VALIDATOR_MARKERS) + "\n",
    )
    write_text(
        root / SCRIPTS_README_REL,
        "# scripts/zigux\n\n## Phase 1\n\n"
        + "\n".join(EXPECTED_README_MARKERS)
        + "\n",
    )
    write_text(
        root / WORKFLOW_REL,
        "jobs:\n  bootstrap:\n    steps:\n"
        + "\n".join(f"      {marker}" for marker in EXPECTED_WORKFLOW_MARKERS)
        + "\n",
    )
    write_text(
        root / PHASE1_LANE_NOTE_REL,
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        + "\n".join(EXPECTED_LANE_NOTE_MARKERS)
        + "\n",
    )
    write_text(root / MANIFEST_REL, "{\n  \"phase\": \"Phase 1\"\n}\n")


def run_self_test() -> int:
    cases: list[tuple[str, callable | None]] = [
        ("baseline", None),
        (
            "missing_closure_restore_state",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[1] + "\n", "", 1),
            ),
        ),
        (
            "missing_closure_validator_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[2] + "\n", "", 1),
            ),
        ),
        (
            "forbidden_missing_current_master_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL) + FORBIDDEN_MARKERS[0] + "\n",
            ),
        ),
        (
            "missing_validator_required_file_marker",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(EXPECTED_VALIDATOR_MARKERS[3] + "\n", "", 1),
            ),
        ),
        (
            "missing_validator_next_step_marker",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(EXPECTED_VALIDATOR_MARKERS[7] + "\n", "", 1),
            ),
        ),
        (
            "missing_validator_shared_reminder_delegate",
            lambda root: write_text(
                root / VALIDATOR_REL,
                load_text(root, VALIDATOR_REL).replace(EXPECTED_VALIDATOR_MARKERS[10] + "\n", "", 1),
            ),
        ),
        (
            "missing_readme_selftest_line",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(EXPECTED_README_MARKERS[0] + "\n", "", 1),
            ),
        ),
        (
            "missing_readme_validator_line",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(EXPECTED_README_MARKERS[1] + "\n", "", 1),
            ),
        ),
        (
            "missing_readme_restored_closure_line",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(EXPECTED_README_MARKERS[2] + "\n", "", 1),
            ),
        ),
        (
            "forbidden_old_next_step_in_readme",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL) + FORBIDDEN_MARKERS[1] + "\n",
            ),
        ),
        (
            "missing_workflow_validate_name",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL).replace(f"      {EXPECTED_WORKFLOW_MARKERS[0]}\n", "", 1),
            ),
        ),
        (
            "missing_workflow_validate_run",
            lambda root: write_text(
                root / WORKFLOW_REL,
                load_text(root, WORKFLOW_REL).replace(f"      {EXPECTED_WORKFLOW_MARKERS[1]}\n", "", 1),
            ),
        ),
        (
            "missing_lane_note_active_packet",
            lambda root: write_text(
                root / PHASE1_LANE_NOTE_REL,
                load_text(root, PHASE1_LANE_NOTE_REL).replace(EXPECTED_LANE_NOTE_MARKERS[0] + "\n", "", 1),
            ),
        ),
        (
            "missing_lane_note_route_split",
            lambda root: write_text(
                root / PHASE1_LANE_NOTE_REL,
                load_text(root, PHASE1_LANE_NOTE_REL).replace(EXPECTED_LANE_NOTE_MARKERS[1] + "\n", "", 1),
            ),
        ),
        ("missing_manifest", lambda root: (root / MANIFEST_REL).unlink()),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-packet-") as tmp:
            root = Path(tmp)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-validator-packet-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-validator-packet-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for focused packet validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
