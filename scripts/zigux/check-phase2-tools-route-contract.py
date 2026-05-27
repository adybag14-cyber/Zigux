#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
VALIDATE_PHASE2 = Path("scripts/zigux/validate-phase2.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_PATHS = (
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-bootstrap-workflow-routes.py"),
    Path("scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    Path("scripts/zigux/artifact_diff.py"),
    Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json"),
)

VALIDATE_REQUIRED_SNIPPETS = (
    '"scripts/zigux/check-phase2-kbuild-routes.py",',
    '"scripts/zigux/check-phase2-docs-shared-reminder.py",',
    '"scripts/zigux/check-phase2-required-make-routes.py",',
    '"scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
    '"scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"scripts/zigux/artifact_diff.py",',
    '"zigux/tests/fixtures/phase2_artifact_tools_manifest.json",',
    '"run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-kbuild-routes.py",',
    '"run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",',
    '"run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-required-make-routes.py",',
    '"run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
    '"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"run: make -C zigux phase2-tools",',
    '"run: make -C zigux phase2-validate",',
    '"run: python3 scripts/zigux/validate-phase2.py",',
    '"phase2-tools:",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",',
    '"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

EXPECTED_SELF_TEST_CASE_COUNT = 13


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str, prefix: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, f"{prefix}{marker}")
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    validate_phase2_path = root / VALIDATE_PHASE2
    makefile_path = root / MAKEFILE
    workflow_path = root / WORKFLOW

    for path in (validate_phase2_path, makefile_path, workflow_path):
        if not path.is_file():
            issues.append(("MISSING_REQUIRED_FILE", path.relative_to(root).as_posix()))
            return issues

    validate_phase2_text = read_text(validate_phase2_path)
    makefile_text = read_text(makefile_path)
    workflow_text = read_text(workflow_path)

    for rel_path in REQUIRED_PATHS:
        if not (root / rel_path).is_file():
            issues.append(("MISSING_REQUIRED_PATH", rel_path.as_posix()))

    for snippet in VALIDATE_REQUIRED_SNIPPETS:
        count = count_exact_line(validate_phase2_text, snippet)
        if count == 0:
            issues.append(("MISSING_VALIDATE_PHASE2_SNIPPET", snippet))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_PHASE2_SNIPPET", f"{snippet}:count={count}"))

    for line in REQUIRED_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, line)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{line}:count={count}"))

    for line in REQUIRED_WORKFLOW_LINES:
        count = count_exact_line(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{line}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_TOOLS_ROUTE_CONTRACT=fail")
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)
    for code, details in grouped.items():
        print(f"{code}_START")
        for detail in details:
            print(detail)
        print(f"{code}_END")
    return 1


def build_validate_phase2_text() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "REQUIRED_PATHS = (",
            '    "scripts/zigux/check-phase2-kbuild-routes.py",',
            '    "scripts/zigux/check-phase2-docs-shared-reminder.py",',
            '    "scripts/zigux/check-phase2-required-make-routes.py",',
            '    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
            '    "scripts/zigux/check-phase2-artifact-tools-manifest.py",',
            '    "scripts/zigux/artifact_diff.py",',
            '    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",',
            ")",
            "REQUIRED_WORKFLOW_LINES = (",
            '    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",',
            '    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",',
            '    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",',
            '    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",',
            '    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",',
            '    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",',
            '    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",',
            '    "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",',
            '    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",',
            '    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",',
            '    "run: make -C zigux phase2-tools",',
            '    "run: make -C zigux phase2-validate",',
            '    "run: python3 scripts/zigux/validate-phase2.py",',
            ")",
            "REQUIRED_MAKEFILE_LINES = (",
            '    "phase2-tools:",',
            '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",',
            '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",',
            '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",',
            '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",',
            '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",',
            '    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
            ")",
        ]
    ) + "\n"


def build_makefile_text() -> str:
    return "\n".join(
        [
            "phase2-tools:",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
            "",
            "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        ]
    ) + "\n"


def build_workflow_text() -> str:
    return "\n".join(
        [
            "name: zigux-bootstrap",
            "- name: Self-test current Phase 2 kbuild routes checker",
            "  run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
            "- name: Check current Phase 2 kbuild packet",
            "  run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
            "- name: Self-test current Phase 2 shared reminder checker",
            "  run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
            "- name: Check current Phase 2 shared reminder packet",
            "  run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
            "- name: Self-test current Phase 2 required-make-routes checker",
            "  run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
            "- name: Check current Phase 2 required-make-routes packet",
            "  run: python3 scripts/zigux/check-phase2-required-make-routes.py",
            "- name: Self-test current Phase 2 bootstrap workflow-routes checker",
            "  run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
            "- name: Check current Phase 2 bootstrap workflow-routes packet",
            "  run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
            "- name: Self-test current Phase 2 artifact tools manifest checker",
            "  run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
            "- name: Check current Phase 2 artifact tools manifest packet",
            "  run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
            "- name: Run current Phase 2 tools make route",
            "  run: make -C zigux phase2-tools",
            "- name: Run current Phase 2 validate make route",
            "  run: make -C zigux phase2-validate",
            "- name: Validate current Phase 2 tool packet",
            "  run: python3 scripts/zigux/validate-phase2.py",
        ]
    ) + "\n"


def build_good_root(root: Path) -> None:
    write_text(root / VALIDATE_PHASE2, build_validate_phase2_text())
    write_text(root / MAKEFILE, build_makefile_text())
    write_text(root / WORKFLOW, build_workflow_text())
    for rel_path in REQUIRED_PATHS:
        write_text(root / rel_path, "placeholder\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_tools_route_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_good_root(root)
        if collect_issues(root):
            raise SystemExit("phase2-tools-route-contract:self-test:good_root")
        case_count += 1

        build_good_root(root)
        validate_path = root / VALIDATE_PHASE2
        validate_path.write_text(
            read_text(validate_path).replace(VALIDATE_REQUIRED_SNIPPETS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("MISSING_VALIDATE_PHASE2_SNIPPET", VALIDATE_REQUIRED_SNIPPETS[0]) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_validate_snippet")
        case_count += 1

        build_good_root(root)
        validate_path = root / VALIDATE_PHASE2
        validate_path.write_text(
            duplicate_exact_line(read_text(validate_path), VALIDATE_REQUIRED_SNIPPETS[7], "    "),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("DUPLICATE_VALIDATE_PHASE2_SNIPPET", f"{VALIDATE_REQUIRED_SNIPPETS[7]}:count=2") not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:duplicate_validate_snippet")
        case_count += 1

        build_good_root(root)
        makefile_path = root / MAKEFILE
        makefile_path.write_text(
            read_text(makefile_path).replace(REQUIRED_MAKEFILE_LINES[1] + "\n", "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_makefile_line")
        case_count += 1

        build_good_root(root)
        makefile_path = root / MAKEFILE
        makefile_path.write_text(
            duplicate_exact_line(read_text(makefile_path), REQUIRED_MAKEFILE_LINES[4], "\t"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[4]}:count=2") not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:duplicate_makefile_line")
        case_count += 1

        build_good_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            read_text(workflow_path).replace(REQUIRED_WORKFLOW_LINES[0] + "\n", "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_workflow_line")
        case_count += 1

        build_good_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            duplicate_exact_line(read_text(workflow_path), REQUIRED_WORKFLOW_LINES[7], "  "),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[7]}:count=2") not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:duplicate_workflow_line")
        case_count += 1

        build_good_root(root)
        (root / REQUIRED_PATHS[0]).unlink()
        issues = collect_issues(root)
        if ("MISSING_REQUIRED_PATH", REQUIRED_PATHS[0].as_posix()) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_required_path")
        case_count += 1

        build_good_root(root)
        (root / VALIDATE_PHASE2).unlink()
        issues = collect_issues(root)
        if ("MISSING_REQUIRED_FILE", VALIDATE_PHASE2.as_posix()) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_validate_file")
        case_count += 1

        build_good_root(root)
        (root / MAKEFILE).unlink()
        issues = collect_issues(root)
        if ("MISSING_REQUIRED_FILE", MAKEFILE.as_posix()) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_makefile_file")
        case_count += 1

        build_good_root(root)
        (root / WORKFLOW).unlink()
        issues = collect_issues(root)
        if ("MISSING_REQUIRED_FILE", WORKFLOW.as_posix()) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_workflow_file")
        case_count += 1

        build_good_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            replace_exact_line(read_text(workflow_path), REQUIRED_WORKFLOW_LINES[10], "  run: make -C zigux phase2-other"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[10]) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_phase2_tools_route")
        case_count += 1

        build_good_root(root)
        validate_path = root / VALIDATE_PHASE2
        validate_path.write_text(
            replace_exact_line(read_text(validate_path), VALIDATE_REQUIRED_SNIPPETS[24], '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/other.py",'),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        if ("MISSING_VALIDATE_PHASE2_SNIPPET", VALIDATE_REQUIRED_SNIPPETS[24]) not in issues:
            raise SystemExit("phase2-tools-route-contract:self-test:missing_bootstrap_workflow_routes_snippet")
        case_count += 1

    print("PHASE2_TOOLS_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_TOOLS_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    if case_count != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit("phase2-tools-route-contract:self-test:unexpected_case_count")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the live Phase 2 phase2-tools packet stays aligned across "
            "validate-phase2.py, zigux/Makefile, and the bootstrap workflow."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLS_ROUTE_CONTRACT=pass")
    print(f"PHASE2_TOOLS_ROUTE_CONTRACT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_TOOLS_ROUTE_CONTRACT_VALIDATE_SNIPPET_COUNT={len(VALIDATE_REQUIRED_SNIPPETS)}")
    print(f"PHASE2_TOOLS_ROUTE_CONTRACT_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_TOOLS_ROUTE_CONTRACT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())