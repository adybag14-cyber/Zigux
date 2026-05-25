#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

CHECKER = "scripts/zigux/check-zig-toolchain.py"
INSTALLER = "scripts/zigux/install-zig.py"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
README = "scripts/zigux/README.md"
MAKEFILE = "zigux/Makefile"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_PATHS = (
    CHECKER,
    INSTALLER,
    POLICY,
    README,
    MAKEFILE,
    WORKFLOW,
)

CHECKER_MARKERS = (
    "def policy_archive_filename(",
    "def iter_archive_search_roots(",
    "def archive_name_has_duplicate_suffix(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
    'parser.add_argument("--allow-missing"',
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing",
    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid",
    "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME=",
    "ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256=",
    "resolve_policy_archive(root=root, policy_path=policy_path)",
    'expect_raises(lambda: validate_policy_archive(duplicate_archive_path, "aarch64-linux", policy_path=policy_path), "is not pinned")',
)

INSTALLER_MARKERS = (
    "def infer_tarball_url(",
    "suffix = '.zip' if system_key == 'windows' else '.tar.xz'",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "def copy_url_to_file(",
    "def resolve_target(",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
)

README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
)


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(root: Path, rel: str) -> str:
    path = resolve(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = resolve(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    checker = read_text(root, CHECKER)
    installer = read_text(root, INSTALLER)
    readme = read_text(root, README)
    makefile = read_text(root, MAKEFILE)
    workflow = read_text(root, WORKFLOW)

    for marker in CHECKER_MARKERS:
        if marker not in checker:
            issues.append(("MISSING_CHECKER_MARKER", marker))

    for marker in INSTALLER_MARKERS:
        if marker not in installer:
            issues.append(("MISSING_INSTALLER_MARKER", marker))

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_README_MARKER", marker))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(root, CHECKER, "\n".join(CHECKER_MARKERS) + "\n")
    write_text(root, INSTALLER, "\n".join(INSTALLER_MARKERS) + "\n")
    write_text(root, POLICY, '{ "phase": "Phase 2" }\n')
    write_text(root, README, "\n".join(README_MARKERS) + "\n")
    write_text(root, MAKEFILE, "\n".join(MAKEFILE_LINES) + "\n")
    write_text(root, WORKFLOW, "\n".join(WORKFLOW_LINES) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_toolchain_checker_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in CHECKER_MARKERS:
            build_self_test_root(root)
            write_text(root, CHECKER, replace_once(read_text(root, CHECKER), marker))
            assert ("MISSING_CHECKER_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in INSTALLER_MARKERS:
            build_self_test_root(root)
            write_text(root, INSTALLER, replace_once(read_text(root, INSTALLER), marker))
            assert ("MISSING_INSTALLER_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in README_MARKERS:
            build_self_test_root(root)
            write_text(root, README, replace_once(read_text(root, README), marker))
            assert ("MISSING_README_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE, replace_once(read_text(root, MAKEFILE), marker))
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), marker))
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, replace_once(read_text(root, WORKFLOW), marker))
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), marker))
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks += 1

        for rel in REQUIRED_PATHS:
            build_self_test_root(root)
            resolve(root, rel).unlink()
            try:
                issues = collect_issues(root)
            except SystemExit as exc:
                assert f"required file missing: {resolve(root, rel)}" in str(exc)
            else:
                assert ("MISSING_REQUIRED_PATH", rel) in issues
            checks += 1

    print("LANE03_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"LANE03_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Lane 03 toolchain checker packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("LANE03_TOOLCHAIN_CHECKER_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("LANE03_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"LANE03_TOOLCHAIN_CHECKER_MARKER_COUNT={len(CHECKER_MARKERS)}")
    print(f"LANE03_TOOLCHAIN_INSTALLER_MARKER_COUNT={len(INSTALLER_MARKERS)}")
    print(f"LANE03_TOOLCHAIN_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
