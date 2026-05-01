#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parent

MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"

MAKEFILE_MARKERS = [
    "phase9-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py\n",
    "phase9: phase9-validate phase9-test",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 9 runtime validator",
    "Validate Phase 9 runtime gates",
    "make -C zigux phase9-validate",
    "Run Phase 9 runtime helper tests",
    "zigux/tests/phase9_build.zig",
]

SURVEY_MARKERS = [
    "- `python3 scripts/zigux/validate-phase9.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`\n",
    "- `python3 scripts/zigux/validate-phase9.py`\n",
    "- `python3 scripts/zigux/check-phase9-validation-flow.py`\n",
    "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
    "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`\n",
    "- `make -C zigux phase9-validate`\n",
    "- `make -C zigux phase9`\n",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    survey = read_text(root, SURVEY_PATH)

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")
    for marker in SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)

    (root / MAKEFILE_PATH).write_text(
        "\n".join(
            [
                "PHONY += phase9-validate phase9-test phase9",
                "",
                "phase9-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py",
                "",
                "phase9-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig --summary all",
                "",
                "phase9: phase9-validate phase9-test",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / WORKFLOW_PATH).write_text(
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 9 runtime validator",
                "        run: python3 scripts/zigux/validate-phase9.py --self-test",
                "      - name: Validate Phase 9 runtime gates",
                "        run: make -C zigux phase9-validate",
                "      - name: Run Phase 9 runtime helper tests",
                "        run: zig build test --build-file zigux/tests/phase9_build.zig --summary all",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Loader Gap Survey",
                "",
                "## Gates",
                "",
                "1. run the validator self-test first",
                "- `python3 scripts/zigux/validate-phase9.py --self-test`",
                "",
                "2. run the shared Phase 9 validation-flow self-test and the dedicated runtime-loader packet self-tests",
                "- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`",
                "",
                "3. run the release-discipline validator and the dedicated runtime-loader packet checks",
                "- `python3 scripts/zigux/validate-phase9.py`",
                "- `python3 scripts/zigux/check-phase9-validation-flow.py`",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`",
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`",
                "",
                "4. run the shared Phase 9 runtime survey bundle",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "",
                "5. run the convenience targets",
                "- `make -C zigux phase9-validate`",
                "- `make -C zigux phase9`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    failures = validate(root)
    if expected_marker not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(
            f"phase9-validation-flow-selftest:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_validation_flow_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline_failures = validate(tmp_root)
        if baseline_failures:
            raise SystemExit(
                "phase9-validation-flow-selftest:baseline_failed:"
                + ",".join(baseline_failures)
            )

        makefile_path = tmp_root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_flow_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_loader_commit_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        workflow_path = tmp_root / WORKFLOW_PATH
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Validate Phase 9 runtime gates\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_phase9_validate_step",
            tmp_root,
            "workflow:Validate Phase 9 runtime gates",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_non_owner_self_test_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`\n",
        )

    print("PHASE9_VALIDATION_FLOW_SELF_TEST=pass")
    print("PHASE9_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 9 validation-flow review surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in fixture-based self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_VALIDATION_FLOW=fail")
        print("PHASE9_VALIDATION_FLOW_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_VALIDATION_FLOW_FAILURES_END")
        return 1

    print("PHASE9_VALIDATION_FLOW=pass")
    print(f"PHASE9_VALIDATION_FLOW_MARKER_COUNT={len(MAKEFILE_MARKERS) + len(WORKFLOW_MARKERS) + len(SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
