#!/usr/bin/env python3
"""Guard the live Phase 2 kconfig bridge Makefile and workflow hooks."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

REQUIRED_PHONY_TARGET = "phase2-kconfig"
REQUIRED_MAKEFILE_TARGET = "phase2-kconfig: phase2-toolchain"
REQUIRED_MAKEFILE_LINES = (
    REQUIRED_MAKEFILE_TARGET,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
)
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
)
EXPECTED_SELF_TEST_CASE_COUNT = 5


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, suffix = stripped.split(":", 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def count_target_definitions(text: str, target: str) -> int:
    prefix = f"{target}:"
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    makefile_text = read_text(root / "zigux" / "Makefile")
    workflow_text = read_text(root / ".github" / "workflows" / "zigux-bootstrap.yml")

    if REQUIRED_PHONY_TARGET not in phony_targets_present(makefile_text):
        issues.append(("MISSING_PHONY_TARGET", REQUIRED_PHONY_TARGET))

    target_count = count_target_definitions(makefile_text, REQUIRED_PHONY_TARGET)
    if target_count == 0:
        issues.append(("MISSING_TARGET_DEFINITION", REQUIRED_MAKEFILE_TARGET))
    elif target_count != 1:
        issues.append(("DUPLICATE_TARGET_DEFINITION", f"{REQUIRED_MAKEFILE_TARGET}:count={target_count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_KCONFIG_ROUTE_HOOKS=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


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


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "zigux" / "Makefile",
        "\n".join(
            (
                ".PHONY: phase2-toolchain phase2-kconfig phase2-validate",
                REQUIRED_MAKEFILE_TARGET,
                *REQUIRED_MAKEFILE_LINES[1:],
            )
        )
        + "\n",
    )
    write_text(
        root / ".github" / "workflows" / "zigux-bootstrap.yml",
        "\n".join(REQUIRED_WORKFLOW_LINES) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_route_hooks_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / "zigux" / "Makefile"
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0]),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / "zigux" / "Makefile"
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                ".PHONY: phase2-toolchain phase2-kconfig phase2-validate",
                ".PHONY: phase2-toolchain phase2-validate",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_PHONY_TARGET", REQUIRED_PHONY_TARGET) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / "zigux" / "Makefile"
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_TARGET),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_TARGET_DEFINITION",
            f"{REQUIRED_MAKEFILE_TARGET}:count=2",
        ) in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_ROUTE_HOOKS_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ROUTE_HOOKS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the live Phase 2 kconfig bridge route hooks.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ROUTE_HOOKS=pass")
    print(f"PHASE2_KCONFIG_ROUTE_TARGET={REQUIRED_PHONY_TARGET}")
    print(f"PHASE2_KCONFIG_ROUTE_MAKEFILE={args.root.resolve() / 'zigux' / 'Makefile'}")
    print(f"PHASE2_KCONFIG_ROUTE_WORKFLOW={args.root.resolve() / '.github' / 'workflows' / 'zigux-bootstrap.yml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
