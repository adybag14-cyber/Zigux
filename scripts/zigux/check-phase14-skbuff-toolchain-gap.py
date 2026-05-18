#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 14 skbuff toolchain gap."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=skbuff_toolchain_gap"
SURVEY_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-skbuff-attached-toolchain-gap.md")
ABSENT_PACKET_PATHS = (
    Path("zigux/tests/phase14_skbuff_bridge.zig"),
    Path("zigux/tests/phase14_build.zig"),
    Path("net/core/skbuff_bridge.zig"),
    Path("zigux/tests/phase14_skbuff_bridge_manifest.json"),
)

REQUIRED_SURVEY_MARKERS = (
    "- `PHASE14_LANE_KEY=P14-L11`",
    "- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`",
    "- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`",
    "- current `master` no longer exposes `zigux/tests/phase14_build.zig`",
    "- current `master` no longer exposes `net/core/skbuff_bridge.zig`",
    "- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- the previous `full_bundle_only` compile path",
    "is archival only and must not be treated as live compile evidence on current `master`",
)

REQUIRED_GAP_NOTE_MARKERS = (
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP=present`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_KIND=anchor_packet_absent_under_attached_toolchain_policy`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_SCOPE=skbuff_packet_truthfulness_only`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`",
    "there is no live\nskbuff-local packet to compile on current `master`.",
    "`scripts/zigux/check-phase14-skbuff-toolchain-gap.py` keeps this gap note and",
    "restore a bounded skbuff anchor packet first",
)

FORBIDDEN_GAP_NOTE_MARKERS = (
    "phase14-skbuff-bridge-tests",
    "make -C zigux phase14-test",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
)


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.exists():
        raise FileNotFoundError(relpath.as_posix())
    return path.read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        failures.append("checker marker missing from script source")

    for relpath in (SURVEY_PATH, GAP_NOTE_PATH):
        if not (root / relpath).exists():
            failures.append(f"missing required file: {relpath.as_posix()}")
    if failures:
        return failures

    survey = read_text(root, SURVEY_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"missing survey marker: {marker}")

    for marker in REQUIRED_GAP_NOTE_MARKERS:
        if marker not in gap_note:
            failures.append(f"missing gap-note marker: {marker}")

    for marker in FORBIDDEN_GAP_NOTE_MARKERS:
        if marker in gap_note:
            failures.append(f"forbidden live compile marker in gap note: {marker}")

    for relpath in ABSENT_PACKET_PATHS:
        if (root / relpath).exists():
            failures.append(
                f"gap note is stale because the skbuff anchor packet path exists again: {relpath.as_posix()}"
            )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_survey() -> str:
    return """# Phase 14 Skbuff Bridge Survey

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`
- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`
- current `master` no longer exposes `zigux/tests/phase14_build.zig`
- current `master` no longer exposes `net/core/skbuff_bridge.zig`
- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`
- the previous `full_bundle_only` compile path from older commits is archival only and must not be treated as live compile evidence on current `master`
"""


def sample_gap_note() -> str:
    return """# Phase 14 Skbuff Attached-Toolchain Evidence Gap

## Status

- `PHASE14_SKBUFF_TOOLCHAIN_GAP=present`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_KIND=anchor_packet_absent_under_attached_toolchain_policy`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_SCOPE=skbuff_packet_truthfulness_only`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_STATUS_BUCKET=study_only`
- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`

That means even when the attached Zig toolchain is available, there is no live
skbuff-local packet to compile on current `master`.

`scripts/zigux/check-phase14-skbuff-toolchain-gap.py` keeps this gap note and
the live skbuff survey aligned on one narrow rule.

If this lane reopens, restore a bounded skbuff anchor packet first and only
then reintroduce attached-toolchain command inventory or compile evidence.
"""


def populate_repo(root: Path) -> None:
    write_text(root / SURVEY_PATH, sample_survey())
    write_text(root / GAP_NOTE_PATH, sample_gap_note())


def run_self_test() -> int:
    checks_run = 0
    tempdir = Path(tempfile.mkdtemp(prefix="phase14-skbuff-toolchain-gap-"))
    try:
        populate_repo(tempdir)
        assert collect_failures(tempdir) == []
        checks_run += 1

        missing_gap_root = tempdir / "missing_gap"
        populate_repo(missing_gap_root)
        (missing_gap_root / GAP_NOTE_PATH).unlink()
        failures = collect_failures(missing_gap_root)
        assert failures == [
            "missing required file: Documentation/zigux/phase14-skbuff-attached-toolchain-gap.md"
        ]
        checks_run += 1

        missing_marker_root = tempdir / "missing_marker"
        populate_repo(missing_marker_root)
        write_text(
            missing_marker_root / GAP_NOTE_PATH,
            sample_gap_note().replace(
                "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_marker_root)
        assert failures == [
            "missing gap-note marker: - `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`"
        ]
        checks_run += 1

        stale_root = tempdir / "stale"
        populate_repo(stale_root)
        write_text(stale_root / ABSENT_PACKET_PATHS[1], "present\n")
        failures = collect_failures(stale_root)
        assert failures == [
            "gap note is stale because the skbuff anchor packet path exists again: zigux/tests/phase14_build.zig"
        ]
        checks_run += 1

        forbidden_root = tempdir / "forbidden"
        populate_repo(forbidden_root)
        write_text(
            forbidden_root / GAP_NOTE_PATH,
            sample_gap_note()
            + "\nThe lane again claims `phase14-skbuff-bridge-tests` as live proof.\n",
        )
        failures = collect_failures(forbidden_root)
        assert failures == [
            "forbidden live compile marker in gap note: phase14-skbuff-bridge-tests"
        ]
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=pass")
    print(f"PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the current Phase 14 skbuff attached-toolchain truthfulness packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.repo_root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE14_SKBUFF_TOOLCHAIN_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
