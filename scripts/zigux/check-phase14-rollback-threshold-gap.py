#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_gap

Fail-closed checker for the current Phase 14 rollback-threshold automation gap
note. This stays intentionally narrow: it keeps the shared-smoke packet honest
about one current checker-local drift without reopening anchor-local Phase 14
ownership.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=rollback_threshold_gap"
SMOKE_NOTE_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
RELEASE_NOTE_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
ROLLBACK_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
)
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-rollback-threshold-automation-gap.md")

SHARED_PACKET_MARKERS = [
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`",
]

GAP_NOTE_MARKERS = [
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=makefile_selftest_coverage_drift`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`",
    "Refresh `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
]

MISSING_FROM_ROLLBACK_CHECKER = [
    '"\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test"',
    '"\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py"',
    '"\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test"',
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def source_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in source_text():
        errors.append("checker marker missing from checker source")

    for rel in [SMOKE_NOTE_PATH, RELEASE_NOTE_PATH, ROLLBACK_CHECKER_PATH, GAP_NOTE_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    smoke_note = read_text(root, SMOKE_NOTE_PATH)
    release_note = read_text(root, RELEASE_NOTE_PATH)
    rollback_checker = read_text(root, ROLLBACK_CHECKER_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    for marker in SHARED_PACKET_MARKERS:
        if marker not in smoke_note:
            errors.append(f"missing shared-smoke marker in {SMOKE_NOTE_PATH.as_posix()}: {marker}")

    if "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`" not in release_note:
        errors.append(
            f"missing release-boundary marker in {RELEASE_NOTE_PATH.as_posix()}: "
            "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`"
        )

    for marker in GAP_NOTE_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing gap-note marker in {GAP_NOTE_PATH.as_posix()}: {marker}")

    for marker in MISSING_FROM_ROLLBACK_CHECKER:
        if marker in rollback_checker:
            errors.append(
                "rollback-threshold checker no longer shows the documented gap for "
                f"{marker}"
            )

    return errors


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_smoke_note() -> str:
    return """# Phase 14 End-to-End Smoke Survey

- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test`
"""


def fixture_release_note() -> str:
    return """## Status

- shared smoke packet: `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
"""


def fixture_rollback_checker() -> str:
    return """#!/usr/bin/env python3
MAKEFILE_EXACT_LINES = [
    "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]
"""


def fixture_gap_note() -> str:
    return """# Phase 14 Rollback-Threshold Automation Gap

- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=makefile_selftest_coverage_drift`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`

Refresh `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
"""


def run_self_test() -> int:
    cases = 4
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, RELEASE_NOTE_PATH, fixture_release_note())
        write(root, ROLLBACK_CHECKER_PATH, fixture_rollback_checker())
        write(root, GAP_NOTE_PATH, fixture_gap_note())
        errors = check(root)
        if errors:
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note().replace(
            "- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`\n", ""
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing owner marker to fail")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note().replace(
            "- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`\n", ""
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing smoke-note self-test marker to fail")
            return 1

        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, ROLLBACK_CHECKER_PATH, fixture_rollback_checker().replace(
            "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
            "\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected rollback-checker gap closure to fail this gap note")
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
