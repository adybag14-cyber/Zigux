#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

REQUIRED_POLICY = {
    "phase": "Phase 2",
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": [
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    ],
}

MAKEFILE_VARIABLE_MARKERS = (
    "PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json",
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
)

MAKEFILE_ROUTE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-kconfig: phase2-toolchain",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
)

WORKFLOW_MARKERS = (
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    'echo "$extract_root" >> "$GITHUB_PATH"',
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_zig_executable(",
    "def iter_repo_local_archive_candidates(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    'parser.add_argument("--zig"',
)

SELF_TEST_CASE_COUNT = (
    1
    + len(MAKEFILE_VARIABLE_MARKERS)
    + len(MAKEFILE_VARIABLE_MARKERS)
    + len(MAKEFILE_ROUTE_MARKERS)
    + len(MAKEFILE_ROUTE_MARKERS)
    + len(WORKFLOW_MARKERS)
    + len(WORKFLOW_MARKERS)
    + len(TOOLCHAIN_CHECKER_MARKERS)
    + len(TOOLCHAIN_CHECKER_MARKERS)
    + 3
)


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


def collect_marker_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_policy_issues(path: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(path))
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != REQUIRED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]
    if upgrade_policy.get("archive_target_scope") != REQUIRED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))
    if upgrade_policy.get("required_make_routes") != REQUIRED_POLICY["required_make_routes"]:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    checker_text = read_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT))
    issues: list[tuple[str, str]] = []
    issues.extend(collect_marker_issues(makefile_text, MAKEFILE_VARIABLE_MARKERS, "MISSING_MAKEFILE_VARIABLE", "DUPLICATE_MAKEFILE_VARIABLE"))
    issues.extend(collect_marker_issues(makefile_text, MAKEFILE_ROUTE_MARKERS, "MISSING_MAKEFILE_ROUTE", "DUPLICATE_MAKEFILE_ROUTE"))
    issues.extend(collect_marker_issues(workflow_text, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKER", "DUPLICATE_WORKFLOW_MARKER"))
    issues.extend(collect_marker_issues(checker_text, TOOLCHAIN_CHECKER_MARKERS, "MISSING_TOOLCHAIN_CHECKER_MARKER", "DUPLICATE_TOOLCHAIN_CHECKER_MARKER"))
    issues.extend(collect_policy_issues(root / TOOLCHAIN_POLICY.relative_to(ROOT)))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ZIG_RESOLVER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root / MAKEFILE.relative_to(ROOT),
        "\n".join((
            "PYTHON ?= python3",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "ZIGUX_ROOT := ..",
            *MAKEFILE_VARIABLE_MARKERS,
            "",
            *MAKEFILE_ROUTE_MARKERS,
        )) + "\n",
    )
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT), "\n".join(TOOLCHAIN_CHECKER_MARKERS) + "\n")
    write_text(
        root / TOOLCHAIN_POLICY.relative_to(ROOT),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(REQUIRED_POLICY["required_make_routes"]),
                },
            },
            indent=2,
        ) + "\n",
    )


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_zig_resolver_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in MAKEFILE_VARIABLE_MARKERS:
            build_self_test_root(root)
            write_text(root / MAKEFILE.relative_to(ROOT), replace_exact_line(read_text(root / MAKEFILE.relative_to(ROOT)), marker, "# removed"))
            expect_issue(root, ("MISSING_MAKEFILE_VARIABLE", marker))
            checks += 1

        for marker in MAKEFILE_VARIABLE_MARKERS:
            build_self_test_root(root)
            write_text(root / MAKEFILE.relative_to(ROOT), duplicate_exact_line(read_text(root / MAKEFILE.relative_to(ROOT)), marker))
            expect_issue(root, ("DUPLICATE_MAKEFILE_VARIABLE", f"{marker}:count=2"))
            checks += 1

        for marker in MAKEFILE_ROUTE_MARKERS:
            build_self_test_root(root)
            write_text(root / MAKEFILE.relative_to(ROOT), replace_exact_line(read_text(root / MAKEFILE.relative_to(ROOT)), marker, "# removed"))
            expect_issue(root, ("MISSING_MAKEFILE_ROUTE", marker))
            checks += 1

        for marker in MAKEFILE_ROUTE_MARKERS:
            build_self_test_root(root)
            write_text(root / MAKEFILE.relative_to(ROOT), duplicate_exact_line(read_text(root / MAKEFILE.relative_to(ROOT)), marker))
            expect_issue(root, ("DUPLICATE_MAKEFILE_ROUTE", f"{marker}:count=2"))
            checks += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            write_text(root / WORKFLOW.relative_to(ROOT), read_text(root / WORKFLOW.relative_to(ROOT)).replace(marker, "# removed", 1))
            expect_issue(root, ("MISSING_WORKFLOW_MARKER", marker))
            checks += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            write_text(root / WORKFLOW.relative_to(ROOT), read_text(root / WORKFLOW.relative_to(ROOT)) + marker + "\n")
            expect_issue(root, ("DUPLICATE_WORKFLOW_MARKER", f"{marker}:count=2"))
            checks += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_self_test_root(root)
            write_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT), read_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT)).replace(marker, "# removed", 1))
            expect_issue(root, ("MISSING_TOOLCHAIN_CHECKER_MARKER", marker))
            checks += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_self_test_root(root)
            write_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT), read_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT)) + marker + "\n")
            expect_issue(root, ("DUPLICATE_TOOLCHAIN_CHECKER_MARKER", f"{marker}:count=2"))
            checks += 1

        build_self_test_root(root)
        payload = json.loads(read_text(root / TOOLCHAIN_POLICY.relative_to(ROOT)))
        payload["phase"] = "Phase 3"
        write_text(root / TOOLCHAIN_POLICY.relative_to(ROOT), json.dumps(payload, indent=2) + "\n")
        expect_issue(root, ("POLICY_PHASE_MISMATCH", repr("Phase 3")))
        checks += 1

        build_self_test_root(root)
        payload = json.loads(read_text(root / TOOLCHAIN_POLICY.relative_to(ROOT)))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        write_text(root / TOOLCHAIN_POLICY.relative_to(ROOT), json.dumps(payload, indent=2) + "\n")
        expect_issue(root, ("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(["aarch64-linux"])))
        checks += 1

        build_self_test_root(root)
        payload = json.loads(read_text(root / TOOLCHAIN_POLICY.relative_to(ROOT)))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_text(root / TOOLCHAIN_POLICY.relative_to(ROOT), json.dumps(payload, indent=2) + "\n")
        expect_issue(root, ("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(["phase2-toolchain"])))
        checks += 1

    assert checks == SELF_TEST_CASE_COUNT
    print("PHASE2_ZIG_RESOLVER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_ZIG_RESOLVER_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard the current Phase 2 pinned-Zig resolver packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ZIG_RESOLVER_PACKET=pass")
    print(f"PHASE2_ZIG_RESOLVER_PACKET_MAKEFILE_VARIABLE_COUNT={len(MAKEFILE_VARIABLE_MARKERS)}")
    print(f"PHASE2_ZIG_RESOLVER_PACKET_ROUTE_MARKER_COUNT={len(MAKEFILE_ROUTE_MARKERS)}")
    print(f"PHASE2_ZIG_RESOLVER_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
