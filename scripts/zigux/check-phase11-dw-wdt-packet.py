#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SURVEY_NOTE_PATH = "Documentation/zigux/phase11-dw-wdt-survey.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-dw-wdt-validation-matrix.md"
SHARED_REPLAY_CONTRACT_PATH = "Documentation/zigux/phase11-shared-replay-contract.md"
TEARDOWN_NOTE_PATH = "Documentation/zigux/phase11-dw-wdt-teardown-note.md"
MANIFEST_PATH = "zigux/tests/phase11_dw_wdt_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/phase11_dw_wdt_survey.zig"
REGISTRATION_SCAFFOLD_PATH = "zigux/tests/phase11_dw_wdt_registration_scaffold.zig"
VERIFY_REPLAY_PATH = "drivers/watchdog/dw_wdt_verify.zig"
BUILD_PATH = "zigux/tests/phase11_build.zig"
SCRIPT_PATH = "scripts/zigux/check-phase11-dw-wdt-packet.py"

REQUIRED_SURVEY_NOTE_MARKERS = [
    "lane identity `P11-L12`",
    "platform-resource preflight",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py`",
]

REQUIRED_VALIDATION_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-dw-wdt-survey.md`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`",
    "`scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`",
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` aligned so the DesignWare-local packet checker stays fail-closed around the current starter without reopening broader shared Phase 11 contract surfaces",
]

REQUIRED_SHARED_REPLAY_MARKERS = [
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-survey.md`",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`",
]

REQUIRED_TEARDOWN_NOTE_MARKERS = [
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`stop()`",
    "`removeSummary()`",
    "`teardownSummary()`",
    "`platformRegistrationScaffoldSummary()`",
    "continued-heartbeat",
    "`dw_wdt_drv_shutdown`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
]

REQUIRED_MANIFEST_MARKERS = [
    '"lane_key": "P11-L12"',
    '"id": "phase11-dw-wdt-survey-gate"',
    '"id": "phase11-dw-wdt-platform-resource-preflight"',
    '"id": "phase11-dw-wdt-registration-order-scaffold"',
    '"id": "phase11-dw-wdt-teardown-parity"',
    '"id": "phase11-dw-wdt-platform-registration-scaffold"',
]

REQUIRED_BUILD_MARKERS = [
    '.name = "phase11-dw-wdt-tests"',
    '.name = "phase11-dw-wdt-registration-scaffold-tests"',
    '.name = "phase11-dw-wdt-verify-tests"',
    '.name = "phase11-dw-wdt-survey-tests"',
]

SELF_TEST_CASE_COUNT = 28


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [
        SURVEY_NOTE_PATH,
        VALIDATION_MATRIX_PATH,
        SHARED_REPLAY_CONTRACT_PATH,
        TEARDOWN_NOTE_PATH,
        MANIFEST_PATH,
        SURVEY_GATE_PATH,
        REGISTRATION_SCAFFOLD_PATH,
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
    for marker in REQUIRED_VALIDATION_MATRIX_MARKERS:
        if marker not in read_text(root, VALIDATION_MATRIX_PATH):
            failures.append(f"validation_matrix:{marker}")
    for marker in REQUIRED_SHARED_REPLAY_MARKERS:
        if marker not in read_text(root, SHARED_REPLAY_CONTRACT_PATH):
            failures.append(f"shared_replay:{marker}")
    for marker in REQUIRED_TEARDOWN_NOTE_MARKERS:
        if marker not in read_text(root, TEARDOWN_NOTE_PATH):
            failures.append(f"teardown_note:{marker}")
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
        """# Phase 11 DesignWare Watchdog Survey

This survey note keeps lane identity `P11-L12` explicit beside the current review packet.

- platform-resource preflight
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- run `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test` for the synthetic packet
- run `python3 scripts/zigux/check-phase11-dw-wdt-packet.py` for the live repo packet
""",
    )
    write_text(
        root / VALIDATION_MATRIX_PATH,
        """# Phase 11 DesignWare Watchdog Validation Matrix

- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` aligned so the DesignWare-local packet checker stays fail-closed around the current starter without reopening broader shared Phase 11 contract surfaces
""",
    )
    write_text(
        root / SHARED_REPLAY_CONTRACT_PATH,
        """# Phase 11 Shared Replay Contract

- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `zigux/tests/phase11_dw_wdt_manifest.json`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `scripts/zigux/check-phase11-dw-wdt-packet.py`
- `python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`
- `python3 scripts/zigux/check-phase11-dw-wdt-packet.py`
- `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`
""",
    )
    write_text(
        root / TEARDOWN_NOTE_PATH,
        """# Phase 11 DesignWare Watchdog Teardown Note

- `drivers/watchdog/dw_wdt_verify.zig`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `stop()`
- `removeSummary()`
- `teardownSummary()`
- `platformRegistrationScaffoldSummary()`
- continued-heartbeat
- `dw_wdt_drv_shutdown`
- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`
""",
    )
    write_text(
        root / MANIFEST_PATH,
        """{
  "lane_key": "P11-L12",
  "gaps": [
    {"id": "phase11-dw-wdt-survey-gate"},
    {"id": "phase11-dw-wdt-platform-resource-preflight"},
    {"id": "phase11-dw-wdt-registration-order-scaffold"},
    {"id": "phase11-dw-wdt-teardown-parity"},
    {"id": "phase11-dw-wdt-platform-registration-scaffold"}
  ]
}
""",
    )
    write_text(root / SURVEY_GATE_PATH, "const std = @import(\"std\");\ntest \"synthetic dw survey gate\" { try std.testing.expect(true); }\n")
    write_text(root / REGISTRATION_SCAFFOLD_PATH, "const std = @import(\"std\");\ntest \"synthetic dw registration scaffold\" { try std.testing.expect(true); }\n")
    write_text(root / VERIFY_REPLAY_PATH, "const std = @import(\"std\");\ntest \"synthetic dw verify replay\" { try std.testing.expect(true); }\n")
    write_text(
        root / BUILD_PATH,
        """const phase11_dw_wdt_tests = b.addTest(.{ .name = \"phase11-dw-wdt-tests\" });
const phase11_dw_wdt_registration_scaffold_tests = b.addTest(.{ .name = \"phase11-dw-wdt-registration-scaffold-tests\" });
const dw_wdt_verify_tests = b.addTest(.{ .name = \"phase11-dw-wdt-verify-tests\" });
const phase11_dw_wdt_survey_tests = b.addTest(.{ .name = \"phase11-dw-wdt-survey-tests\" });
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
    with tempfile.TemporaryDirectory(prefix="phase11_dw_packet_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1
        checks = [
            (SURVEY_NOTE_PATH, "platform-resource preflight", "survey_note:platform-resource preflight"),
            (SURVEY_NOTE_PATH, "`scripts/zigux/check-phase11-dw-wdt-packet.py`", "survey_note:`scripts/zigux/check-phase11-dw-wdt-packet.py`"),
            (SURVEY_NOTE_PATH, "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`", "survey_note:`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`"),
            (VALIDATION_MATRIX_PATH, "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`", "validation_matrix:`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`"),
            (VALIDATION_MATRIX_PATH, "`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`", "validation_matrix:`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`"),
            (VALIDATION_MATRIX_PATH, "`scripts/zigux/README.md`", "validation_matrix:keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `scripts/zigux/check-phase11-dw-wdt-packet.py` aligned so the DesignWare-local packet checker stays fail-closed around the current starter without reopening broader shared Phase 11 contract surfaces"),
            (SHARED_REPLAY_CONTRACT_PATH, "`scripts/zigux/check-phase11-dw-wdt-packet.py`", "shared_replay:`scripts/zigux/check-phase11-dw-wdt-packet.py`"),
            (SHARED_REPLAY_CONTRACT_PATH, "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`", "shared_replay:`python3 scripts/zigux/check-phase11-dw-wdt-packet.py --self-test`"),
            (SHARED_REPLAY_CONTRACT_PATH, "`python3 scripts/zigux/check-phase11-dw-wdt-packet.py`", "shared_replay:`python3 scripts/zigux/check-phase11-dw-wdt-packet.py`"),
            (SHARED_REPLAY_CONTRACT_PATH, "`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`", "shared_replay:`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`"),
            (TEARDOWN_NOTE_PATH, "`stop()`", "teardown_note:`stop()`"),
            (TEARDOWN_NOTE_PATH, "`teardownSummary()`", "teardown_note:`teardownSummary()`"),
            (TEARDOWN_NOTE_PATH, "`platformRegistrationScaffoldSummary()`", "teardown_note:`platformRegistrationScaffoldSummary()`"),
            (TEARDOWN_NOTE_PATH, "continued-heartbeat", "teardown_note:continued-heartbeat"),
            (TEARDOWN_NOTE_PATH, "`dw_wdt_drv_shutdown`", "teardown_note:`dw_wdt_drv_shutdown`"),
            (TEARDOWN_NOTE_PATH, "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`", "teardown_note:`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`"),
            (MANIFEST_PATH, '"id": "phase11-dw-wdt-platform-resource-preflight"', 'manifest:"id": "phase11-dw-wdt-platform-resource-preflight"'),
            (MANIFEST_PATH, '"id": "phase11-dw-wdt-registration-order-scaffold"', 'manifest:"id": "phase11-dw-wdt-registration-order-scaffold"'),
            (BUILD_PATH, '.name = "phase11-dw-wdt-survey-tests"', 'build:.name = "phase11-dw-wdt-survey-tests"'),
        ]
        for rel_path, marker, expected in checks:
            write_fixture_tree(root)
            try:
                expect_failure(root, rel_path, marker, expected)
            except AssertionError as exc:
                print(str(exc), file=sys.stderr)
                return 1
        for rel_path in [SURVEY_GATE_PATH, REGISTRATION_SCAFFOLD_PATH, VERIFY_REPLAY_PATH, SCRIPT_PATH, MANIFEST_PATH, VALIDATION_MATRIX_PATH, SHARED_REPLAY_CONTRACT_PATH, TEARDOWN_NOTE_PATH, SURVEY_NOTE_PATH]:
            write_fixture_tree(root)
            try:
                expect_missing_file(root, rel_path)
            except AssertionError as exc:
                print(str(exc), file=sys.stderr)
                return 1
    print("PHASE11_DW_WDT_PACKET_SELFTEST=pass")
    print(f"PHASE11_DW_WDT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the dedicated Phase 11 DesignWare watchdog review packet.")
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
    print("PHASE11_DW_WDT_PACKET=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
