#!/usr/bin/env python3
"""Guard the current Lane 03 Zig toolchain resolution packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CHECKER = Path("scripts/zigux/check-zig-toolchain.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_PATHS = (CHECKER, WORKFLOW, MAKEFILE)

CHECKER_MARKERS = (
    "def iter_zig_search_roots(",
    'add_search_root(root / ".zig-toolchain")',
    'add_search_root(root / "toolchains")',
    'add_search_root(root / ".toolchains")',
    'add_search_root(parent / ".toolchains")',
    'add_search_root(parent / "toolchains")',
    "def normalize_explicit_zig_path(",
    "if normalized.is_dir():",
    "def iter_repo_local_zig_candidates(",
    'pinned_dirname = f"zig-x86_64-linux-{pinned_channel}"',
    "add_candidate_roots(base / pinned_dirname)",
    "def resolve_zig_executable(",
    "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
    'return which("zig")',
    'print(f"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}")',
)

WORKFLOW_MARKERS = (
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    'zig_path="$extract_root/zig"',
    'echo "$extract_root" >> "$GITHUB_PATH"',
    '"$zig_path" version',
)

MAKEFILE_MARKERS = (
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
)

EXPECTED_SELF_TEST_CASE_COUNT = 9


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


def duplicate_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, f"{marker}\n{marker}", 1)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def swap_once(text: str, first: str, second: str) -> str:
    if first not in text or second not in text:
        raise AssertionError("swap markers not found")
    placeholder = "__zigux_lane03_resolution_swap__"
    text = text.replace(first, placeholder, 1)
    text = text.replace(second, first, 1)
    return text.replace(placeholder, second, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_order_issue(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    indices: list[int] = []
    for marker in markers:
        index = text.find(marker)
        if index < 0:
            return []
        indices.append(index)
    if indices != sorted(indices):
        return [(code, " -> ".join(markers))]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not resolve_path(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel.as_posix()))
    if issues:
        return issues

    checker_text = read_text(root, CHECKER)
    for marker in CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKER", marker))

    workflow_text = read_text(root, WORKFLOW)
    for marker in WORKFLOW_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_MARKER", f"{marker}:count={count}"))
    issues.extend(collect_order_issue(workflow_text, WORKFLOW_MARKERS, "WORKFLOW_ORDER_DRIFT"))
    zig_verify_marker = 'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then'
    zig_verify_count = workflow_text.count(zig_verify_marker)
    if zig_verify_count != 2:
        issues.append(("INVALID_WORKFLOW_ZIG_VERIFY_COUNT", str(zig_verify_count)))

    makefile_text = read_text(root, MAKEFILE)
    for marker in MAKEFILE_MARKERS:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_MARKER", f"{marker}:count={count}"))
    issues.extend(collect_order_issue(makefile_text, MAKEFILE_MARKERS, "MAKEFILE_ORDER_DRIFT"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        CHECKER,
        "\n".join(
            (
                "def iter_zig_search_roots(root=ROOT):",
                '    add_search_root(root / ".zig-toolchain")',
                '    add_search_root(root / "toolchains")',
                '    add_search_root(root / ".toolchains")',
                '    add_search_root(parent / ".toolchains")',
                '    add_search_root(parent / "toolchains")',
                "",
                "def normalize_explicit_zig_path(explicit_zig):",
                "    normalized = Path(explicit_zig).expanduser()",
                "    if normalized.is_dir():",
                '        raise ValueError("explicit zig path is a directory, expected an executable file")',
                "",
                "def iter_repo_local_zig_candidates(*, root=ROOT, pinned_channel=None):",
                '    pinned_dirname = f"zig-x86_64-linux-{pinned_channel}"',
                "    add_candidate_roots(base / pinned_dirname)",
                "",
                "def resolve_zig_executable(explicit_zig=None, *, root=ROOT, policy_path=TOOLCHAIN_POLICY, which=shutil.which):",
                "    for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
                '        return which("zig")',
                "",
                'print(f"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}")',
            )
        )
        + "\n",
    )
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
                '          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
                '          zig_path="$extract_root/zig"',
                '          if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
                "            return 0",
                "          fi",
                '          if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
                "            return 0",
                "          fi",
                '          echo "$extract_root" >> "$GITHUB_PATH"',
                '          "$zig_path" version',
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(MAKEFILE_MARKERS) + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_zig_resolution_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        resolve_path(root, CHECKER).unlink()
        assert ("MISSING_REQUIRED_PATH", CHECKER.as_posix()) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = resolve_path(root, CHECKER)
        checker_path.write_text(replace_once(checker_path.read_text(encoding="utf-8"), CHECKER_MARKERS[4]), encoding="utf-8")
        assert ("MISSING_CHECKER_MARKER", CHECKER_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(replace_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_MARKERS[3]), encoding="utf-8")
        assert ("MISSING_WORKFLOW_MARKER", WORKFLOW_MARKERS[3]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(duplicate_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_MARKERS[1]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_MARKER", f"{WORKFLOW_MARKERS[1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(replace_once(workflow_path.read_text(encoding="utf-8"), 'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then'), encoding="utf-8")
        assert ("INVALID_WORKFLOW_ZIG_VERIFY_COUNT", "1") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(replace_once(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[5]), encoding="utf-8")
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_MARKERS[5]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(swap_once(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[4], MAKEFILE_MARKERS[5]), encoding="utf-8")
        assert any(code == "MAKEFILE_ORDER_DRIFT" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(swap_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_MARKERS[2], WORKFLOW_MARKERS[3]), encoding="utf-8")
        assert any(code == "WORKFLOW_ORDER_DRIFT" for code, _ in collect_issues(root))
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 Zig toolchain resolution packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print("PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_CHECKER_MARKER_COUNT={len(CHECKER_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_ZIG_RESOLUTION_PACKET_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
