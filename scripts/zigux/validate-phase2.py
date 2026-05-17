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
PHASE2_CROSS_TARGETS_REL = "zigux/tests/fixtures/phase2_cross_targets.json"

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
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py --zig \"$(ZIG)\"',
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

EXPECTED_SELF_TEST_CASE_COUNT = 17


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    scripts_readme_text = read_text(root, SCRIPTS_README)
    tests_readme_text = read_text(root, TESTS_README)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    makefile_text = read_text(root, MAKEFILE)

    for marker in EXPECTED_MAKEFILE_LINES:
        if marker not in makefile_text:
            issues.append(("MISSING_MAKEFILE_LINES", marker))

    for marker in EXPECTED_PRESENT_FILE_MARKERS:
        if marker not in scripts_readme_text:
            issues.append(("MISSING_SCRIPTS_README_MARKERS", marker))
        if marker not in tests_readme_text:
            issues.append(("MISSING_TESTS_README_MARKERS", marker))
        if marker not in review_checklist_text:
            issues.append(("MISSING_REVIEW_CHECKLIST_MARKERS", marker))

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
        assert ("MISSING_MAKEFILE_LINES", EXPECTED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        for code, path in (
            ("MISSING_SCRIPTS_README_MARKERS", SCRIPTS_README),
            ("MISSING_TESTS_README_MARKERS", TESTS_README),
            ("MISSING_REVIEW_CHECKLIST_MARKERS", REVIEW_CHECKLIST),
        ):
            build_self_test_root(root)
            target = resolve_path(root, path)
            target.write_text(
                replace_once(target.read_text(encoding="utf-8"), EXPECTED_PRESENT_FILE_MARKERS[0]),
                encoding="utf-8",
            )
            assert (code, EXPECTED_PRESENT_FILE_MARKERS[0]) in collect_issues(root)
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
