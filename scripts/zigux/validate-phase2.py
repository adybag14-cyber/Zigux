#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
FIXDEP = ROOT / "scripts" / "zigux" / "fixdep.zig"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
PHASE2_CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

CHECKERS = (
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py",
)

EXPECTED_PRESENT_FILE_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/Makefile`",
)

EXPECTED_MAKEFILE_LINES = (
    ".PHONY: phase2-validate phase2-toolchain phase2-fixdep phase2-tools phase2-kconfig phase2-cross phase2",
    "phase2-toolchain:",
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py --zig "$(ZIG)"',
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "phase2-fixdep: phase2-toolchain",
    "phase2-tools: phase2-fixdep",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
    "phase2-kconfig: phase2-toolchain",
    "phase2-validate: phase2-tools phase2-kconfig",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "phase2-cross: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
    "phase2: phase2-validate phase2-cross",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
)

DISALLOWED_MAKEFILE_LINES = (
    "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
    "PHASE3_SCRIPT_ROOT := ../scripts/zigux",
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase10-validate phase10-test phase10",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "phase2: phase2-validate",
)

EXPECTED_SELF_TEST_CASE_COUNT = 28


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(root: Path, path: Path) -> str:
    resolved = resolve_path(root, path)
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc


def count_exact_lines(text: str, line: str) -> int:
    return sum(1 for item in text.splitlines() if item == line)


def collect_marker_count_issues(
    text: str,
    marker: str,
    *,
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    count = text.count(marker)
    if count == 0:
        return [(missing_code, marker)]
    if count != 1:
        return [(duplicate_code, f"{marker}:count={count}")]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    scripts_readme_text = read_text(root, SCRIPTS_README)
    tests_readme_text = read_text(root, TESTS_README)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    makefile_text = read_text(root, MAKEFILE)

    for marker in EXPECTED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in DISALLOWED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count != 0:
            issues.append(("UNEXPECTED_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in EXPECTED_PRESENT_FILE_MARKERS:
        issues.extend(
            collect_marker_count_issues(
                scripts_readme_text,
                marker,
                missing_code="MISSING_SCRIPTS_README_MARKERS",
                duplicate_code="DUPLICATE_SCRIPTS_README_MARKERS",
            )
        )
        issues.extend(
            collect_marker_count_issues(
                tests_readme_text,
                marker,
                missing_code="MISSING_TESTS_README_MARKERS",
                duplicate_code="DUPLICATE_TESTS_README_MARKERS",
            )
        )
        issues.extend(
            collect_marker_count_issues(
                review_checklist_text,
                marker,
                missing_code="MISSING_REVIEW_CHECKLIST_MARKERS",
                duplicate_code="DUPLICATE_REVIEW_CHECKLIST_MARKERS",
            )
        )

    for path in (CLOSURE_DOC, CLOSURE_VALIDATOR, WORKFLOW, FIXDEP, CONF_BRIDGE, PHASE2_CROSS_TARGETS):
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_FILE", path.relative_to(ROOT).as_posix()))
    for path in CHECKERS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_CHECKER", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(root: Path, path: Path, content: str) -> None:
    resolved = resolve_path(root, path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(root, CLOSURE_DOC, "# present\n")
    for path in (SCRIPTS_README, TESTS_README, REVIEW_CHECKLIST):
        write_text(root, path, "\n".join(EXPECTED_PRESENT_FILE_MARKERS) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            [
                "PYTHON ?= python3",
                "ZIG ?= zig",
                "ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)",
                "",
                *EXPECTED_MAKEFILE_LINES,
            ]
        )
        + "\n",
    )
    write_text(root, CLOSURE_VALIDATOR, "# present\n")
    write_text(root, WORKFLOW, "name: zigux-bootstrap\n")
    write_text(root, FIXDEP, "// present\n")
    write_text(root, CONF_BRIDGE, "// present\n")
    write_text(
        root,
        PHASE2_CROSS_TARGETS,
        '{\n  "phase": "Phase 2",\n  "status": "closed",\n  "target_count": 3,\n  "targets": [\n    "x86_64-linux-musl",\n    "aarch64-linux-musl",\n    "riscv64-linux-musl"\n  ],\n  "zig_test_files": [\n    "scripts/zigux/fixdep.zig"\n  ]\n}\n',
    )
    for path in CHECKERS:
        write_text(root, path, "# present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, f"{marker}\n{marker}", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), EXPECTED_MAKEFILE_LINES[0]), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", EXPECTED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_once(path.read_text(encoding="utf-8"), EXPECTED_MAKEFILE_LINES[1]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINE", f"{EXPECTED_MAKEFILE_LINES[1]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(path.read_text(encoding="utf-8") + DISALLOWED_MAKEFILE_LINES[0] + "\n", encoding="utf-8")
        assert ("UNEXPECTED_MAKEFILE_LINE", f"{DISALLOWED_MAKEFILE_LINES[0]}:count=1") in collect_issues(root)
        checks_run += 1

        for code, duplicate_code, path in (
            ("MISSING_SCRIPTS_README_MARKERS", "DUPLICATE_SCRIPTS_README_MARKERS", SCRIPTS_README),
            ("MISSING_TESTS_README_MARKERS", "DUPLICATE_TESTS_README_MARKERS", TESTS_README),
            ("MISSING_REVIEW_CHECKLIST_MARKERS", "DUPLICATE_REVIEW_CHECKLIST_MARKERS", REVIEW_CHECKLIST),
        ):
            for marker in EXPECTED_PRESENT_FILE_MARKERS:
                build_self_test_root(root)
                target = resolve_path(root, path)
                target.write_text(
                    replace_once(target.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                assert (code, marker) in collect_issues(root)
                checks_run += 1

                build_self_test_root(root)
                target = resolve_path(root, path)
                target.write_text(
                    duplicate_once(target.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                assert (duplicate_code, f"{marker}:count=2") in collect_issues(root)
                checks_run += 1

        for path in (CLOSURE_DOC, CLOSURE_VALIDATOR, WORKFLOW, FIXDEP, CONF_BRIDGE, PHASE2_CROSS_TARGETS):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_REQUIRED_FILE", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

        for path in CHECKERS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert ("MISSING_CHECKER", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the current-master-safe shared Phase 2 packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATION=pass")
    print(f"PHASE2_REQUIRED_CHECKER_COUNT={len(CHECKERS)}")
    print(f"PHASE2_REQUIRED_ROUTE_COUNT={len(EXPECTED_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
