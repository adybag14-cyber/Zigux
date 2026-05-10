#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SCRIPT_PATH = "scripts/zigux/check-phase11-shared-replay-contract.py"
NOTE_PATH = "Documentation/zigux/phase11-shared-replay-contract.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"

REQUIRED_NOTE_MARKERS = (
    "# Phase 11 Shared Replay Contract",
    "* `scripts/zigux/check-phase11-shared-replay-contract.py`",
    "The shipped gpio watchdog sub-packet inside that shared route stays explicit as `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`.",
    "The shipped bcm2835 watchdog sub-packet inside that shared route stays explicit as `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`.",
    "The shipped DesignWare watchdog sub-packet inside that shared route stays explicit as `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`.",
    "* gpio watchdog: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`",
    "* bcm2835 watchdog: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`",
    "* DesignWare watchdog: `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and the shared `phase11-dw-wdt-registration-scaffold-tests` plus `phase11-dw-wdt-verify-tests` replay artifacts",
    "The dedicated archival HVC evidence still stays explicit beside that shared route:",
    "* there is no shared `make -C zigux phase11-validate` target on `master`",
)

REQUIRED_DOCS_README_MARKERS = (
    "Phase 11 notes - `Documentation/zigux/phase11-bcm2835-wdt-slice.md`",
    "`Documentation/zigux/phase11-shared-replay-contract.md` now records that same shared contributor packet",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "- `check-phase11-shared-replay-contract.py`",
    "- `check-phase11-bcm2835-wdt-packet.py`",
    "- `check-phase11-dw-wdt-packet.py`",
    "- `check-phase11-header-boundary-packet.py`",
    "- `check-phase11-hvc-survey-packet.py`",
    "Phase 11 flow",
    "- `Documentation/zigux/README.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`Documentation/zigux/phase11-closure-note.md`",
)

REQUIRED_TESTS_README_MARKERS = (
    "keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too:",
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey`",
    "the dedicated bcm2835 archival checker route",
    "the dedicated DesignWare packet checker",
    "the dedicated bcm2835, gpio, and DesignWare manifest-backed survey checkpoints",
    "the dedicated gpio teardown companion",
    "the dedicated DesignWare teardown companion",
    "the dedicated `hvc_console` survey note, teardown note, and checker-backed `make -C zigux phase11-hvc-survey` replay",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`scripts/zigux/check-phase11-dw-wdt-packet.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
)

REQUIRED_FILES = (
    SCRIPT_PATH,
    NOTE_PATH,
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    REVIEW_CHECKLIST_PATH,
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    checks = (
        ("phase11-note", NOTE_PATH, REQUIRED_NOTE_MARKERS),
        ("docs-readme", DOCS_README_PATH, REQUIRED_DOCS_README_MARKERS),
        ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS),
        ("tests-readme", TESTS_README_PATH, REQUIRED_TESTS_README_MARKERS),
        ("review-checklist", REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS),
    )
    for label, rel_path, markers in checks:
        source = read_text(root, rel_path)
        for marker in markers:
            if marker not in source:
                problems.append(f"missing-marker:{label}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_missing_case(root: Path, label: str, rel_path: str, needle: str) -> None:
    text = read_text(root, rel_path)
    if needle not in text:
        raise SystemExit(f"self-test-fixture-missing:{label}")
    (root / rel_path).write_text(text.replace(needle, "", 1), encoding="utf-8")
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{label}")
    expected = f"missing-marker:{label}:{needle}"
    actual = result.stdout.strip() or result.stderr.strip() or "no_output"
    if expected not in actual:
        raise SystemExit(f"self-test-mismatch:{label}:{actual}")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    write_text(root, NOTE_PATH, "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    write_text(root, DOCS_README_PATH, "\n".join(REQUIRED_DOCS_README_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, TESTS_README_PATH, "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(
        root,
        REVIEW_CHECKLIST_PATH,
        "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n",
    )


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_shared_contract_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            ("phase11-note", NOTE_PATH, REQUIRED_NOTE_MARKERS[1]),
            ("phase11-note", NOTE_PATH, REQUIRED_NOTE_MARKERS[5]),
            ("docs-readme", DOCS_README_PATH, REQUIRED_DOCS_README_MARKERS[1]),
            ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS[7]),
            ("scripts-readme", SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_MARKERS[11]),
            ("tests-readme", TESTS_README_PATH, REQUIRED_TESTS_README_MARKERS[7]),
            ("review-checklist", REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS[0]),
        )
        for label, rel_path, needle in mutations:
            case_root = Path(tmp) / f"{label}_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, label, rel_path, needle)
            cases += 1

    print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
    print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE11_SHARED_REPLAY_CONTRACT=fail")
        print("PHASE11_SHARED_REPLAY_CONTRACT_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE11_SHARED_REPLAY_CONTRACT_PROBLEMS_END")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    print(f"PHASE11_SHARED_REPLAY_CONTRACT_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
