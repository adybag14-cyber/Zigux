#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CONFDATA_SURVEY = ROOT / "Documentation" / "zigux" / "phase2-confdata-bridge-survey.md"

VALIDATOR_MARKERS = (
    'ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"',
    'ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"',
    '"scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"',
    '"scripts/zigux/check-phase2-kconfig-selftest-alignment.py"',
    '"scripts/zigux/check-kconfig-bridge.py --self-test"',
    '"scripts/zigux/check-kconfig-bridge.py"',
    "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 25",
)
VALIDATOR_EXACT_COUNTS = {
    '"scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"': 1,
    '"scripts/zigux/check-phase2-kconfig-selftest-alignment.py"': 2,
    '"scripts/zigux/check-kconfig-bridge.py --self-test"': 1,
    '"scripts/zigux/check-kconfig-bridge.py"': 3,
    "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 25": 1,
}

CLOSURE_VALIDATOR_MARKERS = (
    "shared kconfig selftest-alignment self-test",
    'KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"',
    "16-case` conf bridge plus `13-case` confdata fixture replay",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: python3 scripts/zigux/validate-phase2-closure.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
)

MAKEFILE_LINES = (
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
)

SCRIPTS_README_MARKERS = (
    "check-phase2-kconfig-readme-alignment.py --self-test",
    "dedicated kconfig bridge checker packet documented through the shared Phase 2 reminder surface",
    "`check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, `validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`, `check-phase2-tests-readme-alignment.py`, `check-phase2-kconfig-readme-alignment.py`, `check-phase2-tool-manifest-packets.py`, `check-phase2-fixdep-gate.py`, `check-fixdep-diff.py`, `check-genksyms-bridge.py`, `check-phase2-cross.py`, `check-phase2-cross-selftest-alignment.py`, and `check-phase2-kconfig-selftest-alignment.py` are the live shared scripts-root Phase 2 helpers on current `master`",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "the shipped direct kconfig bridge replays",
)

REVIEW_CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "make -C zigux phase2-kconfig",
)

PHASE2_CLOSURE_DOC_MARKERS = (
    "shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "shared kconfig selftest-alignment gate: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "direct replay owners stay split on current `master`: `zig test scripts/zigux/fixdep.zig` remains the shipped direct Phase 2 Zig replay, while the broader fixdep, genksyms, artifact-tools, and kconfig bridge evidence stays documented through `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, `zigux/tests/README.md`, and `zigux/Makefile` instead of implying unshipped direct bridge or artifact replay entrypoints on current `master`",
)

PHASE2_BOOTSTRAP_NOTES_MARKERS = (
    "the broader fixdep, genksyms, artifact-tools, kconfig bridge, and manifest packet should stay documented through `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` instead of presenting non-existent standalone checker scripts as live current-`master` evidence in this dedicated pin-scope note",
    "the closure note, tests root, and Makefile keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json` plus `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded fixdep replay, the committed genksyms and artifact-tools fixtures, and the direct kconfig and confdata Zig replays reviewable without restating missing standalone checker scripts in this dedicated pin-scope note",
    "the active Phase 2 closure note and tests root keep the shipped fixdep workflow gate plus the direct `zig test scripts/zigux/fixdep.zig` replay explicit beside the same bounded tools route",
    "the Linux-style `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` replay routes keep this dedicated note tied to the same kbuild-facing replay surface named by `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, the shared validator pair, and the closure note",
)

PHASE2_CONFDATA_SURVEY_MARKERS = (
    "`zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 13 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, `empty_config_symbol_names`, `last_state_transitions`, and `duplicate_malformed_quoted_assignment`.",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` now keep the already-landed confdata bridge packet reviewable through the shared Phase 2 reminder surface instead of reviving the older dedicated `check-kconfig-bridge.py` scaffold claim.",
    "When a writable checkout and Zig toolchain are available, rerun `python3 scripts/zigux/check-kconfig-bridge.py --self-test`, the full `python3 scripts/zigux/check-kconfig-bridge.py` gate, and the shared Phase 2 closure validators against the now `13-case` confdata packet.",
)

PHASE2_CONFDATA_SURVEY_FORBIDDEN_MARKERS = (
    "`scripts/zigux/check-kconfig-bridge.py`",
    "11 fixture cases",
    "same 11-case packet",
)

EXPECTED_SELF_TEST_CASE_COUNT = 27

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc

def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path

def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def count_exact_substrings(text: str, marker: str) -> int:
    return text.count(marker)

def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]

def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]

def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    validator_text = read_text(resolve_path(root, PHASE2_VALIDATOR))
    closure_validator_text = read_text(resolve_path(root, PHASE2_CLOSURE_VALIDATOR))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    closure_doc_text = read_text(resolve_path(root, PHASE2_CLOSURE_DOC))
    bootstrap_notes_text = read_text(resolve_path(root, PHASE2_BOOTSTRAP_NOTES))
    confdata_survey_text = read_text(resolve_path(root, PHASE2_CONFDATA_SURVEY))

    issues.extend(collect_missing_markers(validator_text, VALIDATOR_MARKERS, "MISSING_VALIDATOR_MARKERS"))
    for marker, expected_count in VALIDATOR_EXACT_COUNTS.items():
        count = count_exact_substrings(validator_text, marker)
        if count != expected_count:
            issues.append(("DUPLICATE_VALIDATOR_MARKERS", f"{marker}:count={count}:expected={expected_count}"))

    issues.extend(
        collect_missing_markers(
            closure_validator_text, CLOSURE_VALIDATOR_MARKERS, "MISSING_CLOSURE_VALIDATOR_MARKERS"
        )
    )

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(
        collect_missing_markers(review_checklist_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS")
    )
    issues.extend(
        collect_missing_markers(closure_doc_text, PHASE2_CLOSURE_DOC_MARKERS, "MISSING_CLOSURE_DOC_MARKERS")
    )
    issues.extend(
        collect_missing_markers(bootstrap_notes_text, PHASE2_BOOTSTRAP_NOTES_MARKERS, "MISSING_BOOTSTRAP_NOTES_MARKERS")
    )
    issues.extend(
        collect_missing_markers(confdata_survey_text, PHASE2_CONFDATA_SURVEY_MARKERS, "MISSING_CONFDATA_SURVEY_MARKERS")
    )
    issues.extend(
        collect_forbidden_markers(
            confdata_survey_text,
            PHASE2_CONFDATA_SURVEY_FORBIDDEN_MARKERS,
            "FORBIDDEN_CONFDATA_SURVEY_MARKERS",
        )
    )
    return issues

def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_KCONFIG_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def build_self_test_root(root: Path) -> None:
    validator_lines = [
        VALIDATOR_MARKERS[0],
        VALIDATOR_MARKERS[1],
        VALIDATOR_MARKERS[2],
        VALIDATOR_MARKERS[3],
        VALIDATOR_MARKERS[3],
        VALIDATOR_MARKERS[4],
        VALIDATOR_MARKERS[5],
        VALIDATOR_MARKERS[5],
        VALIDATOR_MARKERS[5],
        VALIDATOR_MARKERS[6],
    ]
    write_text(resolve_path(root, PHASE2_VALIDATOR), "\n".join(validator_lines) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE_VALIDATOR), "\n".join(CLOSURE_VALIDATOR_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE_DOC), "\n".join(PHASE2_CLOSURE_DOC_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_BOOTSTRAP_NOTES), "\n".join(PHASE2_BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_CONFDATA_SURVEY), "\n".join(PHASE2_CONFDATA_SURVEY_MARKERS) + "\n")

def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)

def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")

def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_kconfig_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_VALIDATOR)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), VALIDATOR_MARKERS[0], ""), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", VALIDATOR_MARKERS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_VALIDATOR)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                VALIDATOR_MARKERS[6],
                "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 14",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "MISSING_VALIDATOR_MARKERS",
            "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 25",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_VALIDATOR)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                VALIDATOR_MARKERS[2],
                VALIDATOR_MARKERS[2] + "\n" + VALIDATOR_MARKERS[2],
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "DUPLICATE_VALIDATOR_MARKERS",
            f'{VALIDATOR_MARKERS[2]}:count=2:expected=1',
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_VALIDATOR)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), VALIDATOR_MARKERS[4], ""),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", VALIDATOR_MARKERS[4]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_CLOSURE_VALIDATOR)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), CLOSURE_VALIDATOR_MARKERS[0], ""),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CLOSURE_VALIDATOR_MARKERS", CLOSURE_VALIDATOR_MARKERS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), WORKFLOW_LINES[2], "run: python3 other.py --self-test"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", WORKFLOW_LINES[2]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), WORKFLOW_LINES[3]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{WORKFLOW_LINES[3]}:count=2") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                WORKFLOW_LINES[6],
                "run: python3 other-kconfig.py --self-test",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", WORKFLOW_LINES[6]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                MAKEFILE_LINES[3],
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/other.py --self-test",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", MAKEFILE_LINES[3]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[4]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{MAKEFILE_LINES[4]}:count=2") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                MAKEFILE_LINES[7],
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/other-kconfig.py --self-test",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", MAKEFILE_LINES[7]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[8]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{MAKEFILE_LINES[8]}:count=2") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, SCRIPTS_README)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), SCRIPTS_README_MARKERS[2], ""), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_SCRIPTS_README_MARKERS", SCRIPTS_README_MARKERS[2]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), TESTS_README_MARKERS[0], ""), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_TESTS_README_MARKERS", TESTS_README_MARKERS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, REVIEW_CHECKLIST)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), REVIEW_CHECKLIST_MARKERS[1], ""),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_REVIEW_CHECKLIST_MARKERS", REVIEW_CHECKLIST_MARKERS[1]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_CLOSURE_DOC)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), PHASE2_CLOSURE_DOC_MARKERS[0], ""),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CLOSURE_DOC_MARKERS", PHASE2_CLOSURE_DOC_MARKERS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_BOOTSTRAP_NOTES)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), PHASE2_BOOTSTRAP_NOTES_MARKERS[1], ""),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_BOOTSTRAP_NOTES_MARKERS", PHASE2_BOOTSTRAP_NOTES_MARKERS[1]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_CONFDATA_SURVEY)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), PHASE2_CONFDATA_SURVEY_MARKERS[0], ""),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_CONFDATA_SURVEY_MARKERS", PHASE2_CONFDATA_SURVEY_MARKERS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, PHASE2_CONFDATA_SURVEY)
        path.write_text(
            path.read_text(encoding="utf-8") + PHASE2_CONFDATA_SURVEY_FORBIDDEN_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "FORBIDDEN_CONFDATA_SURVEY_MARKERS",
            PHASE2_CONFDATA_SURVEY_FORBIDDEN_MARKERS[0],
        ) in issues
        checks_run += 1

        for rel_path in (
            PHASE2_VALIDATOR,
            PHASE2_CLOSURE_VALIDATOR,
            WORKFLOW,
            MAKEFILE,
            SCRIPTS_README,
            TESTS_README,
            PHASE2_CONFDATA_SURVEY,
        ):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 kconfig packet stays aligned with the live validator, docs, tests, workflow, and make surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())