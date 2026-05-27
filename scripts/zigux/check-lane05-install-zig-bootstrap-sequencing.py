#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 install-zig bootstrap workflow contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
INSTALL_ZIG_PATH = Path("scripts/zigux/install-zig.py")

WORKFLOW_MARKERS = (
    "- 'scripts/zigux/**'",
    "- 'third_party/**'",
    "- '.github/workflows/zigux-bootstrap.yml'",
    "- name: Setup pinned Zig toolchain",
    "- name: Self-test current Lane 05 local-first archive checker",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "- name: Check current Lane 05 local-first archive packet",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "- name: Self-test current Lane 05 local archive README checker",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "- name: Check current Lane 05 local archive README packet",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "- name: Self-test current Zig installer helper",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "- name: Self-test current Phase 2 fixdep gate checker",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
)

INSTALL_ZIG_MARKERS = (
    "parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')",
    "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
    "if args.self_test:",
    "if args.resolve_only:",
    "print('ZIG_INSTALL_STATUS=resolved')",
    "print('ZIG_INSTALL_STATUS=pass')",
    "if entry is None and VERSION_KEY_RE.fullmatch(channel):",
    "return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
    "if '-dev.' in channel:",
    "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
    "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'",
    "assert load_index('0.17.0-dev.87+9b177a7d2') == {}",
    "raise AssertionError('expected non-explicit channel timeout to fail')",
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig bootstrap checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig bootstrap checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 install-zig bootstrap checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig bootstrap checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(workflow_text: str) -> None:
    for marker in WORKFLOW_MARKERS:
        require_marker(workflow_text, marker, "workflow marker")

    require_exact_count(
        workflow_text,
        "- name: Self-test current Zig installer helper",
        1,
        "workflow step name",
    )
    require_exact_count(
        workflow_text,
        "run: python3 scripts/zigux/install-zig.py --self-test",
        1,
        "workflow run line",
    )
    require_exact_count(
        workflow_text,
        "- 'third_party/**'",
        1,
        "workflow path filter",
    )
    require_order(
        workflow_text,
        "- name: Check current Lane 05 local archive README packet",
        "- name: Self-test current Zig installer helper",
        "workflow step order",
    )
    require_order(
        workflow_text,
        "- name: Self-test current Zig installer helper",
        "- name: Self-test current Phase 2 fixdep gate checker",
        "workflow step order",
    )


def check_install_zig(install_zig_text: str) -> None:
    for marker in INSTALL_ZIG_MARKERS:
        require_marker(install_zig_text, marker, "install-zig marker")

    require_exact_count(
        install_zig_text,
        "parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')",
        1,
        "resolve-only argument",
    )
    require_exact_count(
        install_zig_text,
        "print('ZIG_INSTALL_STATUS=resolved')",
        1,
        "resolve-only status line",
    )
    require_exact_count(
        install_zig_text,
        "print('ZIG_INSTALL_STATUS=pass')",
        1,
        "pass status line",
    )
    require_order(
        install_zig_text,
        "if args.self_test:",
        "if args.resolve_only:",
        "install-zig control flow",
    )
    require_order(
        install_zig_text,
        "if args.resolve_only:",
        "print('ZIG_INSTALL_STATUS=resolved')",
        "resolve-only status flow",
    )
    require_order(
        install_zig_text,
        "if '-dev.' in channel:",
        "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
        "dev fallback URL flow",
    )
    require_order(
        install_zig_text,
        "if '-dev.' in channel:",
        "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'",
        "stable fallback URL flow",
    )
    require_order(
        install_zig_text,
        "if entry is None and VERSION_KEY_RE.fullmatch(channel):",
        "return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
        "explicit-version fallback flow",
    )


def run_checker(workflow_path: Path, install_zig_path: Path) -> None:
    check_workflow(workflow_path.read_text(encoding="utf-8"))
    check_install_zig(install_zig_path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def good_workflow_text() -> str:
    return """name: zigux-bootstrap
on:
  pull_request:
    paths:
      - 'scripts/zigux/**'
      - 'third_party/**'
      - '.github/workflows/zigux-bootstrap.yml'
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: echo setup
      - name: Self-test current Lane 05 local-first archive checker
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
      - name: Check current Lane 05 local-first archive packet
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
      - name: Self-test current Lane 05 local archive README checker
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test
      - name: Check current Lane 05 local archive README packet
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
      - name: Self-test current Zig installer helper
        run: python3 scripts/zigux/install-zig.py --self-test
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""


def good_install_zig_text() -> str:
    return """parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')
parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')
if args.self_test:
    return run_self_test()
if args.resolve_only:
    print('ZIG_INSTALL_STATUS=resolved')
    return 0
if entry is None and VERSION_KEY_RE.fullmatch(channel):
    return target_key, channel, infer_tarball_url(channel, target_key, system_key)
if '-dev.' in channel:
    return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'
return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'
assert load_index('0.17.0-dev.87+9b177a7d2') == {}
raise AssertionError('expected non-explicit channel timeout to fail')
print('ZIG_INSTALL_STATUS=pass')
"""


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_install_zig_bootstrap_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_text(root / WORKFLOW_PATH, good_workflow_text())
            write_text(root / INSTALL_ZIG_PATH, good_install_zig_text())
            run_checker(root / WORKFLOW_PATH, root / INSTALL_ZIG_PATH)
            case_count += 1

    def expect_failure(
        workflow_text: str,
        install_zig_text: str,
        expected_substring: str,
    ) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_install_zig_bootstrap_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_text(root / WORKFLOW_PATH, workflow_text)
            write_text(root / INSTALL_ZIG_PATH, install_zig_text)
            try:
                run_checker(root / WORKFLOW_PATH, root / INSTALL_ZIG_PATH)
            except SystemExit as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    workflow_text = good_workflow_text()
    install_zig_text = good_install_zig_text()

    expect_pass()
    expect_failure(
        workflow_text.replace(
            "      - name: Self-test current Zig installer helper\n"
            "        run: python3 scripts/zigux/install-zig.py --self-test\n",
            "",
            1,
        ),
        install_zig_text,
        "Self-test current Zig installer helper",
    )
    expect_failure(
        workflow_text.replace(
            "      - 'third_party/**'\n",
            "",
            1,
        ),
        install_zig_text,
        "third_party/**",
    )
    expect_failure(
        workflow_text.replace(
            "      - name: Check current Lane 05 local archive README packet\n"
            "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py\n"
            "      - name: Self-test current Zig installer helper\n"
            "        run: python3 scripts/zigux/install-zig.py --self-test\n",
            "      - name: Self-test current Zig installer helper\n"
            "        run: python3 scripts/zigux/install-zig.py --self-test\n"
            "      - name: Check current Lane 05 local archive README packet\n"
            "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py\n",
            1,
        ),
        install_zig_text,
        "workflow step order",
    )
    expect_failure(
        workflow_text,
        install_zig_text.replace(
            "parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')\n",
            "",
            1,
        ),
        "resolve-only",
    )
    expect_failure(
        workflow_text,
        install_zig_text.replace(
            "print('ZIG_INSTALL_STATUS=resolved')\n",
            "",
            1,
        ),
        "ZIG_INSTALL_STATUS=resolved",
    )
    expect_failure(
        workflow_text,
        install_zig_text.replace(
            "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'\n",
            "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'\n",
            1,
        ),
        "builds/zig-",
    )
    expect_failure(
        workflow_text,
        install_zig_text.replace(
            "assert load_index('0.17.0-dev.87+9b177a7d2') == {}\n",
            "",
            1,
        ),
        "load_index('0.17.0-dev.87+9b177a7d2') == {}",
    )

    print("LANE05_INSTALL_ZIG_BOOTSTRAP_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_BOOTSTRAP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap wiring keeps the install-zig helper contract visible."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    parser.add_argument(
        "--install-zig",
        type=Path,
        default=INSTALL_ZIG_PATH,
        help="Path to scripts/zigux/install-zig.py",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    run_checker(args.workflow, args.install_zig)
    print("LANE05_INSTALL_ZIG_BOOTSTRAP=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
