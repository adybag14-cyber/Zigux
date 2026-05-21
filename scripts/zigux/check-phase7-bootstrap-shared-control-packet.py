#!/usr/bin/env python3
"""Guard the current Phase 7 shared-control bootstrap packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
SEQUENCING_PATH = Path("Documentation/zigux/phase7-helper-lane-sequencing.md")
CHECKPOINT_PATH = Path("Documentation/zigux/phase7-shared-control-review-checkpoint.md")
DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SAMPLES_README_PATH = Path("samples/zigux/README.md")
BUILD_WIRING_PATH = Path("scripts/zigux/check-phase7-build-wiring.py")
SHARED_CONTROL_GAP_PATH = Path("scripts/zigux/check-phase7-shared-control-gap.py")
SELFTEST_ALIGNMENT_PATH = Path("scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase7.py")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_PATHS = [
    WORKFLOW_PATH,
    SEQUENCING_PATH,
    CHECKPOINT_PATH,
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SAMPLES_README_PATH,
    BUILD_WIRING_PATH,
    SHARED_CONTROL_GAP_PATH,
    SELFTEST_ALIGNMENT_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
]

REQUIRED_STEP_NAMES = [
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 shared-control gap packet",
    "Self-test current Phase 7 make-wrapper selftest alignment checker",
    "Check current Phase 7 make-wrapper selftest alignment packet",
]

REQUIRED_WORKFLOW_LINES = [
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test",
    "run: python3 scripts/zigux/check-phase7-shared-control-gap.py",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py",
]

REQUIRED_SNIPPETS: dict[Path, list[str]] = {
    SEQUENCING_PATH: [
        "- shared control-surface packet, lane `P7-Y05`:",
        "- `scripts/zigux/check-phase7-shared-control-gap.py`",
        "- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "- `scripts/zigux/validate-phase7.py`",
        "the workflow carries the current `check-phase7-shared-control-gap.py` and `check-phase7-make-wrapper-selftest-alignment.py` self-test hooks",
    ],
    CHECKPOINT_PATH: [
        "# Phase 7 Shared Control Review Checkpoint",
        "`scripts/zigux/check-phase7-shared-control-gap.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "Keep `scripts/zigux/validate-phase7.py` and `phase7-validate` framed as a returned narrow validation foothold only;",
        "Keep `phase7-test` and `phase7` framed as absent wrapper-route vocabulary",
    ],
    DOCS_README_PATH: [
        "Phase 7 notes",
        "`scripts/zigux/check-phase7-shared-control-gap.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "`scripts/zigux/validate-phase7.py`",
    ],
    SCRIPTS_README_PATH: [
        "## Phase 7",
        "`scripts/zigux/check-phase7-shared-control-gap.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "`scripts/zigux/validate-phase7.py`",
        "`make -C zigux phase7-validate`",
    ],
    TESTS_README_PATH: [
        "## Phase 7",
        "`scripts/zigux/check-phase7-shared-control-gap.py`",
        "`scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`",
        "`scripts/zigux/validate-phase7.py`",
        "`make -C zigux phase7-validate`",
    ],
    SAMPLES_README_PATH: [
        "samples/zigux/README.md",
        "Phase 9 runtime pilot family",
    ],
    BUILD_WIRING_PATH: [
        "check-phase7-build-wiring.py",
        "phase7-validate",
    ],
    SHARED_CONTROL_GAP_PATH: [
        "REQUIRED_WORKFLOW_LINES = [",
        'print("PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass")',
        'print("PHASE7_SHARED_CONTROL_GAP=pass")',
    ],
    SELFTEST_ALIGNMENT_PATH: [
        "REQUIRED_WORKFLOW_LINES = (",
        'print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")',
        'print("PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass")',
    ],
    VALIDATOR_PATH: [
        "EXPECTED_PACKET = \"phase7-leaf-library-evidence\"",
        "\"python3 scripts/zigux/validate-phase7.py --self-test\",",
        "\"python3 scripts/zigux/validate-phase7.py\",",
        "\"make -C zigux phase7-validate\",",
    ],
    MAKEFILE_PATH: [
        "phase7-validate:",
        "scripts/zigux/validate-phase7.py --self-test",
        "scripts/zigux/validate-phase7.py",
    ],
}

SELF_TEST_CASE_COUNT = 7


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(f"missing expected marker in {rel_path.as_posix()}: {snippet}")


def count_exact_lines(text: str, marker: str) -> int:
    normalized = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == normalized)


def require_workflow_packet(root: Path) -> None:
    workflow_text = read_text(root / WORKFLOW_PATH)

    for marker in REQUIRED_STEP_NAMES:
        count = count_exact_lines(workflow_text, f"- name: {marker}")
        if count == 0:
            raise ValidationError(f"missing workflow step: {marker}")
        if count != 1:
            raise ValidationError(f"duplicate workflow step: {marker}")

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            raise ValidationError(f"missing workflow command: {marker}")
        if count != 1:
            raise ValidationError(f"duplicate workflow command: {marker}")

    positions = [workflow_text.index(f"- name: {marker}") for marker in REQUIRED_STEP_NAMES]
    if positions != sorted(positions):
        raise ValidationError("phase7 workflow packet order drifted")

    start = positions[0]
    end = workflow_text.index(f"- name: {REQUIRED_STEP_NAMES[-1]}", positions[-1]) + len(REQUIRED_STEP_NAMES[-1])
    packet_slice = workflow_text[start:end]
    if "- name: Self-test current Phase 10 bootstrap route checker" in packet_slice:
        raise ValidationError("phase10 step intruded into phase7 workflow packet")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required paths: " + ", ".join(missing))
    require_workflow_packet(root)
    require_snippets(root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write(
        root / WORKFLOW_PATH,
        "\n".join(
            [
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
            ]
        ),
    )
    write(
        root / SEQUENCING_PATH,
        "\n".join(REQUIRED_SNIPPETS[SEQUENCING_PATH]) + "\n",
    )
    write(
        root / CHECKPOINT_PATH,
        "\n".join(REQUIRED_SNIPPETS[CHECKPOINT_PATH]) + "\n",
    )
    write(
        root / DOCS_README_PATH,
        "# Zigux Documentation\nPhase 7 notes\n- `scripts/zigux/check-phase7-shared-control-gap.py`\n- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`\n- `scripts/zigux/validate-phase7.py`\n",
    )
    write(
        root / SCRIPTS_README_PATH,
        "# scripts/zigux\n\n## Phase 7\n- `scripts/zigux/check-phase7-shared-control-gap.py`\n- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`\n- `scripts/zigux/validate-phase7.py`\n- `make -C zigux phase7-validate`\n",
    )
    write(
        root / TESTS_README_PATH,
        "# zigux/tests\n\n## Phase 7\n- `scripts/zigux/check-phase7-shared-control-gap.py`\n- `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`\n- `scripts/zigux/validate-phase7.py`\n- `make -C zigux phase7-validate`\n",
    )
    write(
        root / SAMPLES_README_PATH,
        "# samples/zigux\n\n- samples/zigux/README.md\n- Phase 9 runtime pilot family\n",
    )
    write(
        root / BUILD_WIRING_PATH,
        "# phase7 build wiring\ncheck-phase7-build-wiring.py\nphase7-validate\n",
    )
    write(
        root / SHARED_CONTROL_GAP_PATH,
        "REQUIRED_WORKFLOW_LINES = [\n]\nprint(\"PHASE7_SHARED_CONTROL_GAP_SELF_TEST=pass\")\nprint(\"PHASE7_SHARED_CONTROL_GAP=pass\")\n",
    )
    write(
        root / SELFTEST_ALIGNMENT_PATH,
        "REQUIRED_WORKFLOW_LINES = (\n)\nprint(\"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT_SELF_TEST=pass\")\nprint(\"PHASE7_MAKE_WRAPPER_SELFTEST_ALIGNMENT=pass\")\n",
    )
    write(
        root / VALIDATOR_PATH,
        "\n".join(REQUIRED_SNIPPETS[VALIDATOR_PATH]) + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "phase7-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py\n",
    )


def expect_failure(root: Path) -> None:
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="phase7_bootstrap_shared_control_") as tmpdir:
        base = Path(tmpdir)
        write_sample_root(base)
        validate(base)

        case_root = base / "case_missing_workflow_command"
        write_sample_root(case_root)
        write(case_root / WORKFLOW_PATH, read_text(case_root / WORKFLOW_PATH).replace(REQUIRED_WORKFLOW_LINES[0] + "\n", "", 1))
        expect_failure(case_root)
        cases_run += 1

        case_root = base / "case_reordered_workflow_step"
        write_sample_root(case_root)
        workflow_text = read_text(case_root / WORKFLOW_PATH)
        old = (
            "      - name: Self-test current Phase 7 shared-control gap checker\n"
            "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test\n"
        )
        new = (
            "      - name: Self-test current Phase 7 make-wrapper selftest alignment checker\n"
            "        run: python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py --self-test\n"
        )
        workflow_text = workflow_text.replace(old, "__TMP__", 1).replace(new, old, 1).replace("__TMP__", new, 1)
        write(case_root / WORKFLOW_PATH, workflow_text)
        expect_failure(case_root)
        cases_run += 1

        case_root = base / "case_duplicate_workflow_step"
        write_sample_root(case_root)
        write(case_root / WORKFLOW_PATH, read_text(case_root / WORKFLOW_PATH) + "      - name: Check current Phase 7 shared-control gap packet\n")
        expect_failure(case_root)
        cases_run += 1

        case_root = base / "case_missing_sequencing_marker"
        write_sample_root(case_root)
        write(case_root / SEQUENCING_PATH, read_text(case_root / SEQUENCING_PATH).replace(REQUIRED_SNIPPETS[SEQUENCING_PATH][0], "", 1))
        expect_failure(case_root)
        cases_run += 1

        case_root = base / "case_missing_makefile_marker"
        write_sample_root(case_root)
        write(case_root / MAKEFILE_PATH, read_text(case_root / MAKEFILE_PATH).replace("phase7-validate:\n", "", 1))
        expect_failure(case_root)
        cases_run += 1

        case_root = base / "case_missing_validator_file"
        write_sample_root(case_root)
        (case_root / VALIDATOR_PATH).unlink()
        expect_failure(case_root)
        cases_run += 1

        case_root = base / "case_phase10_intrusion"
        write_sample_root(case_root)
        intrude = "      - name: Self-test current Phase 10 bootstrap route checker\n"
        write(case_root / WORKFLOW_PATH, read_text(case_root / WORKFLOW_PATH).replace(intrude, "      - name: Self-test current Phase 10 bootstrap route checker\n" "        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test\n" "      - name: Check current Phase 7 shared-control gap packet\n", 1))
        expect_failure(case_root)
        cases_run += 1

    if cases_run != SELF_TEST_CASE_COUNT:
        raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, ran {cases_run}")

    print("PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_SELF_TEST=pass")
    print(f"PHASE7_BOOTSTRAP_SHARED_CONTROL_PACKET_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
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
