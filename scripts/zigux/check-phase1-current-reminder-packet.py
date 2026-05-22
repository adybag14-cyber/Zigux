#!/usr/bin/env python3
"""Check the current Phase 1 reminder packet across shared reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

CURRENT_REMINDER_PACKET = (
    "Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md,"
    "Documentation/zigux/README.md,"
    "Documentation/zigux/review-checklist.md,"
    "scripts/zigux/README.md,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,"
    "scripts/zigux/check-phase1-bench.py,"
    "scripts/zigux/check-phase1-shared-reminder-packet.py,"
    "scripts/zigux/validate-phase1-closure.py,"
    "zigux/tests/README.md,"
    "zigux/tests/build.zig,"
    "zigux/tests/phase1_host_tools_smoke.zig,"
    ".github/workflows/zigux-bootstrap.yml,"
    "zigux/tests/fixtures/phase1_helper_manifest.json"
)

CURRENT_GAP_PACKET = (
    "scripts/zigux/validate-phase1.py,"
    "scripts/zigux/check-phase1-parity.py,"
    "zigux/tests/phase1_helpers.zig,"
    "zigux/tests/phase1_bench.zig,"
    "zigux/tests/fixtures/phase1_bench_expectations.json,"
    "zigux/tests/fixtures/phase1_helpers_c_harness.c"
)

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    STRING_REVIEW_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    VALIDATOR_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    WORKFLOW_REL,
    MANIFEST_REL,
)

EXPECTED_CLOSURE_MARKERS = (
    f"`PHASE1_CURRENT_REMINDER_PACKET={CURRENT_REMINDER_PACKET}`",
    f"`PHASE1_CURRENT_GAP_PACKET={CURRENT_GAP_PACKET}`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
)

EXPECTED_DOCS_MARKERS = (
    "- `Documentation/zigux/phase1-closure.md`",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
)

EXPECTED_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `zigux/Makefile` explicit as current repo evidence for the returned non-Phase-1 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
)

EXPECTED_SCRIPTS_MARKERS = (
    "- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map and string-review guards instead of rebuilding the broader installer-backed closure packet from older missing routes",
    "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
)

EXPECTED_TESTS_MARKERS = (
    "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_contains(text: str, label: str, needle: str) -> list[str]:
    return [] if needle in text else [f"{label}:missing:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for marker in EXPECTED_CLOSURE_MARKERS:
        failures.extend(require_contains(closure_text, PHASE1_CLOSURE_REL.as_posix(), marker))

    docs_text = load_text(root, DOCS_ROOT_REL)
    for marker in EXPECTED_DOCS_MARKERS:
        failures.extend(require_contains(docs_text, DOCS_ROOT_REL.as_posix(), marker))

    checklist_text = load_text(root, REVIEW_CHECKLIST_REL)
    for marker in EXPECTED_CHECKLIST_MARKERS:
        failures.extend(require_contains(checklist_text, REVIEW_CHECKLIST_REL.as_posix(), marker))

    scripts_text = load_text(root, SCRIPTS_README_REL)
    for marker in EXPECTED_SCRIPTS_MARKERS:
        failures.extend(require_contains(scripts_text, SCRIPTS_README_REL.as_posix(), marker))

    tests_text = load_text(root, TESTS_README_REL)
    for marker in EXPECTED_TESTS_MARKERS:
        failures.extend(require_contains(tests_text, TESTS_README_REL.as_posix(), marker))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_placeholder(path: Path) -> None:
    write_text(path, f"placeholder for {path.as_posix()}\n")


def make_fixture_tree(root: Path) -> None:
    for path in REQUIRED_FILES:
        if path in {
            PHASE1_CLOSURE_REL,
            DOCS_ROOT_REL,
            REVIEW_CHECKLIST_REL,
            SCRIPTS_README_REL,
            TESTS_README_REL,
        }:
            continue
        make_placeholder(root / path)

    write_text(root / PHASE1_LANE_NOTE_REL, "phase1 lane note placeholder\n")
    write_text(root / PHASE1_CLOSURE_REL, "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n")
    write_text(root / DOCS_ROOT_REL, "# Zigux Documentation\n\n" + "\n".join(EXPECTED_DOCS_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_REL, "# Zigux Review Checklist\n\n" + "\n".join(EXPECTED_CHECKLIST_MARKERS) + "\n")
    write_text(root / SCRIPTS_README_REL, "# scripts/zigux\n\n" + "\n".join(EXPECTED_SCRIPTS_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "# zigux/tests\n\n" + "\n".join(EXPECTED_TESTS_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_closure_packet",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[0] + "\n", "", 1),
            ),
        ),
        (
            "stale_gap_packet",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(
                    EXPECTED_CLOSURE_MARKERS[1],
                    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py`",
                    1,
                ),
            ),
        ),
        (
            "missing_docs_owner_map_marker",
            lambda root: write_text(
                root / DOCS_ROOT_REL,
                load_text(root, DOCS_ROOT_REL).replace(EXPECTED_DOCS_MARKERS[6] + "\n", "", 1),
            ),
        ),
        (
            "missing_checklist_packet",
            lambda root: write_text(
                root / REVIEW_CHECKLIST_REL,
                load_text(root, REVIEW_CHECKLIST_REL).replace(EXPECTED_CHECKLIST_MARKERS[0] + "\n", "", 1),
            ),
        ),
        (
            "missing_scripts_replay_marker",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(EXPECTED_SCRIPTS_MARKERS[1] + "\n", "", 1),
            ),
        ),
        (
            "missing_tests_prompt",
            lambda root: write_text(
                root / TESTS_README_REL,
                load_text(root, TESTS_README_REL).replace(EXPECTED_TESTS_MARKERS[2] + "\n", "", 1),
            ),
        ),
        ("missing_required_file", lambda root: (root / WORKFLOW_REL).unlink()),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-current-reminder-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-current-reminder-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-current-reminder-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CURRENT_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CURRENT_REMINDER_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def write_sample_root(target_root: Path) -> None:
    make_fixture_tree(target_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument("--write-sample-root", help="write a sample Phase 1 reminder packet root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print(f"PHASE1_CURRENT_REMINDER_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CURRENT_REMINDER_PACKET=pass")
    print(f"PHASE1_CURRENT_REMINDER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_CURRENT_REMINDER_PACKET_CURRENT_FILE_COUNT={CURRENT_REMINDER_PACKET.count(',') + 1}")
    print(f"PHASE1_CURRENT_REMINDER_PACKET_GAP_FILE_COUNT={CURRENT_GAP_PACKET.count(',') + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
