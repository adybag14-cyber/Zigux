#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_gap

Fail-closed checker for the current Phase 14 rollback-threshold automation gap
note. This stays intentionally narrow: it keeps the shared-smoke packet honest
about the current direct-readback split between the readable rollback packet
and the still-missing executable packet members without reopening anchor-local
Phase 14 ownership.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_gap"
SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
SHARED_SMOKE_GAP_PATH = Path("Documentation/zigux/phase14-shared-smoke-current-master-gap.md")
ROLLBACK_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
)
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-rollback-threshold-automation-gap.md")

ROLLBACK_NOTE_MARKERS = [
    "- rollback owner: `Repo Tooling Pod`",
    "- rollback threshold: `0` tolerated same-packet drifts across anchor-local manifests, anchor-local survey notes, the compile shard matrix, and shared replay wiring",
    "- fallback path: keep this shared smoke lane parked and rerun `make -C zigux phase14-validate` before reopening any anchor-local or shared follow-up",
    "- automatic return-to-blocked triggers:",
    "anchor-local manifest drift",
    "anchor-local survey note drift",
    "compile shard matrix drift",
    "shared replay wiring drift",
]

MISSING_EXECUTABLE_MARKERS = [
    "`scripts/zigux/validate-phase14.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/tests/phase14_build.zig`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`zigux/tests/phase14_end_to_end_smoke_survey.zig`",
]

GAP_NOTE_MARKERS = [
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=executable_packet_readback_gap`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`",
    "The directly readable rollback-threshold packet is stronger than an older docs-absence claim.",
    "But the executable rollback-threshold packet members still return missing-path results on the same exact contents path:",
    "The remaining same-lane gap is no longer a smaller Makefile-self-test inventory mismatch inside `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`.",
    "tighten broader Phase 14 reminder surfaces so they name the rollback-threshold note/checker layer as directly readable while keeping the executable layer explicit as the remaining gap.",
]

PROHIBITED_GAP_NOTE_MARKERS = [
    "makefile_selftest_coverage_drift",
    "Refresh `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`",
]

ROLLBACK_CHECKER_MARKERS = [
    'ROLLBACK_OWNER = "Repo Tooling Pod"',
    "ROLLBACK_THRESHOLD_MARKER =",
    "ROLLBACK_FALLBACK_PATH_MARKER =",
    "ROLLBACK_TRIGGER_MARKERS = [",
    '"  - anchor-local manifest drift"',
    '"  - anchor-local survey note drift"',
    '"  - compile shard matrix drift"',
    '"  - shared replay wiring drift"',
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    for rel in [
        SMOKE_NOTE_PATH,
        PRODUCTIZATION_GAP_PATH,
        SHARED_SMOKE_GAP_PATH,
        ROLLBACK_CHECKER_PATH,
        GAP_NOTE_PATH,
    ]:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    productization_gap = read_text(root, PRODUCTIZATION_GAP_PATH)
    shared_smoke_gap = read_text(root, SHARED_SMOKE_GAP_PATH)
    rollback_checker = read_text(root, ROLLBACK_CHECKER_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    for marker in ROLLBACK_NOTE_MARKERS:
        if marker not in smoke_note:
            errors.append(
                f"missing rollback-note marker in {SMOKE_NOTE_PATH.as_posix()}: {marker}"
            )

    for marker in MISSING_EXECUTABLE_MARKERS:
        if marker not in productization_gap:
            errors.append(
                f"missing productization-gap marker in {PRODUCTIZATION_GAP_PATH.as_posix()}: {marker}"
            )
        if marker not in shared_smoke_gap:
            errors.append(
                f"missing shared-smoke-gap marker in {SHARED_SMOKE_GAP_PATH.as_posix()}: {marker}"
            )
        if marker not in gap_note:
            errors.append(
                f"missing rollback-gap note marker in {GAP_NOTE_PATH.as_posix()}: {marker}"
            )

    for marker in GAP_NOTE_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing gap-note marker in {GAP_NOTE_PATH.as_posix()}: {marker}")

    for marker in PROHIBITED_GAP_NOTE_MARKERS:
        if marker in gap_note:
            errors.append(
                f"stale gap-note marker still present in {GAP_NOTE_PATH.as_posix()}: {marker}"
            )

    for marker in ROLLBACK_CHECKER_MARKERS:
        if marker not in rollback_checker:
            errors.append(
                "missing rollback-checker marker in "
                f"{ROLLBACK_CHECKER_PATH.as_posix()}: {marker}"
            )

    return errors


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_smoke_note() -> str:
    return """# Phase 14 End-to-End Smoke Survey

- rollback owner: `Repo Tooling Pod`
- rollback threshold: `0` tolerated same-packet drifts across anchor-local manifests, anchor-local survey notes, the compile shard matrix, and shared replay wiring
- fallback path: keep this shared smoke lane parked and rerun `make -C zigux phase14-validate` before reopening any anchor-local or shared follow-up
- automatic return-to-blocked triggers:
  - anchor-local manifest drift
  - anchor-local survey note drift
  - compile shard matrix drift
  - shared replay wiring drift
"""


def fixture_productization_gap() -> str:
    return """# Phase 14 Productization Gap Survey

- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
"""


def fixture_shared_smoke_gap() -> str:
    return """# Phase 14 Shared Smoke Current-Master Gap

- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
"""


def fixture_rollback_checker() -> str:
    return """#!/usr/bin/env python3
ROLLBACK_OWNER = \"Repo Tooling Pod\"
ROLLBACK_THRESHOLD_MARKER = \"threshold\"
ROLLBACK_FALLBACK_PATH_MARKER = \"fallback\"
ROLLBACK_TRIGGER_MARKERS = [
    \"  - anchor-local manifest drift\",
    \"  - anchor-local survey note drift\",
    \"  - compile shard matrix drift\",
    \"  - shared replay wiring drift\",
]
"""


def fixture_gap_note() -> str:
    return """# Phase 14 Rollback-Threshold Automation Gap

## Status

- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=executable_packet_readback_gap`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`

## Why this gap note exists

The directly readable rollback-threshold packet is stronger than an older docs-absence claim.
But the executable rollback-threshold packet members still return missing-path results on the same exact contents path:

- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`

## Current bounded gap

The remaining same-lane gap is no longer a smaller Makefile-self-test inventory mismatch inside `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`.

## Next bounded fix

Either re-materialize the missing executable packet members above on current `master`, or tighten broader Phase 14 reminder surfaces so they name the rollback-threshold note/checker layer as directly readable while keeping the executable layer explicit as the remaining gap.
"""


def run_self_test() -> int:
    cases = 5
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(root, SHARED_SMOKE_GAP_PATH, fixture_shared_smoke_gap())
        write(root, ROLLBACK_CHECKER_PATH, fixture_rollback_checker())
        write(root, GAP_NOTE_PATH, fixture_gap_note())
        errors = check(root)
        if errors:
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(
            root,
            PRODUCTIZATION_GAP_PATH,
            fixture_productization_gap().replace(
                "- `zigux/tests/phase14_end_to_end_smoke_manifest.json`\n", "", 1
            ),
        )
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing executable-marker failure")
            return 1

        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(
            root,
            GAP_NOTE_PATH,
            fixture_gap_note() + "\nRefresh `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`\n",
        )
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected stale gap-note guidance failure")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(
            root,
            SMOKE_NOTE_PATH,
            fixture_smoke_note().replace(
                "- automatic return-to-blocked triggers:\n", "", 1
            ),
        )
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing rollback-trigger heading failure")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(
            root,
            ROLLBACK_CHECKER_PATH,
            fixture_rollback_checker().replace(
                '    \"  - shared replay wiring drift\",\n', "", 1
            ),
        )
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing rollback-checker trigger failure")
            return 1

    print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=pass")
    print(f"PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST_CASES={cases}")
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
