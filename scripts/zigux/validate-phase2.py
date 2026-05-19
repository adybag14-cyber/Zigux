#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"

REQUIRED_PATHS = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    MAKEFILE,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: make -C zigux phase2-toolchain",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/validate-phase2.py",
)

DISALLOWED_WORKFLOW_LINES = (
    "name: Run current Phase 2 genksyms bridge unit tests",
    "run: zig test scripts/zigux/genksyms.zig",
)

REQUIRED_PHASE2_PHONY_LINE = ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2"
REQUIRED_PHASE2_PHONY_TARGETS = tuple(REQUIRED_PHASE2_PHONY_LINE.split(":", 1)[1].strip().split())

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

DISALLOWED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(REQUIRED_WORKFLOW_LINES)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(DISALLOWED_WORKFLOW_LINES)
    + 2
    + len(REQUIRED_MAKEFILE_LINES)
    + len(REQUIRED_MAKEFILE_LINES)
    + len(DISALLOWED_MAKEFILE_LINES)
    + (len(REQUIRED_PATHS) - 1)
    + 2
)


def path_under(root: Path, rel: str) -> Path:
    return root / rel


def read_text(root: Path, rel: str) -> str:
    path = path_under(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = path_under(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


def has_required_phase2_phony_targets(text: str) -> bool:
    return set(REQUIRED_PHASE2_PHONY_TARGETS).issubset(phony_targets_present(text))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in DISALLOWED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count != 0:
            issues.append(("UNEXPECTED_WORKFLOW_LINE", f"{marker}:count={count}"))

    if not has_required_phase2_phony_targets(makefile_text):
        issues.append(("MISSING_MAKEFILE_LINE", REQUIRED_PHASE2_PHONY_LINE))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in DISALLOWED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count != 0:
            issues.append(("UNEXPECTED_MAKEFILE_LINE", f"{marker}:count={count}"))

    for rel in REQUIRED_PATHS:
        if not path_under(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

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


def build_self_test_root(root: Path) -> None:
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    write_text(root, WORKFLOW, "\n".join(workflow_lines) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            [
                "PYTHON ?= python3",
                "ZIG ?= zig",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "ZIGUX_ROOT := ..",
                "",
                REQUIRED_PHASE2_PHONY_LINE,
                *REQUIRED_MAKEFILE_LINES,
            ]
        )
        + "\n",
    )
    for rel in REQUIRED_PATHS:
        if rel != MAKEFILE:
            write_text(root, rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(
                    workflow_path.read_text(encoding="utf-8"),
                    marker,
                    "run: python3 scripts/zigux/other.py",
                ),
                encoding="utf-8",
            )
            assert (("MISSING_WORKFLOW_LINE", marker) in collect_issues(root))
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root))
            checks_run += 1

        for marker in DISALLOWED_WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = path_under(root, WORKFLOW)
            workflow_path.write_text(
                workflow_path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            assert (("UNEXPECTED_WORKFLOW_LINE", f"{marker}:count=1") in collect_issues(root))
            checks_run += 1

        build_self_test_root(root)
        makefile_path = path_under(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                REQUIRED_PHASE2_PHONY_LINE,
                "# removed for self-test",
            ),
            encoding="utf-8",
        )
        assert (("MISSING_MAKEFILE_LINE", REQUIRED_PHASE2_PHONY_LINE) in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        makefile_path = path_under(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                REQUIRED_PHASE2_PHONY_LINE,
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3",
            ),
            encoding="utf-8",
        )
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = path_under(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker, "# removed for self-test"),
                encoding="utf-8",
            )
            assert (("MISSING_MAKEFILE_LINE", marker) in collect_issues(root))
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = path_under(root, MAKEFILE)
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root))
            checks_run += 1

        for marker in DISALLOWED_MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = path_under(root, MAKEFILE)
            makefile_path.write_text(
                makefile_path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            assert (("UNEXPECTED_MAKEFILE_LINE", f"{marker}:count=1") in collect_issues(root))
            checks_run += 1

        for rel in REQUIRED_PATHS[:-1]:
            build_self_test_root(root)
            path = path_under(root, rel)
            path.unlink()
            issues = collect_issues(root)
            assert (("MISSING_REQUIRED_PATH", rel) in issues)
            checks_run += 1

        build_self_test_root(root)
        path_under(root, WORKFLOW).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing workflow did not abort")
        checks_run += 1

        build_self_test_root(root)
        path_under(root, MAKEFILE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing makefile did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 2 toolchain, kbuild, and kconfig packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATION=pass")
    print(f"PHASE2_VALIDATION_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
