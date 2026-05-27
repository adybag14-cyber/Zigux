#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
DOC = ROOT / "Documentation" / "zigux" / "phase2-validator-coverage-gap.md"

LIVE_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "run: make -C zigux phase2",
)

LIVE_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
    "phase2: phase2-validate",
)

VALIDATOR_PRESENT_MARKERS = (
    '"scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
    '"phase2-tools:",',
    '"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
)

VALIDATOR_GAP_MARKERS = (
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "run: make -C zigux phase2",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test\",",
    "\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py\",",
)

DOC_MARKERS = (
    "# Phase 2 Validator Coverage Gap",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`",
    "`make -C zigux phase2`",
    "current `master` already ships the bootstrap-workflow guard in the workflow and the Phase 2 tools make route",
    "the validator still does not require those exact workflow or makefile markers",
    "next bounded repo-tooling step is to widen `validate-phase2.py` so the shipped bootstrap-workflow guard and aggregate `phase2` route become validator-enforced",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_lines(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    validator_text = read_text(root / VALIDATOR.relative_to(ROOT))
    doc_text = read_text(root / DOC.relative_to(ROOT))

    issues: list[tuple[str, str]] = []

    for marker in LIVE_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_LIVE_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_LIVE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in LIVE_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_LIVE_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_LIVE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in VALIDATOR_PRESENT_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_PRESENT_MARKER", marker))

    for marker in VALIDATOR_GAP_MARKERS:
        if marker in validator_text:
            issues.append(("VALIDATOR_GAP_CLOSED_OR_DRIFTED", marker))

    for marker in DOC_MARKERS:
        if marker not in doc_text:
            issues.append(("MISSING_DOC_MARKER", marker))

    return issues


def build_sample_root(root: Path) -> None:
    write_text(
        root / WORKFLOW.relative_to(ROOT),
        "\n".join(("name: zigux-bootstrap", *LIVE_WORKFLOW_LINES)) + "\n",
    )
    write_text(
        root / MAKEFILE.relative_to(ROOT),
        "\n".join(
            (
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                *LIVE_MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root / VALIDATOR.relative_to(ROOT),
        "\n".join(
            (
                "REQUIRED_PATHS = (",
                '    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
                ")",
                "REQUIRED_MAKEFILE_LINES = (",
                '    "phase2-tools:",',
                '    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
                ")",
            )
        )
        + "\n",
    )
    write_text(root / DOC.relative_to(ROOT), "\n".join(DOC_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_coverage_gap_") as tmpdir:
        root = Path(tmpdir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        workflow_path = root / WORKFLOW.relative_to(ROOT)
        makefile_path = root / MAKEFILE.relative_to(ROOT)
        validator_path = root / VALIDATOR.relative_to(ROOT)
        doc_path = root / DOC.relative_to(ROOT)

        for marker in LIVE_WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_LIVE_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8") + LIVE_WORKFLOW_LINES[0] + "\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_LIVE_WORKFLOW_LINE", f"{LIVE_WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        for marker in LIVE_MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_LIVE_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + LIVE_MAKEFILE_LINES[0] + "\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_LIVE_MAKEFILE_LINE", f"{LIVE_MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        for marker in VALIDATOR_PRESENT_MARKERS:
            build_sample_root(root)
            validator_path.write_text(
                replace_exact_line(validator_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_VALIDATOR_PRESENT_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in VALIDATOR_GAP_MARKERS:
            build_sample_root(root)
            validator_path.write_text(
                validator_path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            assert ("VALIDATOR_GAP_CLOSED_OR_DRIFTED", marker) in collect_issues(root)
            checks += 1

        for marker in DOC_MARKERS:
            build_sample_root(root)
            doc_path.write_text(
                replace_once(doc_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_DOC_MARKER", marker) in collect_issues(root)
            checks += 1

    print("PHASE2_VALIDATOR_COVERAGE_GAP_SELF_TEST=pass")
    print(f"PHASE2_VALIDATOR_COVERAGE_GAP_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 validator coverage-gap note aligned with the live workflow, Makefile, and validator surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_VALIDATOR_COVERAGE_GAP=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_VALIDATOR_COVERAGE_GAP=pass")
    print(f"PHASE2_VALIDATOR_COVERAGE_GAP_WORKFLOW_LINE_COUNT={len(LIVE_WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATOR_COVERAGE_GAP_MAKEFILE_LINE_COUNT={len(LIVE_MAKEFILE_LINES)}")
    print(f"PHASE2_VALIDATOR_COVERAGE_GAP_VALIDATOR_GAP_COUNT={len(VALIDATOR_GAP_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
