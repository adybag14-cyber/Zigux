#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 community-mirror fallback packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPT_PATH = Path("scripts/zigux/check-lane05-community-mirror-fallback.py")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
TOOLCHAIN_CHECKER_PATH = Path("scripts/zigux/check-zig-toolchain.py")

SELF_TEST_STEP = "- name: Self-test current Lane 05 community-mirror fallback checker"
SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-community-mirror-fallback.py --self-test"
)
CHECK_STEP = "- name: Check current Lane 05 community-mirror fallback packet"
CHECK_CMD = "python3 scripts/zigux/check-lane05-community-mirror-fallback.py"

MIRROR_MARKERS = (
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'rm -f "$archive_path" "$mirror_file"',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    "while IFS= read -r mirror_url; do",
    '[ -n "$mirror_url" ] || continue',
    'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
    "download_success=1",
    "break",
    'done < "$mirror_file"',
)

ORDER_PAIRS = (
    (
        'mirror_file=".zig-toolchain/community-mirrors.txt"',
        'rm -f "$archive_path" "$mirror_file"',
        "mirror cleanup setup",
    ),
    (
        'rm -f "$archive_path" "$mirror_file"',
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        "mirror fetch after startup cleanup",
    ),
    (
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        "while IFS= read -r mirror_url; do",
        "mirror fetch before mirror iteration",
    ),
    (
        "while IFS= read -r mirror_url; do",
        '[ -n "$mirror_url" ] || continue',
        "blank-line skip inside mirror loop",
    ),
    (
        '[ -n "$mirror_url" ] || continue',
        'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
        "blank-line skip before mirror download attempt",
    ),
    (
        'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
        "break",
        "mirror success break",
    ),
    (
        "break",
        'done < "$mirror_file"',
        "mirror loop closes after success break",
    ),
    (
        'done < "$mirror_file"',
        'if try_download "$ZIGUX_ZIG_URL"; then',
        "direct download remains the last fallback",
    ),
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 community-mirror fallback missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 community-mirror fallback expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            "lane05 community-mirror fallback expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 community-mirror fallback missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 community-mirror fallback expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_required_files(root: Path) -> None:
    for relative_path in (WORKFLOW_PATH, TOOLCHAIN_CHECKER_PATH, POLICY_PATH):
        if not (root / relative_path).is_file():
            raise SystemExit(
                "lane05 community-mirror fallback missing required file: "
                f"{relative_path.as_posix()}"
            )


def check_workflow(text: str) -> None:
    for marker in MIRROR_MARKERS:
        require_marker(text, marker, "workflow mirror marker")

    require_marker(
        text,
        'if try_download "$ZIGUX_ZIG_URL"; then',
        "workflow direct-download fallback marker",
    )
    require_marker(text, SELF_TEST_STEP, "workflow checker self-test step name")
    require_marker(text, SELF_TEST_CMD, "workflow checker self-test command")
    require_marker(text, CHECK_STEP, "workflow checker step name")
    require_marker(text, CHECK_CMD, "workflow checker command")

    require_exact_count(
        text,
        'mirror_file=".zig-toolchain/community-mirrors.txt"',
        1,
        "mirror-file marker",
    )
    require_exact_count(
        text,
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        1,
        "mirror-fetch marker",
    )
    require_exact_count(text, "while IFS= read -r mirror_url; do", 1, "mirror loop")
    require_exact_count(text, "break", 1, "mirror success break")
    require_exact_count(text, 'done < "$mirror_file"', 1, "mirror loop close")
    require_exact_line_count(
        text,
        f"run: {SELF_TEST_CMD}",
        1,
        "workflow run line",
    )
    require_exact_line_count(
        text,
        f"run: {CHECK_CMD}",
        1,
        "workflow run line",
    )

    for earlier, later, label in ORDER_PAIRS:
        require_order(text, earlier, later, label)


def check_root(root: Path) -> None:
    check_required_files(root)
    workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
    check_workflow(workflow_text)


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / WORKFLOW_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SCRIPT_PATH.parent).mkdir(parents=True, exist_ok=True)

    workflow_text = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          mirror_file=".zig-toolchain/community-mirrors.txt"
          rm -f "$archive_path" "$mirror_file"
          download_success=0
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            while IFS= read -r mirror_url; do
              [ -n "$mirror_url" ] || continue
              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
                download_success=1
                break
              fi
            done < "$mirror_file"
          fi
          if [ "$download_success" -ne 1 ]; then
            if try_download "$ZIGUX_ZIG_URL"; then
              download_success=1
            fi
          fi
      - name: Self-test current Lane 05 community-mirror fallback checker
        run: python3 scripts/zigux/check-lane05-community-mirror-fallback.py --self-test
      - name: Check current Lane 05 community-mirror fallback packet
        run: python3 scripts/zigux/check-lane05-community-mirror-fallback.py
"""
    (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
    (root / TOOLCHAIN_CHECKER_PATH).write_text(
        "# current toolchain checker companion placeholder\n",
        encoding="utf-8",
    )
    (root / POLICY_PATH).write_text(
        '{\n  "channel": "0.17.0-dev.87+9b177a7d2"\n}\n',
        encoding="utf-8",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          mirror_file=".zig-toolchain/community-mirrors.txt"
          rm -f "$archive_path" "$mirror_file"
          download_success=0
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            while IFS= read -r mirror_url; do
              [ -n "$mirror_url" ] || continue
              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
                download_success=1
                break
              fi
            done < "$mirror_file"
          fi
          if [ "$download_success" -ne 1 ]; then
            if try_download "$ZIGUX_ZIG_URL"; then
              download_success=1
            fi
          fi
      - name: Self-test current Lane 05 community-mirror fallback checker
        run: python3 scripts/zigux/check-lane05-community-mirror-fallback.py --self-test
      - name: Check current Lane 05 community-mirror fallback packet
        run: python3 scripts/zigux/check-lane05-community-mirror-fallback.py
"""
    check_workflow(good_workflow)
    case_count = 1

    missing_mirror_fetch = good_workflow.replace(
        '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n',
        "",
        1,
    )
    try:
        check_workflow(missing_mirror_fetch)
    except SystemExit as exc:
        assert "community-mirrors.txt" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing mirror fetch failure")

    missing_blank_skip = good_workflow.replace(
        '              [ -n "$mirror_url" ] || continue\n',
        "",
        1,
    )
    try:
        check_workflow(missing_blank_skip)
    except SystemExit as exc:
        assert 'mirror_url' in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing blank-line skip failure")

    missing_query_suffix = good_workflow.replace(
        '${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap',
        '${mirror_url%/}/$ZIGUX_ZIG_FILENAME',
        1,
    )
    try:
        check_workflow(missing_query_suffix)
    except SystemExit as exc:
        assert "?source=github-zigux-bootstrap" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing source query failure")

    missing_break = good_workflow.replace("                break\n", "", 1)
    try:
        check_workflow(missing_break)
    except SystemExit as exc:
        assert "mirror success break" in str(exc) or "break" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing break failure")

    direct_before_mirrors = good_workflow.replace(
        '            done < "$mirror_file"\n'
        "          fi\n"
        '          if [ "$download_success" -ne 1 ]; then\n'
        '            if try_download "$ZIGUX_ZIG_URL"; then\n'
        "              download_success=1\n"
        "            fi\n"
        "          fi\n",
        '          if [ "$download_success" -ne 1 ]; then\n'
        '            if try_download "$ZIGUX_ZIG_URL"; then\n'
        "              download_success=1\n"
        "            fi\n"
        "          fi\n"
        '            done < "$mirror_file"\n'
        "          fi\n",
        1,
    )
    try:
        check_workflow(direct_before_mirrors)
    except SystemExit as exc:
        assert "direct download remains the last fallback" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected direct-before-mirrors order failure")

    missing_self_test = good_workflow.replace(
        "      - name: Self-test current Lane 05 community-mirror fallback checker\n"
        "        run: python3 scripts/zigux/check-lane05-community-mirror-fallback.py --self-test\n",
        "",
        1,
    )
    try:
        check_workflow(missing_self_test)
    except SystemExit as exc:
        assert SELF_TEST_STEP in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing self-test step failure")

    missing_check_step = good_workflow.replace(
        "      - name: Check current Lane 05 community-mirror fallback packet\n"
        "        run: python3 scripts/zigux/check-lane05-community-mirror-fallback.py\n",
        "",
        1,
    )
    try:
        check_workflow(missing_check_step)
    except SystemExit as exc:
        assert CHECK_STEP in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing check step failure")

    duplicate_mirror_loop = good_workflow.replace(
        "            while IFS= read -r mirror_url; do\n",
        "            while IFS= read -r mirror_url; do\n"
        "            while IFS= read -r mirror_url; do\n",
        1,
    )
    try:
        check_workflow(duplicate_mirror_loop)
    except SystemExit as exc:
        assert "mirror loop" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate mirror loop failure")

    print("LANE05_COMMUNITY_MIRROR_FALLBACK_SELF_TEST=pass")
    print(f"LANE05_COMMUNITY_MIRROR_FALLBACK_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap keeps the community-mirror fallback packet intact."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"LANE05_COMMUNITY_MIRROR_FALLBACK_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    check_root(args.root)
    print("LANE05_COMMUNITY_MIRROR_FALLBACK=pass")
    print(
        "LANE05_COMMUNITY_MIRROR_FALLBACK_MARKER_COUNT="
        f"{len(MIRROR_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
