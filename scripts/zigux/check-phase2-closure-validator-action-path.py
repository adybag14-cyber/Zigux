#!/usr/bin/env python3
"""Check that the indirect Phase 2 closure-validator action path stays aligned."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[1] if len(HERE.parents) > 1 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_README = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MAKEFILE = Path("zigux/Makefile")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    WORKFLOW,
    DOCS_README,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    TOOL_MANIFEST,
)

REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_DOCS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "PHASE2_CLOSURE_VALIDATORS=",
)

REQUIRED_REVIEW_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_TESTS_README_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

EXPECTED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_MAKE_WRAPPERS = (
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

EXPECTED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
)

REQUIRED_PHASE2_PHONY_TARGETS = ("phase2-validate", "phase2")


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


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], category: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(category)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", category))
        return None
    return list(value)


def collect_marker_issues(
    issues: list[tuple[str, str]], text: str, code: str, markers: tuple[str, ...]
) -> None:
    for marker in markers:
        if marker not in text:
            issues.append((code, marker))


def expect_subset(
    issues: list[tuple[str, str]],
    label: str,
    actual: list[str] | None,
    expected: tuple[str, ...],
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def parse_phase2_phony_targets(text: str) -> list[str] | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            return stripped.split(":", 1)[1].strip().split()
    return None


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    docs_readme_text = read_text(resolve(root, DOCS_README))
    bootstrap_notes_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE))
    review_text = read_text(resolve(root, REVIEW_CHECKLIST))
    scripts_text = read_text(resolve(root, SCRIPTS_README))
    tests_text = read_text(resolve(root, TESTS_README))
    manifest = read_json(resolve(root, TOOL_MANIFEST))
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

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
        issues.append(("WORKFLOW_ORDER_MISMATCH", "phase2-closure-validator-route-order"))

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
        issues.append(("MAKEFILE_ORDER_MISMATCH", "phase2-closure-validator-route-order"))

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
        issues, bootstrap_notes_text, "MISSING_BOOTSTRAP_MARKER", REQUIRED_BOOTSTRAP_MARKERS
    )
    collect_marker_issues(
        issues, closure_text, "MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS
    )
    collect_marker_issues(
        issues, review_text, "MISSING_REVIEW_MARKER", REQUIRED_REVIEW_MARKERS
    )
    collect_marker_issues(
        issues, scripts_text, "MISSING_SCRIPTS_MARKER", REQUIRED_SCRIPTS_README_MARKERS
    )
    collect_marker_issues(
        issues, tests_text, "MISSING_TESTS_MARKER", REQUIRED_TESTS_README_MARKERS
    )

    validators = require_manifest_list(issues, manifest, "validators")
    make_wrappers = require_manifest_list(issues, manifest, "make_wrappers")
    review_surfaces = require_manifest_list(issues, manifest, "review_surfaces")
    expect_subset(issues, "validators", validators, EXPECTED_VALIDATORS)
    expect_subset(issues, "make_wrappers", make_wrappers, EXPECTED_MAKE_WRAPPERS)
    expect_subset(issues, "review_surfaces", review_surfaces, EXPECTED_REVIEW_SURFACES)
    return issues


def report_counts(root: Path) -> None:
    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    docs_readme_text = read_text(resolve(root, DOCS_README))
    bootstrap_notes_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE))
    review_text = read_text(resolve(root, REVIEW_CHECKLIST))
    scripts_text = read_text(resolve(root, SCRIPTS_README))
    tests_text = read_text(resolve(root, TESTS_README))
    manifest = read_json(resolve(root, TOOL_MANIFEST))
    assert isinstance(manifest, dict)
    validators = manifest["present_surfaces"]["validators"]
    make_wrappers = manifest["present_surfaces"]["make_wrappers"]
    print("PHASE2_CLOSURE_VALIDATOR_ACTION_PATH=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(
        f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_DOCS_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_DOCS_README_MARKERS if marker in docs_readme_text)}"
    )
    print(
        f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_BOOTSTRAP_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_BOOTSTRAP_MARKERS if marker in bootstrap_notes_text)}"
    )
    print(
        f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_CLOSURE_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_CLOSURE_MARKERS if marker in closure_text)}"
    )
    print(
        f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_REVIEW_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_REVIEW_MARKERS if marker in review_text)}"
    )
    print(
        f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_SCRIPTS_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_SCRIPTS_README_MARKERS if marker in scripts_text)}"
    )
    print(
        f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_TESTS_MARKER_COUNT="
        f"{sum(1 for marker in REQUIRED_TESTS_README_MARKERS if marker in tests_text)}"
    )
    print(
        "PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_VALIDATOR_COUNT="
        f"{sum(1 for item in validators if item in EXPECTED_VALIDATORS)}"
    )
    print(
        "PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_MAKE_WRAPPER_COUNT="
        f"{sum(1 for item in make_wrappers if item in EXPECTED_MAKE_WRAPPERS)}"
    )
    print(
        "PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_WORKFLOW_VALIDATION_LINES="
        f"{sum(1 for marker in REQUIRED_WORKFLOW_LINES if count_exact_lines(workflow_text, marker) == 1)}"
    )
    print(
        "PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_MAKEFILE_VALIDATION_LINES="
        f"{sum(1 for marker in REQUIRED_MAKEFILE_LINES if count_exact_lines(makefile_text, marker) == 1)}"
    )


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"{code}={detail}")
        return 1
    report_counts(root)
    return 0


def sample_manifest() -> dict[str, object]:
    return {
        "present_surfaces": {
            "validators": [
                "scripts/zigux/validate-phase2.py",
                "scripts/zigux/validate-phase2-closure.py",
            ],
            "make_wrappers": [
                "make -C zigux phase2-toolchain",
                "make -C zigux phase2-validate",
                "make -C zigux phase2",
            ],
            "review_surfaces": [
                "Documentation/zigux/README.md",
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/review-checklist.md",
                "zigux/tests/README.md",
            ],
        }
    }


def write_sample_root(root: Path) -> None:
    write_text(
        resolve(root, WORKFLOW),
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 2 validate make route",
                "        run: make -C zigux phase2-validate",
                "      - name: Validate current Phase 2 tool packet",
                "        run: python3 scripts/zigux/validate-phase2.py",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, MAKEFILE),
        "\n".join(
            [
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
                "phase2: phase2-validate",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, DOCS_README),
        "\n".join(
            [
                "# Docs",
                "`scripts/zigux/validate-phase2.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`zigux/Makefile`",
                "`make -C zigux phase2-validate`",
                "`make -C zigux phase2`",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, BOOTSTRAP_NOTES),
        "\n".join(
            [
                "# Notes",
                "`Documentation/zigux/phase2-closure.md`",
                "`scripts/zigux/validate-phase2.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`scripts/zigux/check-phase2-tool-manifest.py`",
                "`make -C zigux phase2-validate`",
                "`make -C zigux phase2`",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, PHASE2_CLOSURE),
        "\n".join(
            [
                "# Closure",
                "`scripts/zigux/validate-phase2.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`scripts/zigux/check-phase2-tool-manifest.py`",
                "`make -C zigux phase2-validate`",
                "`make -C zigux phase2`",
                "PHASE2_CLOSURE_VALIDATORS=scripts/zigux/validate-phase2.py,scripts/zigux/validate-phase2-closure.py",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, REVIEW_CHECKLIST),
        "\n".join(
            [
                "# Review",
                "`Documentation/zigux/phase2-closure.md`",
                "`scripts/zigux/validate-phase2.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`make -C zigux phase2-validate`",
                "`make -C zigux phase2`",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, SCRIPTS_README),
        "\n".join(
            [
                "# Scripts",
                "`scripts/zigux/validate-phase2.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`scripts/zigux/check-phase2-tool-manifest.py`",
                "`zigux/Makefile`",
                "`make -C zigux phase2-validate`",
                "`make -C zigux phase2`",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, TESTS_README),
        "\n".join(
            [
                "# Tests",
                "`scripts/zigux/validate-phase2.py`",
                "`scripts/zigux/validate-phase2-closure.py`",
                "`scripts/zigux/check-phase2-tool-manifest.py`",
                "`zigux/Makefile`",
                "`make -C zigux phase2-validate`",
                "`make -C zigux phase2`",
                "",
            ]
        ),
    )
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(sample_manifest(), indent=2) + "\n",
    )


def run_self_test() -> int:
    def quiet_check(root: Path) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return run_check(root)

    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase2_closure_validator_action_path_") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        assert quiet_check(root) == 0
        cases += 1

        broken_workflow = read_text(resolve(root, WORKFLOW))
        write_text(
            resolve(root, WORKFLOW),
            replace_exact_line(broken_workflow, REQUIRED_WORKFLOW_LINES[0]),
        )
        assert quiet_check(root) == 1
        cases += 1
        write_sample_root(root)

        duplicate_workflow = read_text(resolve(root, WORKFLOW))
        write_text(
            resolve(root, WORKFLOW),
            duplicate_exact_line(duplicate_workflow, REQUIRED_WORKFLOW_LINES[0]),
        )
        assert quiet_check(root) == 1
        cases += 1
        write_sample_root(root)

        broken_makefile = read_text(resolve(root, MAKEFILE))
        write_text(
            resolve(root, MAKEFILE),
            replace_exact_line(broken_makefile, REQUIRED_MAKEFILE_LINES[2]),
        )
        assert quiet_check(root) == 1
        cases += 1
        write_sample_root(root)

        broken_docs = read_text(resolve(root, DOCS_README))
        write_text(
            resolve(root, DOCS_README),
            replace_once(broken_docs, REQUIRED_DOCS_README_MARKERS[1]),
        )
        assert quiet_check(root) == 1
        cases += 1
        write_sample_root(root)

        broken_closure = read_text(resolve(root, PHASE2_CLOSURE))
        write_text(
            resolve(root, PHASE2_CLOSURE),
            replace_once(broken_closure, "PHASE2_CLOSURE_VALIDATORS="),
        )
        assert quiet_check(root) == 1
        cases += 1
        write_sample_root(root)

        manifest = sample_manifest()
        manifest["present_surfaces"]["validators"] = ["scripts/zigux/validate-phase2.py"]
        write_text(resolve(root, TOOL_MANIFEST), json.dumps(manifest, indent=2) + "\n")
        assert quiet_check(root) == 1
        cases += 1
        write_sample_root(root)

        broken_phony = read_text(resolve(root, MAKEFILE))
        write_text(
            resolve(root, MAKEFILE),
            replace_once(broken_phony, "phase2-validate", "phase2-validate-missing",),
        )
        assert quiet_check(root) == 1
        cases += 1

    print("PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_ACTION_PATH_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0
    if args.self_test:
        return run_self_test()
    return run_check(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
