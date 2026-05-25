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
GENKSYMS_SURVEY = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MAKEFILE = Path("zigux/Makefile")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    WORKFLOW,
    DOCS_README,
    GENKSYMS_SURVEY,
    PHASE2_CLOSURE,
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
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
)

REQUIRED_DOCS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_SURVEY_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`zig test scripts/zigux/genksyms.zig`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`zig test scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_REVIEW_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
)

REQUIRED_TESTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
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

EXPECTED_MAKE_WRAPPERS = ("make -C zigux phase2-genksyms",)

EXPECTED_FIXTURE_ROSTER = (
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
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
    survey_text = read_text(resolve(root, GENKSYMS_SURVEY))
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
        issues, docs_readme_text, "MISSING_DOCS_README_MARKER", REQUIRED_DOCS_README_MARKERS
    )
    collect_marker_issues(issues, survey_text, "MISSING_SURVEY_MARKER", REQUIRED_SURVEY_MARKERS)
    collect_marker_issues(issues, closure_text, "MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS)
    collect_marker_issues(issues, review_text, "MISSING_REVIEW_MARKER", REQUIRED_REVIEW_MARKERS)
    collect_marker_issues(
        issues, scripts_text, "MISSING_SCRIPTS_README_MARKER", REQUIRED_SCRIPTS_README_MARKERS
    )
    collect_marker_issues(issues, tests_text, "MISSING_TESTS_MARKER", REQUIRED_TESTS_README_MARKERS)

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
        "make_wrappers",
        require_manifest_list(issues, manifest, "make_wrappers"),
        EXPECTED_MAKE_WRAPPERS,
    )
    expect_subset(
        issues,
        "fixture_roster",
        require_manifest_list(issues, manifest, "fixture_roster"),
        EXPECTED_FIXTURE_ROSTER,
    )

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
    write_text(resolve(root, GENKSYMS_SURVEY), "\n".join(REQUIRED_SURVEY_MARKERS) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE), "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
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
                    "make_wrappers": list(EXPECTED_MAKE_WRAPPERS),
                    "fixture_roster": list(EXPECTED_FIXTURE_ROSTER),
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + 1
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + 1
        + len(REQUIRED_DOCS_README_MARKERS)
        + len(REQUIRED_SURVEY_MARKERS)
        + len(REQUIRED_CLOSURE_MARKERS)
        + len(REQUIRED_REVIEW_MARKERS)
        + len(REQUIRED_SCRIPTS_README_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(EXPECTED_CHECKERS)
        + len(EXPECTED_BRIDGE_HELPERS)
        + len(EXPECTED_MAKE_WRAPPERS)
        + len(EXPECTED_FIXTURE_ROSTER)
        + len(REQUIRED_FILES)
        + 1
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_action_path_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve(root, WORKFLOW)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, WORKFLOW)
        path.write_text("\n".join(reversed(REQUIRED_WORKFLOW_LINES)) + "\n", encoding="utf-8")
        assert ("WORKFLOW_ORDER_MISMATCH", "phase2-genksyms-route-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve(root, MAKEFILE)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, MAKEFILE)
        path.write_text("\n".join(reversed(REQUIRED_MAKEFILE_LINES)) + "\n", encoding="utf-8")
        assert ("MAKEFILE_ORDER_MISMATCH", "phase2-genksyms-packet-order") in collect_issues(root)
        checks += 1

        for marker in REQUIRED_DOCS_README_MARKERS:
            build_sample_root(root)
            path = resolve(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_DOCS_README_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_SURVEY_MARKERS:
            build_sample_root(root)
            path = resolve(root, GENKSYMS_SURVEY)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SURVEY_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_CLOSURE_MARKERS:
            build_sample_root(root)
            path = resolve(root, PHASE2_CLOSURE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_CLOSURE_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_REVIEW_MARKERS:
            build_sample_root(root)
            path = resolve(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_REVIEW_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_SCRIPTS_README_MARKERS:
            build_sample_root(root)
            path = resolve(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_TESTS_README_MARKERS:
            build_sample_root(root)
            path = resolve(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in EXPECTED_CHECKERS:
            build_sample_root(root)
            path = resolve(root, TOOL_MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["checkers"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_SURFACE", f"checkers:{marker}") in collect_issues(root)
            checks += 1

        for marker in EXPECTED_BRIDGE_HELPERS:
            build_sample_root(root)
            path = resolve(root, TOOL_MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["bridge_helpers"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_SURFACE", f"bridge_helpers:{marker}") in collect_issues(root)
            checks += 1

        for marker in EXPECTED_MAKE_WRAPPERS:
            build_sample_root(root)
            path = resolve(root, TOOL_MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["make_wrappers"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_SURFACE", f"make_wrappers:{marker}") in collect_issues(root)
            checks += 1

        for marker in EXPECTED_FIXTURE_ROSTER:
            build_sample_root(root)
            path = resolve(root, TOOL_MANIFEST)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["fixture_roster"].remove(marker)
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_SURFACE", f"fixture_roster:{marker}") in collect_issues(root)
            checks += 1

        for rel in REQUIRED_FILES:
            build_sample_root(root)
            resolve(root, rel).unlink()
            assert ("MISSING_REQUIRED_FILE", rel.as_posix()) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        path = resolve(root, TOOL_MANIFEST)
        path.write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid manifest JSON did not abort")

    assert checks == expected_case_count, (checks, expected_case_count)
    print("PHASE2_GENKSYMS_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 genksyms action path stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_ACTION_PATH=pass")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_DOCS_MARKER_COUNT={len(REQUIRED_DOCS_README_MARKERS)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_SURVEY_MARKER_COUNT={len(REQUIRED_SURVEY_MARKERS)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_REVIEW_MARKER_COUNT={len(REQUIRED_REVIEW_MARKERS)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_SCRIPTS_MARKER_COUNT={len(REQUIRED_SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_GENKSYMS_ACTION_PATH_TESTS_MARKER_COUNT={len(REQUIRED_TESTS_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
