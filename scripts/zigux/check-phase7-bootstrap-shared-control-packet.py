#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control bootstrap packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[1] if len(SELF_PATH.parents) > 1 else Path.cwd()

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
SEQUENCING_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
CHECKPOINT_PATH = Path("Documentation/zigux/phase7-shared-control-review-checkpoint.md")
SURVEY_PATH = Path("Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md")
SHARED_CONTROL_GAP_PATH = Path("scripts/zigux/check-phase7-shared-control-gap.py")
SELFTEST_ALIGNMENT_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
MAKEFILE_PATH = Path("zigux/Makefile")
PARKED_PATH = Path("scripts/zigux/check-phase7-make-wrapper.py")

REQUIRED_PATHS = (
    WORKFLOW_PATH,
    SEQUENCING_PATH,
    CHECKPOINT_PATH,
    SURVEY_PATH,
    SHARED_CONTROL_GAP_PATH,
    SELFTEST_ALIGNMENT_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
)

REQUIRED_STEP_NAMES = (
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 shared-control gap packet",
    "Self-test current Phase 7 make-wrapper selftest alignment checker",
    "Check current Phase 7 make-wrapper selftest alignment packet",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: make -C zigux phase7-validate",
    "run: make -C zigux phase7-test",
    "run: python3 scripts/zigux/validate-phase7.py --self-test",
    "run: python3 scripts/zigux/validate-phase7.py",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
)

REQUIRED_SNIPPETS: dict[Path, tuple[str, ...]] = {
    SEQUENCING_PATH: (
        "- shared control-surface packet, lane `P7-Y05`:",
        "- `scripts/zigux/check-phase7-shared-control-gap.py`",
        "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "- `scripts/zigux/validate-phase7.py`",
        "the readable non-owner shared-control files in this slot are still `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase7_build.zig`",
    ),
    CHECKPOINT_PATH: (
        "# Phase 7 Shared Control Review Checkpoint",
        "`scripts/zigux/check-phase7-shared-control-gap.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "Keep `scripts/zigux/validate-phase7.py` and `phase7-validate` framed as a returned narrow validation foothold only;",
        "Keep `phase7-test` and `phase7` framed as absent wrapper-route vocabulary",
        ".github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate` and `make -C zigux phase7-test` steps.",
    ),
    SURVEY_PATH: (
        "`PHASE7_STATUS=shared_control_workspace_bootstrap_gap_survey`",
        "`PHASE7_LANE_KEY=P7-L01`",
        "scripts/zigux/validate-phase7.py` plus `make -C zigux phase7-validate` keep one returned shared validation foothold explicit on current `master`",
        ".github/workflows/zigux-bootstrap.yml` self-tests `scripts/zigux/check-phase7-shared-control-gap.py` and `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "current `master` still does not materialize `phase7-test` or `phase7` in `zigux/Makefile`",
        ".github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `zig build test --build-file zigux/tests/phase7_build.zig --summary all` steps",
    ),
    SHARED_CONTROL_GAP_PATH: (
        "REQUIRED_WORKFLOW_LINES = [",
        '"scripts/zigux/check-phase7-make-wrapper.py",',
        'print("PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass")',
        'print("PHASE7_SHARED_CONTROL_GAP=pass")',
    ),
    SELFTEST_ALIGNMENT_PATH: (
        "REQUIRED_WORKFLOW_LINES = (",
        'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")',
        'print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")',
        'print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")',
    ),
    VALIDATOR_PATH: (
        'MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")',
        'run_checker(root, MAKE_WRAPPER_SELFTEST_ALIGNMENT_CHECKER_PATH, "--root")',
        '"make -C zigux phase7-validate",',
    ),
}

REQUIRED_MAKEFILE_LINES = (
    "phase7-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py",
)

FORBIDDEN_MAKEFILE_LINES = (
    "phase7-test:",
    "phase7:",
)

SELF_TEST_CASE_COUNT = 9


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker.strip())


def require_snippets(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(root / rel_path)
        for snippet in snippets:
            count = content.count(snippet)
            if count == 0:
                raise ValidationError(f"missing expected marker in {rel_path.as_posix()}: {snippet}")
            if count != 1:
                raise ValidationError(f"duplicate expected marker in {rel_path.as_posix()}: {snippet}:count={count}")


def require_workflow(root: Path) -> None:
    text = read_text(root / WORKFLOW_PATH)
    for step_name in REQUIRED_STEP_NAMES:
        count = count_exact_lines(text, f"- name: {step_name}")
        if count == 0:
            raise ValidationError(f"missing workflow step: {step_name}")
        if count != 1:
            raise ValidationError(f"duplicate workflow step: {step_name}:count={count}")

    for line in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(text, line)
        if count == 0:
            raise ValidationError(f"missing workflow command: {line}")
        if count != 1:
            raise ValidationError(f"duplicate workflow command: {line}:count={count}")

    positions = [text.index(f"- name: {step_name}") for step_name in REQUIRED_STEP_NAMES]
    if positions != sorted(positions):
        raise ValidationError("phase7 workflow packet order drifted")

    for line in FORBIDDEN_WORKFLOW_LINES:
        if count_exact_lines(text, line):
            raise ValidationError(f"forbidden workflow line present: {line}")


def require_makefile(root: Path) -> None:
    text = read_text(root / MAKEFILE_PATH)
    for line in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(text, line)
        if count == 0:
            raise ValidationError(f"missing makefile line: {line}")
        if count != 1:
            raise ValidationError(f"duplicate makefile line: {line}:count={count}")
    for line in FORBIDDEN_MAKEFILE_LINES:
        if count_exact_lines(text, line):
            raise ValidationError(f"forbidden makefile line present: {line}")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required paths: " + ", ".join(missing))
    if (root / PARKED_PATH).exists():
        raise ValidationError(f"parked shared-control path unexpectedly returned: {PARKED_PATH.as_posix()}")
    require_workflow(root)
    require_snippets(root)
    require_makefile(root)


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 9 trace-events survey witness",
                "        run: zig test zigux/tests/runtime_trace_events_survey.zig",
                "      - name: Self-test current Phase 7 shared-control gap checker",
                "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
                "      - name: Check current Phase 7 shared-control gap packet",
                "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
                "      - name: Self-test current Phase 7 make-wrapper selftest alignment checker",
                "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
                "      - name: Check current Phase 7 make-wrapper selftest alignment packet",
                "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
                "      - name: Self-test current Phase 10 bootstrap route checker",
                "        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test",
                "",
            )
        ),
    )
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write_text(root / rel_path, "\n".join(snippets) + "\n")
    write_text(
        root / MAKEFILE_PATH,
        "phase7-validate:\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n"
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n",
    )


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r}, got {exc!s}") from exc
        return
    raise AssertionError(f"expected failure containing {expected!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase7_bootstrap_shared_control_") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        validate(root)
        cases = 0

        workflow_path = root / WORKFLOW_PATH
        original_workflow = read_text(workflow_path)

        write_text(workflow_path, original_workflow.replace(REQUIRED_WORKFLOW_LINES[0] + "\n", "", 1))
        expect_failure(root, "missing workflow command")
        cases += 1
        write_text(workflow_path, original_workflow + REQUIRED_WORKFLOW_LINES[0] + "\n")
        expect_failure(root, "duplicate workflow command")
        cases += 1
        swapped = original_workflow.replace(
            "      - name: Self-test current Phase 7 shared-control gap checker\n"
            "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test\n"
            "      - name: Check current Phase 7 shared-control gap packet\n"
            "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py\n",
            "      - name: Check current Phase 7 shared-control gap packet\n"
            "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py\n"
            "      - name: Self-test current Phase 7 shared-control gap checker\n"
            "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test\n",
            1,
        )
        write_text(workflow_path, swapped)
        expect_failure(root, "phase7 workflow packet order drifted")
        cases += 1
        write_text(workflow_path, original_workflow)

        seq_path = root / SEQUENCING_PATH
        original_seq = read_text(seq_path)
        write_text(seq_path, original_seq.replace(REQUIRED_SNIPPETS[SEQUENCING_PATH][0], "", 1))
        expect_failure(root, "missing expected marker in Documentation/zigux/phase7-helper-lane-sequencing.md")
        cases += 1
        write_text(seq_path, original_seq)

        checkpoint_path = root / CHECKPOINT_PATH
        original_checkpoint = read_text(checkpoint_path)
        write_text(checkpoint_path, original_checkpoint.replace(REQUIRED_SNIPPETS[CHECKPOINT_PATH][3], "", 1))
        expect_failure(root, "missing expected marker in Documentation/zigux/phase7-shared-control-review-checkpoint.md")
        cases += 1
        write_text(checkpoint_path, original_checkpoint)

        survey_path = root / SURVEY_PATH
        original_survey = read_text(survey_path)
        write_text(survey_path, original_survey.replace(REQUIRED_SNIPPETS[SURVEY_PATH][3], "", 1))
        expect_failure(root, "missing expected marker in Documentation/zigux/phase7-runtime-workspace-bootstrap-gap-survey.md")
        cases += 1
        write_text(survey_path, original_survey)

        validator_path = root / VALIDATOR_PATH
        original_validator = read_text(validator_path)
        write_text(validator_path, original_validator.replace(REQUIRED_SNIPPETS[VALIDATOR_PATH][1], "", 1))
        expect_failure(root, "missing expected marker in scripts/zigux/validate-phase7.py")
        cases += 1
        write_text(validator_path, original_validator)

        makefile_path = root / MAKEFILE_PATH
        original_makefile = read_text(makefile_path)
        write_text(makefile_path, original_makefile + "phase7-test:\n\t@true\n")
        expect_failure(root, "forbidden makefile line present: phase7-test:")
        cases += 1
        write_text(makefile_path, original_makefile)

        write_text(root / PARKED_PATH, "# parked path unexpectedly rematerialized\n")
        expect_failure(root, "parked shared-control path unexpectedly returned")
        cases += 1

        if cases != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, ran {cases}")

    print("PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_SELF_TEST=pass")
    print(f"PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    try:
        validate(args.root)
    except ValidationError as exc:
        print(f"PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET=fail: {exc}")
        return 1

    print("PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET=pass")
    print(f"PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_WORKFLOW_STEP_COUNT={len(REQUIRED_STEP_NAMES)}")
    print(f"PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(
        "PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
