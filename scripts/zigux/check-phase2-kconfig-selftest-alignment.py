#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) >= 3 else Path.cwd()
CHECKER = Path("scripts/zigux/check-kconfig-bridge.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_CHECKER_MARKERS = (
    'env["KCONFIG_ALLCONFIG"] = case["allconfig_env"]',
    'env["KCONFIG_AUTOCONFIG"] = case["autoconfig"]',
    'env["KCONFIG_AUTOHEADER"] = case["autoheader"]',
    'env["KCONFIG_NOSILENTUPDATE"] = case["nosilentupdate"]',
)
REQUIRED_MAKEFILE_LINES = (
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
)
REQUIRED_WORKFLOW_LINES = (
    'run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
    'run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    checker_text = read_text(root / CHECKER)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)
    makefile_lines = {line.strip() for line in makefile_text.splitlines()}
    workflow_lines = {line.strip() for line in workflow_text.splitlines()}

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKERS", marker))

    for marker in REQUIRED_MAKEFILE_LINES:
        if marker not in makefile_lines:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        if marker not in workflow_lines:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_KCONFIG_ALIGNMENT=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / CHECKER,
        "\n".join((
            "def replay(case, env):",
            '    env["KCONFIG_ALLCONFIG"] = case["allconfig_env"]',
            '    env["KCONFIG_AUTOCONFIG"] = case["autoconfig"]',
            '    env["KCONFIG_AUTOHEADER"] = case["autoheader"]',
            '    env["KCONFIG_NOSILENTUPDATE"] = case["nosilentupdate"]',
            "",
        )),
    )
    write_text(
        root / MAKEFILE,
        "\n".join((
            "phase2-kconfig:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
            "",
        )),
    )
    write_text(
        root / WORKFLOW,
        "\n".join((
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Self-test Phase 2 kconfig selftest alignment",
            "        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "      - name: Check Phase 2 kconfig selftest alignment",
            "        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            "",
        )),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_p2_kconfig_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        cases = 0
        for marker in REQUIRED_CHECKER_MARKERS:
            build_self_test_root(root)
            path = root / CHECKER
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "# removed", 1), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_CHECKER_MARKERS", marker) in issues
            cases += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "\ttrue"), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_HOOKS", marker) in issues
            cases += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "        run: python3 other.py"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            cases += 1

    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 kconfig replay guard stays wired into the shared gate surface."
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
    print(f"PHASE2_KCONFIG_ALIGNMENT_CHECKER_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
