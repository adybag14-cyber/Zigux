#!/usr/bin/env python3
"""Guard the current Phase 1 closure note packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
)

EXPECTED_MISSING_FILES = (
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

EXACT_LINE_MARKERS = (
    "- `PHASE1_STATUS=parked`",
    "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "- `PHASE1_HELPER_COUNT=13`",
    "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, closure validator, shared tests-root smoke route, and the helper-specific next_safe_step_note entries in zigux/tests/fixtures/phase1_helper_manifest.json`",
)

EXACT_TEXT_MARKERS = (
    "# Phase 1 Closure",
    "This note restores the missing Lane 15 closure record in a current-master-safe form.",
    "current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche",
    "The currently reviewable Phase 1 reminder packet is:",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "Current `master` still does not directly materialize the older validator-first and replay-side closure companions that earlier reminder surfaces treated as part of the broader closure stack.",
    "Current `master` does materialize `zigux/Makefile` again",
    "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`",
    "The current shared tests-root closure route is narrow on purpose:",
    "That route keeps a minimal shared import-and-wire smoke check alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.",
)

FORBIDDEN_TEXT_MARKERS = (
    "`PHASE1_SHARED_TESTS_ROUTE=missing_on_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=sync Documentation/zigux/README.md first, then the remaining shared reminder surfaces against the restored closure note and closure validator`",
    "the docs-root reminder surface still lags the restored closure note and validator",
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_only`",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]


def collect_unexpected_present_files(root: Path) -> list[str]:
    return [path.as_posix() for path in EXPECTED_MISSING_FILES if (root / path).exists()]


def collect_exact_line_marker_failures(text: str) -> list[str]:
    failures: list[str] = []
    lines = [line.strip() for line in text.splitlines()]
    for marker in EXACT_LINE_MARKERS:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            failures.append(f"phase1-closure:line:{marker}:expected=1:actual={count}")
    return failures


def collect_exact_text_marker_failures(text: str) -> list[str]:
    failures: list[str] = []
    for marker in EXACT_TEXT_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(f"phase1-closure:text:{marker}:expected=1:actual={count}")
    return failures


def collect_forbidden_marker_failures(text: str) -> list[str]:
    failures: list[str] = []
    for marker in FORBIDDEN_TEXT_MARKERS:
        count = text.count(marker)
        if count != 0:
            failures.append(f"phase1-closure:forbidden:{marker}:actual={count}")
    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path}" for path in collect_missing_files(root)]
    failures.extend(
        f"unexpected_present_gap_file:{path}" for path in collect_unexpected_present_files(root)
    )
    if failures:
        return failures

    text = load_text(root, PHASE1_CLOSURE_REL)
    failures.extend(collect_exact_line_marker_failures(text))
    failures.extend(collect_exact_text_marker_failures(text))
    failures.extend(collect_forbidden_marker_failures(text))
    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, f"fixture for {relative_path.as_posix()}\n")

    note = "\n".join(
        [
            "# Phase 1 Closure",
            "",
            "This note restores the missing Lane 15 closure record in a current-master-safe form.",
            "",
            "## Status",
            "",
            "- `PHASE1_STATUS=parked`",
            "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
            "- `PHASE1_HELPER_COUNT=13`",
            "- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
            "- current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche",
            "",
            "## Current Reminder Packet",
            "",
            "The currently reviewable Phase 1 reminder packet is:",
            "",
            "- `Documentation/zigux/phase1-closure.md`",
            "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
            "- `Documentation/zigux/README.md`",
            "- `Documentation/zigux/review-checklist.md`",
            "- `scripts/zigux/README.md`",
            "- `scripts/zigux/check-phase1-string-review-packet.py`",
            "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
            "- `scripts/zigux/check-phase1-bench.py`",
            "- `scripts/zigux/validate-phase1-closure.py`",
            "- `zigux/tests/README.md`",
            "- `zigux/tests/build.zig`",
            "- `zigux/tests/phase1_host_tools_smoke.zig`",
            "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
            "",
            "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
            "",
            "## Current Repo-Reality Gaps",
            "",
            "Current `master` still does not directly materialize the older validator-first and replay-side closure companions that earlier reminder surfaces treated as part of the broader closure stack.",
            "",
            "- `scripts/zigux/validate-phase1.py`",
            "- `scripts/zigux/check-phase1-parity.py`",
            "- `zigux/tests/phase1_helpers.zig`",
            "- `zigux/tests/phase1_bench.zig`",
            "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
            "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
            "",
            "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
            "",
            "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate`, `phase3`, `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, and `phase8` routes. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
            "",
            "## Closure Validation",
            "",
            "The current shared tests-root closure route is narrow on purpose:",
            "",
            "- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
            "",
            "That route keeps a minimal shared import-and-wire smoke check alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.",
            "",
            "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
            "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
            "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
            "",
            "## Next Step",
            "",
            "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, closure validator, shared tests-root smoke route, and the helper-specific next_safe_step_note entries in zigux/tests/fixtures/phase1_helper_manifest.json`",
            "",
        ]
    )
    write_text(root, PHASE1_CLOSURE_REL, note)


def mutate_remove_once(root: Path, old: str) -> None:
    path = root / PHASE1_CLOSURE_REL
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError(f"missing marker: {old}")
    path.write_text(text.replace(old, "", 1), encoding="utf-8")


def mutate_duplicate_once(root: Path, marker: str) -> None:
    path = root / PHASE1_CLOSURE_REL
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise ValueError(f"missing marker: {marker}")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, callable | None, bool]] = [
        ("baseline", None, True),
        (
            "missing_status_marker",
            lambda root: mutate_remove_once(root, EXACT_LINE_MARKERS[0]),
            False,
        ),
        (
            "missing_reminder_packet_marker",
            lambda root: mutate_remove_once(root, EXACT_LINE_MARKERS[3]),
            False,
        ),
        (
            "missing_string_review_entry",
            lambda root: mutate_remove_once(root, "- `scripts/zigux/check-phase1-string-review-packet.py`\n"),
            False,
        ),
        (
            "missing_direct_owner_entry",
            lambda root: mutate_remove_once(root, "- `scripts/zigux/check-phase1-direct-owner-markers.py`\n"),
            False,
        ),
        (
            "duplicate_next_step_marker",
            lambda root: mutate_duplicate_once(root, EXACT_LINE_MARKERS[-1]),
            False,
        ),
        (
            "missing_required_companion",
            lambda root: (root / Path("scripts/zigux/check-phase1-direct-owner-markers.py")).unlink(),
            False,
        ),
        (
            "missing_makefile",
            lambda root: (root / Path("zigux/Makefile")).unlink(),
            False,
        ),
        (
            "unexpected_gap_file_present",
            lambda root: write_text(
                root,
                Path("zigux/tests/phase1_bench.zig"),
                "stale replay surface should stay absent\n",
            ),
            False,
        ),
        (
            "forbidden_old_next_step",
            lambda root: write_text(
                root,
                PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL)
                + FORBIDDEN_TEXT_MARKERS[1]
                + "\n",
            ),
            False,
        ),
        (
            "missing_makefile_sentence",
            lambda root: mutate_remove_once(root, "Current `master` does materialize `zigux/Makefile` again"),
            False,
        ),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-note-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-closure-note-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_CLOSURE_NOTE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_NOTE_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_NOTE_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_NOTE_ALIGNMENT=pass")
    print(f"PHASE1_CLOSURE_NOTE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_CLOSURE_NOTE_REQUIRED_MARKER_COUNT="
        f"{len(EXACT_LINE_MARKERS) + len(EXACT_TEXT_MARKERS)}"
    )
    print(f"PHASE1_CLOSURE_NOTE_REQUIRED_GAP_COUNT={len(EXPECTED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
