#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SURVEY_NOTE_PATH = "Documentation/zigux/phase11-bcm2835-wdt-survey.md"
SLICE_NOTE_PATH = "Documentation/zigux/phase11-bcm2835-wdt-slice.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
SHARED_CONTRACT_PATH = "Documentation/zigux/phase11-shared-replay-contract.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase11-driver-lane-sequencing.md"
MANIFEST_PATH = "zigux/tests/phase11_bcm2835_wdt_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/phase11_bcm2835_wdt_survey.zig"
VERIFY_REPLAY_PATH = "drivers/watchdog/bcm2835_wdt_verify.zig"
BUILD_PATH = "zigux/tests/phase11_build.zig"
SCRIPT_PATH = "scripts/zigux/check-phase11-bcm2835-wdt-packet.py"

REQUIRED_SURVEY_NOTE_MARKERS = [
    "`P11-L08` packet identity",
    "`P11-L10`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
]

REQUIRED_SLICE_NOTE_MARKERS = [
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "tiny registration-outcome summary",
    "tiny platform-registration and PM-base handoff summary",
]

REQUIRED_VALIDATION_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`",
    "`P11-L10`",
]

REQUIRED_SHARED_CONTRACT_MARKERS = [
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "The dedicated archival bcm2835 evidence also stays explicit beside that shared route:",
    "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
    "`zigux/tests/phase11_bcm2835_wdt_survey.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
]

REQUIRED_LANE_SEQUENCING_MARKERS = [
    "`P11-L08` bcm2835 watchdog lane owns the bounded bcm2835 packet:",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "dedicated bcm2835 packet checker",
]

REQUIRED_MANIFEST_MARKERS = [
    '"lane_key": "P11-L08"',
    '"id": "phase11-bcm2835-wdt-survey-gate"',
    '"id": "phase11-bcm2835-wdt-validation-matrix"',
    '"id": "phase11-bcm2835-wdt-platform-registration"',
]

REQUIRED_BUILD_MARKERS = [
    '.name = "phase11-bcm2835-wdt-tests"',
    '.name = "phase11-bcm2835-wdt-verify-tests"',
    '.name = "phase11-bcm2835-wdt-survey-tests"',
]

SELF_TEST_CASE_COUNT = 16


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [
        SURVEY_NOTE_PATH,
        SLICE_NOTE_PATH,
        VALIDATION_MATRIX_PATH,
        SHARED_CONTRACT_PATH,
        LANE_SEQUENCING_PATH,
        MANIFEST_PATH,
        SURVEY_GATE_PATH,
        VERIFY_REPLAY_PATH,
        BUILD_PATH,
        SCRIPT_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for marker in REQUIRED_SURVEY_NOTE_MARKERS:
        if marker not in read_text(root, SURVEY_NOTE_PATH):
            failures.append(f"survey_note:{marker}")
    for marker in REQUIRED_SLICE_NOTE_MARKERS:
        if marker not in read_text(root, SLICE_NOTE_PATH):
            failures.append(f"slice_note:{marker}")
    for marker in REQUIRED_VALIDATION_MATRIX_MARKERS:
        if marker not in read_text(root, VALIDATION_MATRIX_PATH):
            failures.append(f"validation_matrix:{marker}")
    for marker in REQUIRED_SHARED_CONTRACT_MARKERS:
        if marker not in read_text(root, SHARED_CONTRACT_PATH):
            failures.append(f"shared_contract:{marker}")
    for marker in REQUIRED_LANE_SEQUENCING_MARKERS:
        if marker not in read_text(root, LANE_SEQUENCING_PATH):
            failures.append(f"lane_sequencing:{marker}")
    for marker in REQUIRED_MANIFEST_MARKERS:
        if marker not in read_text(root, MANIFEST_PATH):
            failures.append(f"manifest:{marker}")
    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in read_text(root, BUILD_PATH):
            failures.append(f"build:{marker}")
    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / SURVEY_NOTE_PATH,
        """# Phase 11 BCM2835 Watchdog Survey

This archival watchdog note now keeps `P11-L08` packet identity explicit beside the current bcm2835 review surface, while current scheduled continuity is tracked through `P11-L10`.

- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- run `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test` for the synthetic packet
- run `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py` for the live repo packet
""",
    )
    write_text(
        root / SLICE_NOTE_PATH,
        """# Phase 11 BCM2835 Watchdog Slice

- adds a tiny registration-outcome summary for register-device success versus failure, probe-error return intent, and poweroff-handler claim follow-through or blocking when registration does not complete
- adds a tiny platform-registration and PM-base handoff summary for parent attachment, PM base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability

`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` now records the first bounded hardware-validation matrix for watchdog metadata, timeout conversion, register-image transition coverage, probe-time bookkeeping, registration ownership, registration-outcome failure handling, platform handoff prerequisites, poweroff-path sequencing, and remove-time teardown scope without widening into live PM base or poweroff plumbing.
""",
    )
    write_text(
        root / VALIDATION_MATRIX_PATH,
        """# Phase 11 BCM2835 Watchdog Validation Matrix

- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`
- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
- `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`
- current scheduled continuity is tracked through `P11-L10`
""",
    )
    write_text(
        root / SHARED_CONTRACT_PATH,
        """# Phase 11 Shared Replay Contract

- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`

The dedicated archival bcm2835 evidence also stays explicit beside that shared route:

- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `zigux/tests/phase11_bcm2835_wdt_manifest.json`
- `zigux/tests/phase11_bcm2835_wdt_survey.zig`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`
""",
    )
    write_text(
        root / LANE_SEQUENCING_PATH,
        """# Phase 11 Driver Lane Sequencing

`P11-L08` bcm2835 watchdog lane owns the bounded bcm2835 packet:

- `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`

The lane keeps the dedicated bcm2835 packet checker aligned with the archival review packet.
""",
    )
    write_text(
        root / MANIFEST_PATH,
        """{
  "lane_key": "P11-L08",
  "gaps": [
    {"id": "phase11-bcm2835-wdt-survey-gate"},
    {"id": "phase11-bcm2835-wdt-validation-matrix"},
    {"id": "phase11-bcm2835-wdt-platform-registration"}
  ]
}
""",
    )
    write_text(
        root / SURVEY_GATE_PATH,
        """const std = @import(\"std\");
test \"synthetic bcm2835 survey gate\" {
    try std.testing.expect(true);
}
""",
    )
    write_text(
        root / VERIFY_REPLAY_PATH,
        """const std = @import(\"std\");
test \"synthetic bcm2835 verify replay\" {
    try std.testing.expect(true);
}
""",
    )
    write_text(
        root / BUILD_PATH,
        """const phase11_bcm2835_wdt_tests = b.addTest(.{ .name = \"phase11-bcm2835-wdt-tests\" });
const bcm2835_wdt_verify_tests = b.addTest(.{ .name = \"phase11-bcm2835-wdt-verify-tests\" });
const phase11_bcm2835_wdt_survey_tests = b.addTest(.{ .name = \"phase11-bcm2835-wdt-survey-tests\" });
""",
    )
    write_text(root / SCRIPT_PATH, "#!/usr/bin/env python3\nprint(\"synthetic checker\")\n")


def expect_failure(root: Path, rel_path: str, marker: str, expected_failure: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")


def expect_missing_file(root: Path, rel_path: str) -> None:
    (root / rel_path).unlink()
    failures = validate(root)
    expected_failure = f"missing_file:{rel_path}"
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11_bcm2835_packet_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1
        checks = [
            (SURVEY_NOTE_PATH, "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`", "survey_note:`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`"),
            (SURVEY_NOTE_PATH, "`P11-L10`", "survey_note:`P11-L10`"),
            (SURVEY_NOTE_PATH, "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`", "survey_note:`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`"),
            (SLICE_NOTE_PATH, "tiny registration-outcome summary", "slice_note:tiny registration-outcome summary"),
            (VALIDATION_MATRIX_PATH, "`drivers/watchdog/bcm2835_wdt_verify.zig`", "validation_matrix:`drivers/watchdog/bcm2835_wdt_verify.zig`"),
            (VALIDATION_MATRIX_PATH, "`P11-L10`", "validation_matrix:`P11-L10`"),
            (VALIDATION_MATRIX_PATH, "`phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`", "validation_matrix:`phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`"),
            (SHARED_CONTRACT_PATH, "The dedicated archival bcm2835 evidence also stays explicit beside that shared route:", "shared_contract:The dedicated archival bcm2835 evidence also stays explicit beside that shared route:"),
            (SHARED_CONTRACT_PATH, "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`", "shared_contract:`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`"),
            (LANE_SEQUENCING_PATH, "dedicated bcm2835 packet checker", "lane_sequencing:dedicated bcm2835 packet checker"),
            (MANIFEST_PATH, '"id": "phase11-bcm2835-wdt-validation-matrix"', 'manifest:"id": "phase11-bcm2835-wdt-validation-matrix"'),
            (BUILD_PATH, '.name = "phase11-bcm2835-wdt-survey-tests"', 'build:.name = "phase11-bcm2835-wdt-survey-tests"'),
        ]
        for rel_path, marker, expected in checks:
            write_fixture_tree(root)
            try:
                expect_failure(root, rel_path, marker, expected)
            except AssertionError as exc:
                print(str(exc), file=sys.stderr)
                return 1
        for rel_path in [SLICE_NOTE_PATH, SURVEY_GATE_PATH, VERIFY_REPLAY_PATH, SCRIPT_PATH]:
            write_fixture_tree(root)
            try:
                expect_missing_file(root, rel_path)
            except AssertionError as exc:
                print(str(exc), file=sys.stderr)
                return 1
    print("PHASE11_BCM2835_WDT_PACKET_SELFTEST=pass")
    print(f"PHASE11_BCM2835_WDT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the dedicated Phase 11 bcm2835 watchdog review packet.")
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against a synthetic fixture tree")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("PHASE11_BCM2835_WDT_PACKET=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
