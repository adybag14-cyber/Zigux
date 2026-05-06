#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

SURVEY_NOTE_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
BUILD_PATH = "zigux/tests/phase11_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SCRIPT_PATH = "scripts/zigux/check-phase11-hvc-survey-packet.py"

REQUIRED_SURVEY_NOTE_MARKERS = [
    "lane `P11-L16`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
]

REQUIRED_VALIDATION_MATRIX_MARKERS = [
    "lane: `P11-L16`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`zigux/tests/phase11_build.zig`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`make -C zigux phase11-hvc-survey`",
]

REQUIRED_BUILD_MARKERS = [
    '.name = "phase11-hvc-console-survey-tests"',
    'const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");',
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
    "phase11-hvc-survey:",
    "$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
    "$(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
]

REQUIRED_WORKFLOW_MARKERS = [
    "Run dedicated Phase 11 hvc survey replay",
    "make -C zigux phase11-hvc-survey",
]

SELF_TEST_CASE_COUNT = 5


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
        BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
        SCRIPT_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    survey_note = read_text(root, SURVEY_NOTE_PATH)
    validation_matrix = read_text(root, VALIDATION_MATRIX_PATH)
    build_file = read_text(root, BUILD_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

    for marker in REQUIRED_SURVEY_NOTE_MARKERS:
        if marker not in survey_note:
            failures.append(f"survey_note:{marker}")
    for marker in REQUIRED_VALIDATION_MATRIX_MARKERS:
        if marker not in validation_matrix:
            failures.append(f"validation_matrix:{marker}")
    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in build_file:
            failures.append(f"build:{marker}")
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / SURVEY_NOTE_PATH,
        """# Phase 11 HVC Console Survey

The live archival packet now belongs to lane `P11-L16`.

- `zigux/tests/phase11_hvc_console_survey.zig` now keeps a bounded driver-local layout checkpoint
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md` names the current shared gate
- `scripts/zigux/check-phase11-hvc-survey-packet.py` keeps the dedicated archival survey note, validation matrix, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the same delivery route
- `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` keep those HVC review surfaces coupled to the wider Phase 11 replay route
""",
    )
    write_text(
        root / VALIDATION_MATRIX_PATH,
        """# Phase 11 HVC Console Validation Matrix

- lane: `P11-L16`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_build.zig`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- keep `zigux/tests/phase11_build.zig` as the shared replay path for the current starter while the dedicated archival `make -C zigux phase11-hvc-survey` bootstrap replay remains the only extra CI step for the separate survey route
""",
    )
    write_text(
        root / BUILD_PATH,
        """const phase11_hvc_console_survey_tests = b.addTest(.{
    .name = "phase11-hvc-console-survey-tests",
});

const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");
hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);
""",
    )
    write_text(
        root / MAKEFILE_PATH,
        """PHONY += phase11-contract phase11-test phase11-hvc-survey phase11

phase11-hvc-survey:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py
	cd $(ZIGUX_ROOT) && $(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all
""",
    )
    write_text(
        root / WORKFLOW_PATH,
        """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Run dedicated Phase 11 hvc survey replay
        run: make -C zigux phase11-hvc-survey
""",
    )
    write_text(
        root / SCRIPT_PATH,
        """#!/usr/bin/env python3
print(\"synthetic survey packet checker\")
""",
    )


def expect_failure(root: Path, rel_path: str, marker: str, expected_failure: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11_hvc_survey_", dir=None) as tmpdir:
        root = Path(tmpdir)

        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        write_fixture_tree(root)
        try:
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "survey_note:`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
            )
            expect_failure(
                root,
                SURVEY_NOTE_PATH,
                "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
                "survey_note:`scripts/zigux/check-phase11-hvc-survey-packet.py`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`make -C zigux phase11-hvc-survey`",
                "validation_matrix:`make -C zigux phase11-hvc-survey`",
            )
            expect_failure(
                root,
                VALIDATION_MATRIX_PATH,
                "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
                "validation_matrix:`scripts/zigux/check-phase11-hvc-survey-packet.py`",
            )
            expect_failure(
                root,
                MAKEFILE_PATH,
                "$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
                "makefile:$(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
            )
        except AssertionError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    print("PHASE11_HVC_SURVEY_PACKET_SELFTEST=pass")
    print(f"PHASE11_HVC_SURVEY_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the dedicated Phase 11 hvc survey packet stays aligned."
    )
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

    print("PHASE11_HVC_SURVEY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
