#!/usr/bin/env python3
"""Check that the Phase 13 tests-root summary keeps current shared packet evidence explicit."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

TESTS_README_PATH = Path("zigux/tests/README.md")
PHASE13_START = "Phase 13 review packet"

REQUIRED_MARKERS = (
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-shared-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase13-release-coordination-matrix.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`Documentation/zigux/phase13-libfs-survey.md`",
    "`fs/libfs.zig`",
    "`zigux/tests/phase13_libfs.zig`",
    "`zigux/tests/phase13_libfs_reviewability.zig`",
    "`zigux/tests/phase13_libfs_manifest.json`",
    "`Documentation/zigux/phase13-devres-slice.md`",
    "`Documentation/zigux/phase13-devres-survey.md`",
    "`lib/devres.zig`",
    "`zigux/tests/phase13_devres.zig`",
    "`zigux/tests/phase13_devres_reviewability.zig`",
    "`zigux/tests/phase13_devres_dma_coherent.zig`",
    "`zigux/tests/phase13_devres_boundary_evidence.zig`",
    "`zigux/tests/phase13_devres_manifest.json`",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-slice.md`",
    "`Documentation/zigux/phase13-landlock-ruleset-survey.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-governance.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-slice.md`",
    "`Documentation/zigux/phase13-landlock-syscalls-survey.md`",
    "`Documentation/zigux/phase13-notifier-list-survey.md`",
    "`security/landlock/ruleset.zig`",
    "`security/landlock/syscalls.zig`",
    "`zigux/tests/phase13_landlock_ruleset.zig`",
    "`zigux/tests/phase13_landlock_ruleset_manifest.json`",
    "`zigux/tests/phase13_landlock_syscalls.zig`",
    "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
    "`scripts/zigux/check-phase13-landlock-ruleset-packet.py`",
    "`scripts/zigux/check-phase13-notifier-priority-signal.py`",
    "`scripts/zigux/validate-phase13-release.py`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "`zigux/bindings/notifier_abi.zig`",
    "`include/zigux/abi.h`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`zigux/Makefile`",
    "`make -C zigux phase13-validate`",
    "blocked convenience route `make -C zigux phase13`",
    "`Documentation/zigux/phase13-libfs-slice.md`",
    "`zigux/tests/phase13_build.zig`",
    "`zigux/tests/phase13_libfs_addressability.zig`",
    "`scripts/zigux/check-phase13-notifier-packet.py`",
    "`include/zigux/notifier_abi.h`",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
    "repo-reality gaps",
    "Keep `make -C zigux phase13-validate` as the stable contributor-facing handle until the shared build companion lands",
    "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`",
)

EXPECTED_COUNTS = {
    "`make -C zigux phase13-validate`": 2,
    "blocked convenience route `make -C zigux phase13`": 1,
    "`zigux/tests/phase13_build.zig`": 2,
    "`zigux/helpers/notifier_chain_view.zig`": 2,
    "`zigux/bindings/notifier_abi.zig`": 2,
    "`drivers/tty/hvc/hvc_console.h`": 2,
}


def phase13_section(text: str) -> str:
    start = text.find(PHASE13_START)
    if start == -1:
        raise SystemExit(
            "phase13 tests-readme alignment checker missing `Phase 13 review packet` section heading"
        )
    return text[start:]


def check_section(section: str) -> None:
    missing = [marker for marker in REQUIRED_MARKERS if marker not in section]
    if missing:
        raise SystemExit(
            "phase13 tests-readme alignment checker missing markers: "
            + ", ".join(missing)
        )

    for marker, expected_count in EXPECTED_COUNTS.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            raise SystemExit(
                "phase13 tests-readme alignment checker expected exactly "
                f"{expected_count} occurrences of {marker}, found {actual_count}"
            )


def check_text(text: str) -> None:
    check_section(phase13_section(text))


def run_self_test() -> int:
    good = TESTS_README_PATH.with_suffix(".md").read_text(encoding="utf-8")
    check_text(good)

    missing_heading = good.replace("Phase 13 review packet", "Phase Thirteen review packet", 1)
    try:
        check_text(missing_heading)
    except SystemExit as exc:
        assert "`Phase 13 review packet`" in str(exc)
    else:
        raise AssertionError("expected missing Phase 13 heading failure")

    missing_validate_handle = good.replace("`make -C zigux phase13-validate`", "", 1)
    try:
        check_text(missing_validate_handle)
    except SystemExit as exc:
        assert "`make -C zigux phase13-validate`" in str(exc)
    else:
        raise AssertionError("expected missing phase13 validate handle failure")

    missing_blocked_route = good.replace("blocked convenience route `make -C zigux phase13`", "", 1)
    try:
        check_text(missing_blocked_route)
    except SystemExit as exc:
        assert "blocked convenience route `make -C zigux phase13`" in str(exc)
    else:
        raise AssertionError("expected missing blocked route failure")

    missing_notifier_gap = good.replace("`scripts/zigux/check-phase13-notifier-packet.py`", "", 1)
    try:
        check_text(missing_notifier_gap)
    except SystemExit as exc:
        assert "`scripts/zigux/check-phase13-notifier-packet.py`" in str(exc)
    else:
        raise AssertionError("expected missing notifier gap marker failure")

    missing_phase13_build_gap = good.replace("`zigux/tests/phase13_build.zig`", "", 1)
    try:
        check_text(missing_phase13_build_gap)
    except SystemExit as exc:
        assert "`zigux/tests/phase13_build.zig`" in str(exc)
    else:
        raise AssertionError("expected missing phase13 build gap failure")

    duplicate_notifier_anchor = good.replace(
        "`zigux/helpers/notifier_chain_view.zig`",
        "`zigux/helpers/notifier_chain_view.zig`\n  * `zigux/helpers/notifier_chain_view.zig`",
        1,
    )
    try:
        check_text(duplicate_notifier_anchor)
    except SystemExit as exc:
        assert "`zigux/helpers/notifier_chain_view.zig`" in str(exc)
        assert "expected exactly" in str(exc)
    else:
        raise AssertionError("expected duplicate notifier anchor failure")

    missing_tests_root_summary = good.replace(
        "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`",
        "",
        1,
    )
    try:
        check_text(missing_tests_root_summary)
    except SystemExit as exc:
        assert "Current `master` also materializes the dedicated Phase 13 packet summary in `zigux/tests/README.md`" in str(exc)
    else:
        raise AssertionError("expected missing tests-root summary phrase failure")

    print("PHASE13_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE13_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--source",
        type=Path,
        default=TESTS_README_PATH,
        help="path to zigux/tests/README.md",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    text = args.source.read_text(encoding="utf-8")
    check_text(text)
    print("PHASE13_TESTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
