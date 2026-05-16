#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
README = ROOT / "scripts" / "zigux" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

REQUIRED_FILES = [
    WORKFLOW,
    README,
    MAKEFILE,
    INSTALL_ZIG,
    CHECK_ZIG_TOOLCHAIN,
]

EXACT_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/install-zig.py --self-test": 1,
    "python3 scripts/zigux/install-zig.py --dest .zig-toolchain": 2,
    "python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "python3 scripts/zigux/check-zig-toolchain.py": 1,
    "zig version": 2,
}

REQUIRED_README_MARKERS = [
    "Zig toolchain gate",
    "check-zig-toolchain.py",
    "check-zig-toolchain.py --self-test",
    "minimum version",
]

REQUIRED_MAKEFILE_MARKERS = [
    "ZIG ?= zig",
    "$(ZIG) test scripts/zigux/fixdep.zig",
    "$(ZIG) test scripts/zigux/genksyms.zig",
    "$(ZIG) test scripts/zigux/genksyms_crc.zig",
    "$(ZIG) test scripts/zigux/mk_elfconfig.zig",
    "$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
]

DISALLOWED_WORKFLOW_MARKERS = [
    "--channel master",
]

DISALLOWED_MAKEFILE_MARKERS = [
    ".zig-toolchain/zig",
    "zig-master",
    "toolchains/zig",
]

INSTALL_ZIG_REQUIRED_MARKERS = [
    "--dest",
    "--self-test",
]

CHECK_ZIG_REQUIRED_MARKERS = [
    "--self-test",
    "minimum",
    "version",
]

EXPECTED_SELF_TEST_CASE_COUNT = 6


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow = root / ".github" / "workflows" / "zigux-bootstrap.yml"
    readme = root / "scripts" / "zigux" / "README.md"
    makefile = root / "zigux" / "Makefile"
    install_zig = root / "scripts" / "zigux" / "install-zig.py"
    check_zig = root / "scripts" / "zigux" / "check-zig-toolchain.py"

    issues: list[tuple[str, str]] = []

    for path in (workflow, readme, makefile, install_zig, check_zig):
        if not path.exists():
            issues.append(("MISSING_FILE", str(path.relative_to(root))))

    if issues:
        return issues

    workflow_text = workflow.read_text(encoding="utf-8")
    readme_text = readme.read_text(encoding="utf-8")
    makefile_text = makefile.read_text(encoding="utf-8")
    install_zig_text = install_zig.read_text(encoding="utf-8")
    check_zig_text = check_zig.read_text(encoding="utf-8")

    for command, expected_count in EXACT_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        actual_count = sum(1 for line in workflow_text.splitlines() if line.strip() == expected_line)
        if actual_count != expected_count:
            issues.append(("WORKFLOW_RUN_COUNT", f"{command}:count={actual_count}:expected={expected_count}"))

    for marker in DISALLOWED_WORKFLOW_MARKERS:
        if marker in workflow_text:
            issues.append(("WORKFLOW_DISALLOWED_MARKER", marker))

    for marker in REQUIRED_README_MARKERS:
        if marker not in readme_text:
            issues.append(("README_MARKER", marker))

    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            issues.append(("MAKEFILE_MARKER", marker))

    for marker in DISALLOWED_MAKEFILE_MARKERS:
        if marker in makefile_text:
            issues.append(("MAKEFILE_DISALLOWED_MARKER", marker))

    for marker in INSTALL_ZIG_REQUIRED_MARKERS:
        if marker not in install_zig_text:
            issues.append(("INSTALL_ZIG_MARKER", marker))

    for marker in CHECK_ZIG_REQUIRED_MARKERS:
        if marker not in check_zig_text:
            issues.append(("CHECK_ZIG_TOOLCHAIN_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_TOOLCHAIN_PINNING=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root / ".github" / "workflows" / "zigux-bootstrap.yml",
        """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Self-test Zig installer
        run: python3 scripts/zigux/install-zig.py --self-test
      - name: Install Zig
        run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain
      - name: Show Zig version
        run: zig version
      - name: Self-test Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
  phase2-cross:
    steps:
      - name: Install Zig
        run: python3 scripts/zigux/install-zig.py --dest .zig-toolchain
      - name: Show Zig version
        run: zig version
      - name: Check Zig toolchain policy
        run: python3 scripts/zigux/check-zig-toolchain.py
""",
    )
    write_text(
        root / "scripts" / "zigux" / "README.md",
        """# scripts/zigux

Zig toolchain gate
- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.
- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.
""",
    )
    write_text(
        root / "zigux" / "Makefile",
        """ZIG ?= zig

phase2-tools:
	$(ZIG) test scripts/zigux/fixdep.zig
	$(ZIG) test scripts/zigux/genksyms.zig
	$(ZIG) test scripts/zigux/genksyms_crc.zig
	$(ZIG) test scripts/zigux/mk_elfconfig.zig

phase2-kconfig:
	$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
	$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig
""",
    )
    write_text(
        root / "scripts" / "zigux" / "install-zig.py",
        """#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dest")
parser.add_argument("--self-test", action="store_true")
""",
    )
    write_text(
        root / "scripts" / "zigux" / "check-zig-toolchain.py",
        """#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--self-test", action="store_true")
minimum = "0.17.0"
version = minimum
""",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        workflow = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        write_text(
            workflow,
            workflow.read_text(encoding="utf-8").replace(
                "python3 scripts/zigux/install-zig.py --dest .zig-toolchain",
                "python3 scripts/zigux/install-zig.py --channel master --dest .zig-toolchain",
                1,
            ),
        )
        issues = collect_issues(root)
        assert ("WORKFLOW_DISALLOWED_MARKER", "--channel master") in issues
        checks_run += 1

        build_self_test_root(root)
        workflow = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        write_text(
            workflow,
            workflow.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/check-zig-toolchain.py --self-test\n",
                "",
                1,
            ),
        )
        issues = collect_issues(root)
        assert any(
            block == "WORKFLOW_RUN_COUNT"
            and value == "python3 scripts/zigux/check-zig-toolchain.py --self-test:count=0:expected=1"
            for block, value in issues
        )
        checks_run += 1

        build_self_test_root(root)
        readme = root / "scripts" / "zigux" / "README.md"
        write_text(
            readme,
            readme.read_text(encoding="utf-8").replace("minimum version", "required release", 1),
        )
        issues = collect_issues(root)
        assert ("README_MARKER", "minimum version") in issues
        checks_run += 1

        build_self_test_root(root)
        makefile = root / "zigux" / "Makefile"
        write_text(
            makefile,
            makefile.read_text(encoding="utf-8").replace("ZIG ?= zig", "ZIG ?= .zig-toolchain/zig", 1),
        )
        issues = collect_issues(root)
        assert ("MAKEFILE_DISALLOWED_MARKER", ".zig-toolchain/zig") in issues
        checks_run += 1

        build_self_test_root(root)
        check_zig = root / "scripts" / "zigux" / "check-zig-toolchain.py"
        write_text(
            check_zig,
            check_zig.read_text(encoding="utf-8").replace('parser.add_argument("--self-test", action="store_true")\n', ""),
        )
        issues = collect_issues(root)
        assert ("CHECK_ZIG_TOOLCHAIN_MARKER", "--self-test") in issues
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=fail")
        print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Phase 2 Zig toolchain pinning surfaces.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in toolchain-pinning checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(ROOT)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE2_TOOLCHAIN_REQUIRED_MARKER_COUNT="
        f"{len(EXACT_WORKFLOW_RUN_COUNTS) + len(REQUIRED_README_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(INSTALL_ZIG_REQUIRED_MARKERS) + len(CHECK_ZIG_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
