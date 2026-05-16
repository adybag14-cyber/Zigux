#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=skbuff_toolchain_gap

Fail-closed checker for the current Phase 14 skbuff attached-toolchain gap.
This intentionally stays in the truthfulness lane: it guards the survey note's
absent-packet state instead of reopening skbuff helper delivery.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=skbuff_toolchain_gap"
SKBUFF_NOTE_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-skbuff-attached-toolchain-gap.md")

SKBUFF_NOTE_MARKERS = [
    "- `PHASE14_LANE_KEY=P14-L11`",
    "- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`",
    "- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`",
    "- current `master` no longer exposes `zigux/tests/phase14_build.zig`",
    "- current `master` no longer exposes `net/core/skbuff_bridge.zig`",
    "- because those packet files are absent, there is no live `phase14-skbuff-bridge-tests` or `full_bundle_only` replay route to validate on current `master`",
]

GAP_NOTE_MARKERS = [
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP=present`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_KIND=anchor_packet_absent_under_attached_toolchain_policy`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_SCOPE=skbuff_packet_truthfulness_only`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`",
    "there is no live\nskbuff-local packet to compile on current `master`",
    "`scripts/zigux/check-phase14-skbuff-toolchain-gap.py` keeps this gap note and",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    for rel in [SKBUFF_NOTE_PATH, GAP_NOTE_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    skbuff_note = read_text(root, SKBUFF_NOTE_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    for marker in SKBUFF_NOTE_MARKERS:
        if marker not in skbuff_note:
            errors.append(
                f"missing skbuff survey marker in {SKBUFF_NOTE_PATH.as_posix()}: {marker}"
            )

    for marker in GAP_NOTE_MARKERS:
        if marker not in gap_note:
            errors.append(
                f"missing gap-note marker in {GAP_NOTE_PATH.as_posix()}: {marker}"
            )

    false_compile_claims = [
        "attached-toolchain command inventory",
        "live compile evidence.",
    ]
    if all(claim in skbuff_note for claim in false_compile_claims):
        errors.append("skbuff survey note now claims attached-toolchain compile evidence")

    return errors


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_skbuff_note() -> str:
    return """# Phase 14 Skbuff Bridge Survey

## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing`

## Compile Evidence
- current `master` no longer exposes `zigux/tests/phase14_skbuff_bridge.zig`
- current `master` no longer exposes `zigux/tests/phase14_build.zig`
- current `master` no longer exposes `net/core/skbuff_bridge.zig`
- because those packet files are absent, there is no live `phase14-skbuff-bridge-tests` or `full_bundle_only` replay route to validate on current `master`
"""


def fixture_gap_note() -> str:
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
"""


def run_self_test() -> int:
    cases = 4
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root, SKBUFF_NOTE_PATH, fixture_skbuff_note())
        write(root, GAP_NOTE_PATH, fixture_gap_note())
        errors = check(root)
        if errors:
            print("PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(
            root,
            GAP_NOTE_PATH,
            fixture_gap_note().replace(
                "- `PHASE14_SKBUFF_TOOLCHAIN_GAP_OWNER=Repo Tooling Pod`\n", ""
            ),
        )
        if not check(root):
            print("PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=fail")
            print("expected missing owner marker to fail")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(
            root,
            SKBUFF_NOTE_PATH,
            fixture_skbuff_note().replace(
                "- current `master` no longer exposes `zigux/tests/phase14_build.zig`\n",
                "",
            ),
        )
        if not check(root):
            print("PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=fail")
            print("expected missing absent-packet marker to fail")
            return 1

        write(root, SKBUFF_NOTE_PATH, fixture_skbuff_note())
        write(
            root,
            GAP_NOTE_PATH,
            fixture_gap_note().replace(
                "there is no live\nskbuff-local packet to compile on current `master`",
                "there is attached-toolchain command inventory and live compile evidence.",
            ),
        )
        if not check(root):
            print("PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=fail")
            print("expected false compile claim marker drift to fail")
            return 1

    print("PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST=pass")
    print(f"PHASE14_SKBUFF_TOOLCHAIN_GAP_SELF_TEST_CASES={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(Path.cwd())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
