#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rollback_threshold_gap

Fail-closed checker for the current Phase 14 rollback-threshold automation gap
note. This keeps the dedicated rollback note aligned with the returned shared
smoke route, validator, release-boundary checker, manifest, and current
exact-readback gap split without reopening anchor-local ownership.
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
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")
RELEASE_BOUNDARY_CHECKER_PATH = Path(
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py"
)
MAKEFILE_PATH = Path("zigux/Makefile")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
GAP_NOTE_PATH = Path("Documentation/zigux/phase14-rollback-threshold-automation-gap.md")

ROLLBACK_SMOKE_MARKERS = [
    "- `PHASE14_DIRECT_DOC_PACKET=present`",
    "  * rollback owner: `Repo Tooling Pod`",
    "  * rollback threshold: `0` tolerated same-packet drifts",
    "  * fallback path: keep this shared smoke lane aligned",
    "  * automatic return-to-blocked triggers:",
    "    * rollback-threshold-sequencing drift",
]

DIRECT_PACKET_MARKERS = [
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`scripts/zigux/validate-phase14.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "`zigux/Makefile`",
]

EXECUTABLE_GAP_MARKERS = [
    "`zigux/tests/phase14_build.zig`",
    "`zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "`zigux/tests/phase14_skbuff_bridge.zig`",
    "`zigux/tests/phase14_rcu_tree_survey.zig`",
    "`net/core/skbuff_bridge.zig`",
]

GAP_NOTE_MARKERS = [
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=partial_executable_packet_readback_gap`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`",
    "- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`",
    "The dedicated rollback story is no longer a checker-local self-test inventory drift.",
    "That means same-lane reminder surfaces should describe rollback-threshold automation as directly readable route, checker, validator, manifest, and Makefile evidence while still keeping the broader executable layer explicit as the remaining readback gap.",
]

PROHIBITED_GAP_NOTE_MARKERS = [
    "makefile_selftest_coverage_drift",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test`",
    "The live shared packet has advanced, but the dedicated rollback-threshold checker has not yet caught up",
]

MAKEFILE_MARKERS = [
    "phase14-validate:",
    "scripts/zigux/validate-phase14.py --self-test",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]

VALIDATOR_MARKERS = [
    "PHASE14_VALIDATION=pass",
    "PHASE14_VALIDATOR_SELF_TEST=pass",
    "ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH",
    "RELEASE_BOUNDARY_CHECKER_PATH",
    "END_TO_END_SMOKE_MANIFEST_PATH",
]

RELEASE_BOUNDARY_CHECKER_MARKERS = [
    "PHASE14_CHECK_PACKET=release_boundary_exact_counts",
    "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass",
]

MANIFEST_MARKERS = [
    '"phase14_validate_runs_rollback_threshold_sequencing": true',
    '"phase14_make_smoke_target_present": false',
    '"smoke_commands": [',
    '"make -C zigux phase14-validate"',
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
        VALIDATOR_PATH,
        RELEASE_BOUNDARY_CHECKER_PATH,
        MAKEFILE_PATH,
        MANIFEST_PATH,
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
    validator = read_text(root, VALIDATOR_PATH)
    release_boundary_checker = read_text(root, RELEASE_BOUNDARY_CHECKER_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    manifest = read_text(root, MANIFEST_PATH)
    gap_note = read_text(root, GAP_NOTE_PATH)

    for marker in ROLLBACK_SMOKE_MARKERS:
        if marker not in smoke_note:
            errors.append(
                f"missing rollback smoke marker in {SMOKE_NOTE_PATH.as_posix()}: {marker}"
            )

    for marker in DIRECT_PACKET_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing direct packet marker in {GAP_NOTE_PATH.as_posix()}: {marker}")
        if marker not in productization_gap:
            errors.append(
                f"missing productization marker in {PRODUCTIZATION_GAP_PATH.as_posix()}: {marker}"
            )
        if marker not in shared_smoke_gap:
            errors.append(
                f"missing shared-smoke-gap marker in {SHARED_SMOKE_GAP_PATH.as_posix()}: {marker}"
            )

    for marker in EXECUTABLE_GAP_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing executable gap marker in {GAP_NOTE_PATH.as_posix()}: {marker}")
        if marker not in productization_gap:
            errors.append(
                f"missing productization executable-gap marker in {PRODUCTIZATION_GAP_PATH.as_posix()}: {marker}"
            )
        if marker not in shared_smoke_gap:
            errors.append(
                f"missing shared-smoke executable-gap marker in {SHARED_SMOKE_GAP_PATH.as_posix()}: {marker}"
            )

    for marker in GAP_NOTE_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing gap-note marker in {GAP_NOTE_PATH.as_posix()}: {marker}")

    for marker in PROHIBITED_GAP_NOTE_MARKERS:
        if marker in gap_note:
            errors.append(
                f"stale gap-note marker still present in {GAP_NOTE_PATH.as_posix()}: {marker}"
            )

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            errors.append(f"missing Makefile marker in {MAKEFILE_PATH.as_posix()}: {marker}")

    for marker in VALIDATOR_MARKERS:
        if marker not in validator:
            errors.append(f"missing validator marker in {VALIDATOR_PATH.as_posix()}: {marker}")

    for marker in RELEASE_BOUNDARY_CHECKER_MARKERS:
        if marker not in release_boundary_checker:
            errors.append(
                "missing release-boundary checker marker in "
                f"{RELEASE_BOUNDARY_CHECKER_PATH.as_posix()}: {marker}"
            )

    for marker in MANIFEST_MARKERS:
        if marker not in manifest:
            errors.append(f"missing manifest marker in {MANIFEST_PATH.as_posix()}: {marker}")

    if "PHASE14_CHECK_PACKET=rollback_threshold_sequencing" not in rollback_checker:
        errors.append(
            "missing rollback-checker packet marker in "
            f"{ROLLBACK_CHECKER_PATH.as_posix()}"
        )

    return errors


def write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_smoke_note() -> str:
    return """# Phase 14 End-to-End Smoke Survey

- `PHASE14_DIRECT_DOC_PACKET=present`
  * rollback owner: `Repo Tooling Pod`
  * rollback threshold: `0` tolerated same-packet drifts
  * fallback path: keep this shared smoke lane aligned
  * automatic return-to-blocked triggers:
    * rollback-threshold-sequencing drift
"""


def fixture_productization_gap() -> str:
    return """# Phase 14 Productization Gap Survey

- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/Makefile`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `net/core/skbuff_bridge.zig`
"""


def fixture_shared_smoke_gap() -> str:
    return fixture_productization_gap().replace(
        "# Phase 14 Productization Gap Survey", "# Phase 14 Shared Smoke Current-Master Gap"
    )


def fixture_rollback_checker() -> str:
    return 'PHASE14_CHECK_PACKET=rollback_threshold_sequencing\n'


def fixture_validator() -> str:
    return """PHASE14_VALIDATION=pass
PHASE14_VALIDATOR_SELF_TEST=pass
ROLLBACK_THRESHOLD_SEQUENCING_CHECKER_PATH
RELEASE_BOUNDARY_CHECKER_PATH
END_TO_END_SMOKE_MANIFEST_PATH
"""


def fixture_release_boundary_checker() -> str:
    return """PHASE14_CHECK_PACKET=release_boundary_exact_counts
PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass
"""


def fixture_makefile() -> str:
    return """phase14-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
"""


def fixture_manifest() -> str:
    return """{
  "smoke_commands": [
    "make -C zigux phase14-validate"
  ],
  "survey_summary": {
    "phase14_make_smoke_target_present": false,
    "phase14_validate_runs_rollback_threshold_sequencing": true
  }
}
"""


def fixture_gap_note() -> str:
    return """# Phase 14 Rollback-Threshold Automation Gap

## Status

- `PHASE14_ROLLBACK_THRESHOLD_GAP=present`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_KIND=partial_executable_packet_readback_gap`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_SCOPE=shared_smoke_packet_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_STATUS_BUCKET=study_only`
- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`

The dedicated rollback story is no longer a checker-local self-test inventory drift.

- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `zigux/Makefile`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_skbuff_bridge.zig`
- `zigux/tests/phase14_rcu_tree_survey.zig`
- `net/core/skbuff_bridge.zig`

That means same-lane reminder surfaces should describe rollback-threshold automation as directly readable route, checker, validator, manifest, and Makefile evidence while still keeping the broader executable layer explicit as the remaining readback gap.
"""


def run_self_test() -> int:
    cases = 5
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root, SMOKE_NOTE_PATH, fixture_smoke_note())
        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
        write(root, SHARED_SMOKE_GAP_PATH, fixture_shared_smoke_gap())
        write(root, ROLLBACK_CHECKER_PATH, fixture_rollback_checker())
        write(root, VALIDATOR_PATH, fixture_validator())
        write(root, RELEASE_BOUNDARY_CHECKER_PATH, fixture_release_boundary_checker())
        write(root, MAKEFILE_PATH, fixture_makefile())
        write(root, MANIFEST_PATH, fixture_manifest())
        write(root, GAP_NOTE_PATH, fixture_gap_note())
        errors = check(root)
        if errors:
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note().replace(
            "- `PHASE14_ROLLBACK_THRESHOLD_GAP_OWNER=Repo Tooling Pod`\n", "", 1
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing gap-note owner failure")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(root, MANIFEST_PATH, fixture_manifest().replace(
            '"phase14_validate_runs_rollback_threshold_sequencing": true', ""
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing manifest sequencing marker failure")
            return 1

        write(root, MANIFEST_PATH, fixture_manifest())
        write(root, GAP_NOTE_PATH, fixture_gap_note().replace(
            "partial_executable_packet_readback_gap", "makefile_selftest_coverage_drift", 1
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected stale gap-kind failure")
            return 1

        write(root, GAP_NOTE_PATH, fixture_gap_note())
        write(root, MAKEFILE_PATH, fixture_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test\n",
            "",
            1,
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing Makefile rollback self-test failure")
            return 1

        write(root, MAKEFILE_PATH, fixture_makefile())
        write(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap().replace(
            "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`\n", "", 1
        ))
        if not check(root):
            print("PHASE14_ROLLBACK_THRESHOLD_GAP_SELF_TEST=fail")
            print("expected missing productization executable-gap marker failure")
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