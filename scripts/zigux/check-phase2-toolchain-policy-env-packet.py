#!/usr/bin/env python3
"""Guard the Lane 03 pinned-toolchain policy-to-environment packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

ORDERED_MARKERS = (
    'eval "$(python3 - <<\\\'PY\\\'",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'if len(targets) != 1:',
    'raise SystemExit(f"expected exactly one pinned archive target, got {len(targets)}")',
    'target = targets[0]',
    'channel = policy["channel"]',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
    'print(f"ZIGUX_ZIG_CHANNEL=\'{channel}\'")',
    'print(f"ZIGUX_ZIG_FILENAME=\'{filename}\'")',
    'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
    "PY",
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'if try_download "$ZIGUX_ZIG_URL"; then',
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


def resolve_path(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(root: Path, rel: Path) -> str:
    path = resolve_path(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = resolve_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)

    for marker in ORDERED_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_POLICY_ENV_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_POLICY_ENV_MARKER", f"{marker}:count={count}"))

    if not issues:
        indices = find_exact_line_indices(workflow_text, ORDERED_MARKERS)
        if indices != sorted(indices):
            issues.append(("OUT_OF_ORDER_POLICY_ENV_MARKER", " -> ".join(ORDERED_MARKERS)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_POLICY_ENV_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "        run: |",
                "          set -euxo pipefail",
                f"          {ORDERED_MARKERS[0]}",
                "          import json",
                "          from pathlib import Path",
                f"          {ORDERED_MARKERS[1]}",
                f"          {ORDERED_MARKERS[2]}",
                f"          {ORDERED_MARKERS[3]}",
                f"              {ORDERED_MARKERS[4]}",
                f"          {ORDERED_MARKERS[5]}",
                f"          {ORDERED_MARKERS[6]}",
                f"          {ORDERED_MARKERS[7]}",
                f"          {ORDERED_MARKERS[8]}",
                f"          {ORDERED_MARKERS[9]}",
                f"          {ORDERED_MARKERS[10]}",
                f"          {ORDERED_MARKERS[11]}",
                f"          {ORDERED_MARKERS[12]}",
                f"          {ORDERED_MARKERS[13]}",
                '          )"',
                "          mkdir -p .zig-toolchain",
                f"          {ORDERED_MARKERS[14]}",
                f"          {ORDERED_MARKERS[15]}",
                '          mirror_file=".zig-toolchain/community-mirrors.txt"',
                f"          {ORDERED_MARKERS[16]}",
                '          repo_archive_parts_dir="${repo_archive_path}.parts"',
                "          download_success=0",
                f"          {ORDERED_MARKERS[17]}",
                "            download_success=1",
                "          fi",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_policy_env_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[0]))
        assert ("MISSING_POLICY_ENV_MARKER", ORDERED_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[9]))
        assert ("DUPLICATE_POLICY_ENV_MARKER", f"{ORDERED_MARKERS[9]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[4], "raise SystemExit('wrong target count')"))
        assert ("MISSING_POLICY_ENV_MARKER", ORDERED_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[12], 'print(f"ZIGUX_ZIG_URL={url}")'))
        assert ("MISSING_POLICY_ENV_MARKER", ORDERED_MARKERS[12]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[16], 'repo_archive_path="third_party/archive.tar.xz"'))
        assert ("MISSING_POLICY_ENV_MARKER", ORDERED_MARKERS[16]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), ORDERED_MARKERS[5], ORDERED_MARKERS[6]))
        assert any(code == "OUT_OF_ORDER_POLICY_ENV_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), ORDERED_MARKERS[14], ORDERED_MARKERS[15]))
        assert any(code == "OUT_OF_ORDER_POLICY_ENV_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), ORDERED_MARKERS[17]))
        assert ("DUPLICATE_POLICY_ENV_MARKER", f"{ORDERED_MARKERS[17]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing workflow did not abort")

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("PHASE2_TOOLCHAIN_POLICY_ENV_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_POLICY_ENV_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 pinned-toolchain workflow keeps the policy-to-environment export packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print("PHASE2_TOOLCHAIN_POLICY_ENV_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_TOOLCHAIN_POLICY_ENV_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_POLICY_ENV_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_POLICY_ENV_PACKET_MARKER_COUNT={len(ORDERED_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_POLICY_ENV_PACKET_WORKFLOW_PATH={args.root.resolve() / WORKFLOW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
