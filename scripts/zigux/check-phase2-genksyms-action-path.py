#!/usr/bin/env python3
"""Check that the Phase 2 genksyms action path stays aligned."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_README = Path("Documentation/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MAKEFILE = Path("zigux/Makefile")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    WORKFLOW,
    DOCS_README,
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    TOOL_MANIFEST,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-genksyms",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_DOCS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "`python3 scripts/zigux/check-genksyms-bridge.py`",
    "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_REVIEW_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "genksyms bridge",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_TESTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/`",
    "`make -C zigux phase2-genksyms`",
)

EXPECTED_CHECKERS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
)

EXPECTED_BRIDGE_HELPERS = (
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

EXPECTED_FIXTURE_ROSTER = (
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
)

EXPECTED_MAKE_WRAPPER = "make -C zigux phase2-genksyms"


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
        issues.append(("WORKFLOW_ORDER_MISMATCH", "phase2-genksyms-route-order"))

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
        issues.append(("MAKEFILE_ORDER_MISMATCH", "phase2-genksyms-packet-order"))

    collect_marker_issues(
        issues,
        docs_readme_text,
        "MISSING_DOCS_README_MARKER",
        REQUIRED_DOCS_README_MARKERS,
    )
    collect_marker_issues(
        issues,
        bootstrap_notes_text,
        "MISSING_BOOTSTRAP_MARKER",
        REQUIRED_BOOTSTRAP_MARKERS,
    )
    collect_marker_issues(
        issues,
        review_text,
        "MISSING_REVIEW_MARKER",
        REQUIRED_REVIEW_MARKERS,
    )
    collect_marker_issues(
        issues,
        scripts_text,
        "MISSING_SCRIPTS_README_MARKER",
        REQUIRED_SCRIPTS_README_MARKERS,
    )
    collect_marker_issues(
        issues,
        tests_text,
        "MISSING_TESTS_MARKER",
        REQUIRED_TESTS_README_MARKERS,
    )

    expect_subset(
        issues,
        "checkers",
        require_manifest_list(issues, manifest, "checkers"),
        EXPECTED_CHECKERS,
    )
    expect_subset(
        issues,
        "bridge_helpers",
        require_manifest_list(issues, manifest, "bridge_helpers"),
        EXPECTED_BRIDGE_HELPERS,
    )
    expect_subset(
        issues,
        "fixture_roster",
        require_manifest_list(issues, manifest, "fixture_roster"),
        EXPECTED_FIXTURE_ROSTER,
    )
    make_wrappers = require_manifest_list(issues, manifest, "make_wrappers")
    if make_wrappers is not None and EXPECTED_MAKE_WRAPPER not in make_wrappers:
        issues.append(("MISSING_MANIFEST_SURFACE", f"make_wrappers:{EXPECTED_MAKE_WRAPPER}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, WORKFLOW), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(resolve(root, DOCS_README), "\n".join(REQUIRED_DOCS_README_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(REQUIRED_BOOTSTRAP_MARKERS) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "\n".join(REQUIRED_REVIEW_MARKERS) + "\n")
    write_text(resolve(root, SCRIPTS_README), "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n")
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(
            {
                "present_surfaces": {
                    "checkers": list(EXPECTED_CHECKERS),
                    "bridge_helpers": list(EXPECTED_BRIDGE_HELPERS),
                    "fixture_roster": list(EXPECTED_FIXTURE_ROSTER),
                    "make_wrappers": [EXPECTED_MAKE_WRAPPER],
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    expected_case_count = (
        2
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_DOCS_README_MARKERS)
        + len(REQUIRED_BOOTSTRAP_MARKERS)
        + len(REQUIRED_REVIEW_MARKERS)
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(EXPECTED_CHECKERS)
        + len(EXPECTED_BRIDGE_HELPERS)
        + len(EXPECTED_FIXTURE_ROSTER)
        + 1
    )
    cases_run = 0

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_sample_root(root)
        assert not collect_issues(root)
        cases_run += 1

        missing_file_root = root / "missing-file"
        build_sample_root(missing_file_root)
        resolve(missing_file_root, TESTS_README).unlink()
        issues = collect_issues(missing_file_root)
        assert ("MISSING_REQUIRED_FILE", TESTS_README.as_posix()) in issues
        cases_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            case_root = root / f"missing-workflow-{cases_run}"
            build_sample_root(case_root)
            workflow_path = resolve(case_root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_WORKFLOW_LINE", marker) in issues
            cases_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            case_root = root / f"missing-make-{cases_run}"
            build_sample_root(case_root)
            makefile_path = resolve(case_root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_MAKEFILE_LINE", marker) in issues
            cases_run += 1

        for marker in REQUIRED_DOCS_README_MARKERS:
            case_root = root / f"missing-docs-{cases_run}"
            build_sample_root(case_root)
            docs_path = resolve(case_root, DOCS_README)
            docs_path.write_text(
                replace_once(docs_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_DOCS_README_MARKER", marker) in issues
            cases_run += 1

        for marker in REQUIRED_BOOTSTRAP_MARKERS:
            case_root = root / f"missing-bootstrap-{cases_run}"
            build_sample_root(case_root)
            notes_path = resolve(case_root, BOOTSTRAP_NOTES)
            notes_path.write_text(
                replace_once(notes_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_BOOTSTRAP_MARKER", marker) in issues
            cases_run += 1

        for marker in REQUIRED_REVIEW_MARKERS:
            case_root = root / f"missing-review-{cases_run}"
            build_sample_root(case_root)
            review_path = resolve(case_root, REVIEW_CHECKLIST)
            review_path.write_text(
                replace_once(review_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_REVIEW_MARKER", marker) in issues
            cases_run += 1

        for marker in REQUIRED_SCRIPTS_README_MARKERS:
            case_root = root / f"missing-scripts-{cases_run}"
            build_sample_root(case_root)
            scripts_path = resolve(case_root, SCRIPTS_README)
            scripts_path.write_text(
                replace_once(scripts_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in issues
            cases_run += 1

        for marker in REQUIRED_TESTS_README_MARKERS:
            case_root = root / f"missing-tests-{cases_run}"
            build_sample_root(case_root)
            tests_path = resolve(case_root, TESTS_README)
            tests_path.write_text(
                replace_once(tests_path.read_text(encoding="utf-8"), marker).rstrip() + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(case_root)
            assert ("MISSING_TESTS_MARKER", marker) in issues
            cases_run += 1

        for marker in EXPECTED_CHECKERS:
            case_root = root / f"missing-checker-{cases_run}"
            build_sample_root(case_root)
            manifest_path = resolve(case_root, TOOL_MANIFEST)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["checkers"].remove(marker)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(case_root)
            assert ("MISSING_MANIFEST_SURFACE", f"checkers:{marker}") in issues
            cases_run += 1

        for marker in EXPECTED_BRIDGE_HELPERS:
            case_root = root / f"missing-bridge-helper-{cases_run}"
            build_sample_root(case_root)
            manifest_path = resolve(case_root, TOOL_MANIFEST)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["bridge_helpers"].remove(marker)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(case_root)
            assert ("MISSING_MANIFEST_SURFACE", f"bridge_helpers:{marker}") in issues
            cases_run += 1

        for marker in EXPECTED_FIXTURE_ROSTER:
            case_root = root / f"missing-fixture-{cases_run}"
            build_sample_root(case_root)
            manifest_path = resolve(case_root, TOOL_MANIFEST)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["fixture_roster"].remove(marker)
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(case_root)
            assert ("MISSING_MANIFEST_SURFACE", f"fixture_roster:{marker}") in issues
            cases_run += 1

        case_root = root / "missing-make-wrapper"
        build_sample_root(case_root)
        manifest_path = resolve(case_root, TOOL_MANIFEST)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["make_wrappers"].remove(EXPECTED_MAKE_WRAPPER)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(case_root)
        assert ("MISSING_MANIFEST_SURFACE", f"make_wrappers:{EXPECTED_MAKE_WRAPPER}") in issues
        cases_run += 1

    assert cases_run == expected_case_count, (cases_run, expected_case_count)
    print("PHASE2_GENKSYMS_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal passing sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    docs_text = read_text(resolve(root, DOCS_README))
    bootstrap_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    review_text = read_text(resolve(root, REVIEW_CHECKLIST))
    scripts_text = read_text(resolve(root, SCRIPTS_README))
    tests_text = read_text(resolve(root, TESTS_README))

    print("PHASE2_GENKSYMS_ACTION_PATH=pass")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(
        "PHASE2_GENKSYMS_ACTION_PATH_DOCS_MARKER_COUNT="
        f"{sum(marker in docs_text for marker in REQUIRED_DOCS_README_MARKERS)}"
    )
    print(
        "PHASE2_GENKSYMS_ACTION_PATH_BOOTSTRAP_MARKER_COUNT="
        f"{sum(marker in bootstrap_text for marker in REQUIRED_BOOTSTRAP_MARKERS)}"
    )
    print(
        "PHASE2_GENKSYMS_ACTION_PATH_REVIEW_MARKER_COUNT="
        f"{sum(marker in review_text for marker in REQUIRED_REVIEW_MARKERS)}"
    )
    print(
        "PHASE2_GENKSYMS_ACTION_PATH_SCRIPTS_MARKER_COUNT="
        f"{sum(marker in scripts_text for marker in REQUIRED_SCRIPTS_README_MARKERS)}"
    )
    print(
        "PHASE2_GENKSYMS_ACTION_PATH_TESTS_MARKER_COUNT="
        f"{sum(marker in tests_text for marker in REQUIRED_TESTS_README_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
