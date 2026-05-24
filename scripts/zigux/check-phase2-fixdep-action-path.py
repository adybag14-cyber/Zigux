#!/usr/bin/env python3
"""Guard the current Phase 2 fixdep action path."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_README = Path("Documentation/zigux/README.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MAKEFILE = Path("zigux/Makefile")
FIXDEP_CASES = Path("zigux/tests/fixtures/fixdep/cases.json")

REQUIRED_FILES = (
    WORKFLOW,
    DOCS_README,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    FIXDEP_CASES,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-fixdep",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_DOCS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`make -C zigux phase2-fixdep`",
)

REQUIRED_PHASE2_PHONY_TARGETS = (
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
)

EXPECTED_CASE_NAMES = (
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_continuation",
    "sample_double_backslash_comment",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def exact_line_index(text: str, marker: str) -> int | None:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return None


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def parse_phase2_phony_targets(text: str) -> list[str] | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            return stripped.split(":", 1)[1].strip().split()
    return None


def collect_marker_issues(
    issues: list[tuple[str, str]], text: str, code: str, markers: tuple[str, ...]
) -> None:
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))


def collect_case_issues(issues: list[tuple[str, str]], cases: object) -> None:
    if not isinstance(cases, list):
        issues.append(("INVALID_FIXDEP_CASES_JSON", "root"))
        return
    names: list[str] = []
    for index, item in enumerate(cases):
        if not isinstance(item, dict):
            issues.append(("INVALID_FIXDEP_CASE_ENTRY", f"index={index}"))
            continue
        name = item.get("name")
        if not isinstance(name, str):
            issues.append(("INVALID_FIXDEP_CASE_NAME", f"index={index}"))
            continue
        names.append(name)
    if names != list(EXPECTED_CASE_NAMES):
        issues.append(("FIXDEP_CASE_ORDER_MISMATCH", f"actual={names!r}"))
    for name in EXPECTED_CASE_NAMES:
        if name not in names:
            issues.append(("MISSING_FIXDEP_CASE", name))
    seen: set[str] = set()
    for name in names:
        if name in seen:
            issues.append(("DUPLICATE_FIXDEP_CASE", name))
        seen.add(name)
        if name not in EXPECTED_CASE_NAMES:
            issues.append(("UNEXPECTED_FIXDEP_CASE", name))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    docs_readme_text = read_text(resolve(root, DOCS_README))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE))
    review_text = read_text(resolve(root, REVIEW_CHECKLIST))
    scripts_text = read_text(resolve(root, SCRIPTS_README))
    tests_text = read_text(resolve(root, TESTS_README))
    makefile_text = read_text(resolve(root, MAKEFILE))
    cases = read_json(resolve(root, FIXDEP_CASES))

    workflow_indices: list[int] = []
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        workflow_indices.append(exact_line_index(workflow_text, marker) or 0)
    if len(workflow_indices) == len(REQUIRED_WORKFLOW_LINES) and workflow_indices != sorted(
        workflow_indices
    ):
        issues.append(("WORKFLOW_ORDER_MISMATCH", "phase2-fixdep-route-order"))

    makefile_indices: list[int] = []
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
            continue
        makefile_indices.append(exact_line_index(makefile_text, marker) or 0)
    if len(makefile_indices) == len(REQUIRED_MAKEFILE_LINES) and makefile_indices != sorted(
        makefile_indices
    ):
        issues.append(("MAKEFILE_ORDER_MISMATCH", "phase2-fixdep-route-order"))

    phony_targets = parse_phase2_phony_targets(makefile_text)
    if phony_targets is None:
        issues.append(("MISSING_PHASE2_PHONY", ".PHONY"))
    else:
        for target in REQUIRED_PHASE2_PHONY_TARGETS:
            if target not in phony_targets:
                issues.append(("MISSING_PHASE2_PHONY_TARGET", target))

    collect_marker_issues(
        issues, docs_readme_text, "MISSING_DOCS_README_MARKER", REQUIRED_DOCS_README_MARKERS
    )
    collect_marker_issues(
        issues, closure_text, "MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS
    )
    collect_marker_issues(
        issues, review_text, "MISSING_REVIEW_MARKER", REQUIRED_REVIEW_MARKERS
    )
    collect_marker_issues(
        issues, scripts_text, "MISSING_SCRIPTS_README_MARKER", REQUIRED_SCRIPTS_README_MARKERS
    )
    collect_marker_issues(
        issues, tests_text, "MISSING_TESTS_README_MARKER", REQUIRED_TESTS_README_MARKERS
    )

    collect_case_issues(issues, cases)
    return issues


def expected_file_texts() -> dict[Path, str]:
    workflow_lines = "\n".join(
        (
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Self-test current Phase 2 fixdep gate checker",
            f"        {REQUIRED_WORKFLOW_LINES[0]}",
            "      - name: Check current Phase 2 fixdep gate packet",
            f"        {REQUIRED_WORKFLOW_LINES[1]}",
            "      - name: Self-test current fixdep parity checker",
            f"        {REQUIRED_WORKFLOW_LINES[2]}",
            "      - name: Check current fixdep parity packet",
            f"        {REQUIRED_WORKFLOW_LINES[3]}",
            "      - name: Run current Phase 2 fixdep unit tests",
            f"        {REQUIRED_WORKFLOW_LINES[4]}",
            "      - name: Run current Phase 2 fixdep wrapper route",
            f"        {REQUIRED_WORKFLOW_LINES[5]}",
            "",
        )
    )
    docs_readme = "\n".join(
        (
            "# Zigux Documentation",
            "Current Phase 2 fixdep packet:",
            "- `scripts/zigux/check-phase2-fixdep-gate.py`",
            "- `scripts/zigux/check-fixdep-diff.py`",
            "- `scripts/zigux/fixdep.zig`",
            "- `zigux/tests/fixtures/fixdep/cases.json`",
            "- `make -C zigux phase2-fixdep`",
            "",
        )
    )
    closure = "\n".join(
        (
            "# Phase 2 Closure",
            "The current fixdep packet remains directly reviewable through:",
            "- `scripts/zigux/check-phase2-fixdep-gate.py`",
            "- `scripts/zigux/check-fixdep-diff.py`",
            "- `scripts/zigux/fixdep.zig`",
            "- `zigux/tests/fixtures/fixdep/cases.json`",
            "- `make -C zigux phase2-fixdep`",
            "",
        )
    )
    review = "\n".join(
        (
            "# Zigux Review Checklist",
            "If the change touches the shared Phase 2 toolchain packet, keep:",
            "- `scripts/zigux/check-phase2-fixdep-gate.py`",
            "- `scripts/zigux/check-fixdep-diff.py`",
            "- `scripts/zigux/fixdep.zig`",
            "- `zigux/tests/fixtures/fixdep/cases.json`",
            "- `make -C zigux phase2-fixdep`",
            "",
        )
    )
    scripts_readme = "\n".join(
        (
            "# scripts/zigux",
            "Current Phase 2 fixdep packet:",
            "- `scripts/zigux/check-phase2-fixdep-gate.py`",
            "- `scripts/zigux/check-fixdep-diff.py`",
            "- `scripts/zigux/fixdep.zig`",
            "- `zigux/tests/fixtures/fixdep/cases.json`",
            "- `make -C zigux phase2-fixdep`",
            "",
        )
    )
    tests_readme = "\n".join(
        (
            "# zigux/tests",
            "Current Phase 2 fixdep packet:",
            "- `scripts/zigux/check-phase2-fixdep-gate.py`",
            "- `scripts/zigux/check-fixdep-diff.py`",
            "- `scripts/zigux/fixdep.zig`",
            "- `zigux/tests/fixtures/fixdep/cases.json`",
            "- `make -C zigux phase2-fixdep`",
            "",
        )
    )
    makefile = "\n".join(
        (
            ".PHONY: phase2-fixdep phase2-validate phase2",
            REQUIRED_MAKEFILE_LINES[0],
            f"\t{REQUIRED_MAKEFILE_LINES[1]}",
            f"\t{REQUIRED_MAKEFILE_LINES[2]}",
            f"\t{REQUIRED_MAKEFILE_LINES[3]}",
            f"\t{REQUIRED_MAKEFILE_LINES[4]}",
            f"\t{REQUIRED_MAKEFILE_LINES[5]}",
            "",
            REQUIRED_MAKEFILE_LINES[6],
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
            "",
        )
    )
    cases = json.dumps([{"name": name} for name in EXPECTED_CASE_NAMES], indent=2) + "\n"
    return {
        WORKFLOW: workflow_lines,
        DOCS_README: docs_readme,
        PHASE2_CLOSURE: closure,
        REVIEW_CHECKLIST: review,
        SCRIPTS_README: scripts_readme,
        TESTS_README: tests_readme,
        MAKEFILE: makefile,
        FIXDEP_CASES: cases,
    }


def write_sample_root(root: Path) -> None:
    for rel, content in expected_file_texts().items():
        write_text(resolve(root, rel), content)


def run_self_test() -> None:
    cases_run = 0
    with tempfile.TemporaryDirectory(prefix="lane18_fixdep_action_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        issues = collect_issues(root)
        if issues:
            raise SystemExit(f"self-test sample root failed: {issues}")
        cases_run += 1

        workflow_path = resolve(root, WORKFLOW)
        original = read_text(workflow_path)
        write_text(workflow_path, replace_exact_line(original, REQUIRED_WORKFLOW_LINES[0]))
        issues = collect_issues(root)
        if ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) not in issues:
            raise SystemExit(f"expected missing workflow issue, got {issues}")
        cases_run += 1
        write_text(workflow_path, original)

        write_text(workflow_path, duplicate_exact_line(original, REQUIRED_WORKFLOW_LINES[1]))
        issues = collect_issues(root)
        expected = ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2")
        if expected not in issues:
            raise SystemExit(f"expected duplicate workflow issue, got {issues}")
        cases_run += 1
        write_text(workflow_path, original)

        makefile_path = resolve(root, MAKEFILE)
        original = read_text(makefile_path)
        write_text(makefile_path, replace_exact_line(original, REQUIRED_MAKEFILE_LINES[0]))
        issues = collect_issues(root)
        if ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) not in issues:
            raise SystemExit(f"expected missing makefile issue, got {issues}")
        cases_run += 1
        write_text(makefile_path, original)

        write_text(makefile_path, duplicate_exact_line(original, REQUIRED_MAKEFILE_LINES[1]))
        issues = collect_issues(root)
        expected = ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2")
        if expected not in issues:
            raise SystemExit(f"expected duplicate makefile issue, got {issues}")
        cases_run += 1
        write_text(makefile_path, original)

        for target in REQUIRED_PHASE2_PHONY_TARGETS:
            lines = original.splitlines()
            phony_tokens = lines[0].split(":", 1)[1].strip().split()
            phony_tokens.remove(target)
            lines[0] = ".PHONY: " + " ".join(phony_tokens)
            write_text(makefile_path, "\n".join(lines) + "\n")
            issues = collect_issues(root)
            if ("MISSING_PHASE2_PHONY_TARGET", target) not in issues:
                raise SystemExit(f"expected missing phony target issue, got {issues}")
            cases_run += 1
            write_text(makefile_path, original)

        docs_path = resolve(root, DOCS_README)
        original = read_text(docs_path)
        write_text(docs_path, replace_once(original, REQUIRED_DOCS_README_MARKERS[0]))
        issues = collect_issues(root)
        if ("MISSING_DOCS_README_MARKER", REQUIRED_DOCS_README_MARKERS[0]) not in issues:
            raise SystemExit(f"expected docs marker issue, got {issues}")
        cases_run += 1
        write_text(docs_path, original)

        closure_path = resolve(root, PHASE2_CLOSURE)
        original = read_text(closure_path)
        write_text(closure_path, replace_once(original, REQUIRED_CLOSURE_MARKERS[1]))
        issues = collect_issues(root)
        if ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[1]) not in issues:
            raise SystemExit(f"expected closure marker issue, got {issues}")
        cases_run += 1
        write_text(closure_path, original)

        review_path = resolve(root, REVIEW_CHECKLIST)
        original = read_text(review_path)
        write_text(review_path, replace_once(original, REQUIRED_REVIEW_MARKERS[2]))
        issues = collect_issues(root)
        if ("MISSING_REVIEW_MARKER", REQUIRED_REVIEW_MARKERS[2]) not in issues:
            raise SystemExit(f"expected review marker issue, got {issues}")
        cases_run += 1
        write_text(review_path, original)

        scripts_path = resolve(root, SCRIPTS_README)
        original = read_text(scripts_path)
        write_text(scripts_path, replace_once(original, REQUIRED_SCRIPTS_README_MARKERS[3]))
        issues = collect_issues(root)
        if ("MISSING_SCRIPTS_README_MARKER", REQUIRED_SCRIPTS_README_MARKERS[3]) not in issues:
            raise SystemExit(f"expected scripts marker issue, got {issues}")
        cases_run += 1
        write_text(scripts_path, original)

        tests_path = resolve(root, TESTS_README)
        original = read_text(tests_path)
        write_text(tests_path, replace_once(original, REQUIRED_TESTS_README_MARKERS[4]))
        issues = collect_issues(root)
        if ("MISSING_TESTS_README_MARKER", REQUIRED_TESTS_README_MARKERS[4]) not in issues:
            raise SystemExit(f"expected tests marker issue, got {issues}")
        cases_run += 1
        write_text(tests_path, original)

        cases_path = resolve(root, FIXDEP_CASES)
        original = read_text(cases_path)
        write_text(cases_path, json.dumps([{"name": "sample"}], indent=2) + "\n")
        issues = collect_issues(root)
        if ("FIXDEP_CASE_ORDER_MISMATCH", "actual=['sample']") not in issues:
            raise SystemExit(f"expected fixdep case order issue, got {issues}")
        if ("MISSING_FIXDEP_CASE", EXPECTED_CASE_NAMES[-1]) not in issues:
            raise SystemExit(f"expected missing fixdep case issue, got {issues}")
        cases_run += 1
        write_text(cases_path, original)

    print("PHASE2_FIXDEP_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_ACTION_PATH_SELF_TEST_CASE_COUNT={cases_run}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_FIXDEP_ACTION_PATH_SAMPLE_ROOT={args.write_sample_root}")
        return

    if args.self_test:
        run_self_test()
        return

    issues = collect_issues(args.root)
    if issues:
        for code, detail in issues:
            print(f"{code}:{detail}")
        raise SystemExit(1)

    print("PHASE2_FIXDEP_ACTION_PATH=pass")
    print(f"PHASE2_FIXDEP_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_DOCS_MARKER_COUNT={len(REQUIRED_DOCS_README_MARKERS)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_REVIEW_MARKER_COUNT={len(REQUIRED_REVIEW_MARKERS)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_SCRIPTS_MARKER_COUNT={len(REQUIRED_SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_TESTS_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}")
    print(f"PHASE2_FIXDEP_ACTION_PATH_CASE_COUNT={len(EXPECTED_CASE_NAMES)}")


if __name__ == "__main__":
    main()
