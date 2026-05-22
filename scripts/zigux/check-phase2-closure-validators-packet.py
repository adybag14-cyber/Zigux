#!/usr/bin/env python3
"""Guard the exact Phase 2 closure-validator command packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
PHASE2_VALIDATE = "scripts/zigux/validate-phase2.py"
PHASE2_CLOSURE_VALIDATE = "scripts/zigux/validate-phase2-closure.py"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"

EXPECTED_CLOSURE_VALIDATORS = (
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-required-make-routes.py",
    "python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "zig test scripts/zigux/genksyms.zig",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

EXPECTED_MAKE_ROUTES = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_PATHS = (
    PHASE2_CLOSURE,
    PHASE2_VALIDATE,
    PHASE2_CLOSURE_VALIDATE,
    WORKFLOW,
    MAKEFILE,
)

REQUIRED_PHASE2_PHONY_TARGETS = set(route.rsplit(" ", 1)[-1] for route in EXPECTED_MAKE_ROUTES)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
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


def extract_assignment_list(text: str, key: str) -> list[str] | None:
    needle = f"`{key}="
    for line in text.splitlines():
        if needle not in line:
            continue
        start = line.index(needle) + 1
        remainder = line[start:]
        if "`" not in remainder:
            return None
        payload = remainder.split("`", 1)[0]
        value = payload.split("=", 1)[1]
        if value == "":
            return []
        return value.split(",")
    return None


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    closure_text = read_text(root, PHASE2_CLOSURE)
    validate_text = read_text(root, PHASE2_VALIDATE)
    closure_validate_text = read_text(root, PHASE2_CLOSURE_VALIDATE)
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    closure_validators = extract_assignment_list(closure_text, "PHASE2_CLOSURE_VALIDATORS")
    if closure_validators is None:
        issues.append(("MISSING_ASSIGNMENT", "PHASE2_CLOSURE_VALIDATORS"))
    elif tuple(closure_validators) != EXPECTED_CLOSURE_VALIDATORS:
        issues.append(("CLOSURE_VALIDATOR_PACKET_MISMATCH", "PHASE2_CLOSURE_VALIDATORS"))

    make_routes = extract_assignment_list(closure_text, "PHASE2_SHARED_MAKE_ROUTES")
    if make_routes is None:
        issues.append(("MISSING_ASSIGNMENT", "PHASE2_SHARED_MAKE_ROUTES"))
    elif tuple(make_routes) != EXPECTED_MAKE_ROUTES:
        issues.append(("MAKE_ROUTE_PACKET_MISMATCH", "PHASE2_SHARED_MAKE_ROUTES"))
    elif closure_validators is not None and tuple(closure_validators[-len(EXPECTED_MAKE_ROUTES) :]) != EXPECTED_MAKE_ROUTES:
        issues.append(("CLOSURE_VALIDATOR_ROUTE_SUFFIX_MISMATCH", "PHASE2_CLOSURE_VALIDATORS"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    if not REQUIRED_PHASE2_PHONY_TARGETS.issubset(phony_targets_present(makefile_text)):
        issues.append(("MISSING_MAKEFILE_PHONY_TARGETS", ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if 'print("PHASE2_VALIDATION=pass")' not in validate_text:
        issues.append(("MISSING_VALIDATE_MARKER", PHASE2_VALIDATE))
    if 'print("PHASE2_CLOSURE_VALIDATION=pass")' not in closure_validate_text:
        issues.append(("MISSING_VALIDATE_MARKER", PHASE2_CLOSURE_VALIDATE))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATORS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    closure_lines = (
        "# Phase 2 Closure",
        "",
        "## Closure Validation",
        "",
        f"- `PHASE2_CLOSURE_VALIDATORS={','.join(EXPECTED_CLOSURE_VALIDATORS)}`",
        f"- `PHASE2_SHARED_MAKE_ROUTES={','.join(EXPECTED_MAKE_ROUTES)}`",
        "",
    )
    workflow_lines = ("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)
    makefile_lines = (
        "PYTHON ?= python3",
        "ZIG ?= zig",
        "",
        ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
        *REQUIRED_MAKEFILE_LINES,
    )

    write_text(root, PHASE2_CLOSURE, "\n".join(closure_lines) + "\n")
    write_text(
        root,
        PHASE2_VALIDATE,
        '#!/usr/bin/env python3\nprint("PHASE2_VALIDATION=pass")\n',
    )
    write_text(
        root,
        PHASE2_CLOSURE_VALIDATE,
        '#!/usr/bin/env python3\nprint("PHASE2_CLOSURE_VALIDATION=pass")\n',
    )
    write_text(root, WORKFLOW, "\n".join(workflow_lines) + "\n")
    write_text(root, MAKEFILE, "\n".join(makefile_lines) + "\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validators_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        write_text(root, PHASE2_CLOSURE, "# drifted\n")
        expect_issue(root, ("MISSING_ASSIGNMENT", "PHASE2_CLOSURE_VALIDATORS"))
        checks += 1

        build_sample_root(root)
        drifted = replace_exact_line(
            read_text(root, PHASE2_CLOSURE),
            f"- `PHASE2_CLOSURE_VALIDATORS={','.join(EXPECTED_CLOSURE_VALIDATORS)}`",
            f"- `PHASE2_CLOSURE_VALIDATORS={','.join(EXPECTED_CLOSURE_VALIDATORS[:-1])}`",
        )
        write_text(root, PHASE2_CLOSURE, drifted)
        expect_issue(root, ("CLOSURE_VALIDATOR_PACKET_MISMATCH", "PHASE2_CLOSURE_VALIDATORS"))
        checks += 1

        build_sample_root(root)
        drifted = replace_exact_line(
            read_text(root, PHASE2_CLOSURE),
            f"- `PHASE2_SHARED_MAKE_ROUTES={','.join(EXPECTED_MAKE_ROUTES)}`",
            f"- `PHASE2_SHARED_MAKE_ROUTES={','.join(EXPECTED_MAKE_ROUTES[:-1])}`",
        )
        write_text(root, PHASE2_CLOSURE, drifted)
        expect_issue(root, ("MAKE_ROUTE_PACKET_MISMATCH", "PHASE2_SHARED_MAKE_ROUTES"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            PHASE2_CLOSURE,
            replace_exact_line(
                read_text(root, PHASE2_CLOSURE),
                f"- `PHASE2_CLOSURE_VALIDATORS={','.join(EXPECTED_CLOSURE_VALIDATORS)}`",
                f"- `PHASE2_CLOSURE_VALIDATORS={','.join(EXPECTED_CLOSURE_VALIDATORS[:-8] + ('python3 scripts/zigux/validate-phase2-closure.py --self-test',) + EXPECTED_MAKE_ROUTES)}`",
            ),
        )
        expect_issue(root, ("CLOSURE_VALIDATOR_PACKET_MISMATCH", "PHASE2_CLOSURE_VALIDATORS"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
                "run: python3 scripts/zigux/other.py",
            ),
        )
        expect_issue(root, ("MISSING_WORKFLOW_LINE", "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(read_text(root, MAKEFILE), "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep", "# removed"),
        )
        expect_issue(root, ("MISSING_MAKEFILE_LINE", "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(
                read_text(root, MAKEFILE),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
                "# removed",
            ),
        )
        expect_issue(root, ("MISSING_MAKEFILE_LINE", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py"))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(
                read_text(root, MAKEFILE),
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate",
            ),
        )
        expect_issue(
            root,
            (
                "MISSING_MAKEFILE_PHONY_TARGETS",
                ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
            ),
        )
        checks += 1

        build_sample_root(root)
        write_text(root, PHASE2_VALIDATE, '#!/usr/bin/env python3\nprint("OTHER=pass")\n')
        expect_issue(root, ("MISSING_VALIDATE_MARKER", PHASE2_VALIDATE))
        checks += 1

        build_sample_root(root)
        (root / PHASE2_CLOSURE_VALIDATE).unlink()
        expect_issue(root, ("MISSING_REQUIRED_PATH", PHASE2_CLOSURE_VALIDATE))
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            duplicate_exact_line(read_text(root, WORKFLOW), "run: python3 scripts/zigux/validate-phase2.py"),
        )
        expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", "run: python3 scripts/zigux/validate-phase2.py:count=2"))
        checks += 1

    print("PHASE2_CLOSURE_VALIDATORS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATORS_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the exact Phase 2 closure-validator command packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root for focused validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_VALIDATORS_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATORS_PACKET=pass")
    print(f"PHASE2_CLOSURE_VALIDATORS_PACKET_VALIDATOR_COUNT={len(EXPECTED_CLOSURE_VALIDATORS)}")
    print(f"PHASE2_CLOSURE_VALIDATORS_PACKET_ROUTE_COUNT={len(EXPECTED_MAKE_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
