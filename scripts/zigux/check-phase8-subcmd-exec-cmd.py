#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "lib" / "subcmd" / "exec-cmd.zig"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase8_subcmd_exec_cmd_manifest.json"

REQUIRED_ANCHORS = [
    "systemPath and getArgvExecPath preserve C-style precedence",
    "EnvMap owns inserted keys so later caller mutations cannot corrupt lookups",
    "extractArgv0Path splits command names from directory prefixes",
    "buildSearchPath rewrites relative entries against the working directory",
    "buildSearchPath preserves root-cwd doubled slashes used by the C helper",
    "buildSearchPath skips rooted argv0 empty directories when assembling PATH",
    "setupPath preserves the inherited exec-path string while normalizing PATH entries",
    "setupPathWithPwd keeps logical PWD when identity matches",
    "setupPathWithPwd falls back to cwd when logical PWD identity does not match",
    "setupPathWithPwd falls back to cwd when logical PWD identity is unavailable",
    "setupPathWithPwd ignores an explicitly empty logical PWD even when identity matches",
    "prepareExecCmd prepends the configured executable name and preserves a trailing null slot",
    "collectExeclArgs keeps the command head and first null terminator",
    "collectExeclArgs rejects a tail that never terminates with null",
    "collectExeclArgs rejects a null terminator that lands in MAX_ARGS",
    "buildDeferredExeclCall keeps the execl handoff pure and launch-free",
]

REQUIRED_API_SURFACE = [
    "systemPath",
    "getArgvExecPath",
    "buildSearchPath",
    "setupPath",
    "setupPathWithPwd",
    "prepareExecCmd",
    "collectExeclArgs",
    "buildDeferredExeclCall",
    "buildDeferredExecvCall",
]

REQUIRED_HANDOFF_FOCUS = [
    "exec-path precedence stays explicit-over-env-over-prefix",
    "PATH assembly keeps rooted and relative segments aligned with the C helper",
    "logical PWD handoff only wins when file identity matches",
    "execv and execl handoff packets preserve argv order and trailing null behavior",
    "execl argument collection rejects unterminated or over-capacity tails",
]

EXPECTED_SELF_TEST_CASE_COUNT = 6


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("zig")
    if found:
        return found
    raise SystemExit("zig not found; pass --zig")


def read_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_test_anchors(source_text: str) -> list[str]:
    return re.findall(r'^test "([^"]+)" \{$', source_text, re.M)


def collect_public_symbols(source_text: str) -> list[str]:
    return re.findall(r"^pub (?:fn|const) ([A-Za-z_][A-Za-z0-9_]*)", source_text, re.M)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    source_text = (root / SOURCE.relative_to(ROOT)).read_text(encoding="utf-8")
    manifest = read_manifest(root / MANIFEST.relative_to(ROOT))
    issues: list[tuple[str, str]] = []

    actual_anchors = collect_test_anchors(source_text)
    actual_symbols = collect_public_symbols(source_text)

    expected_fields: dict[str, object] = {
        "tool": "tools/lib/subcmd/exec-cmd.zig",
        "status": "closed",
        "mode": "bounded exec handoff helper",
        "test_case_count": len(REQUIRED_ANCHORS),
        "helper_api_surface": REQUIRED_API_SURFACE,
        "helper_local_anchors": REQUIRED_ANCHORS,
        "handoff_focus": REQUIRED_HANDOFF_FOCUS,
    }

    for field_name, expected_value in expected_fields.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append((f"MANIFEST_{field_name.upper()}_MISMATCH", f"actual={actual_value!r}:expected={expected_value!r}"))

    if actual_anchors != REQUIRED_ANCHORS:
        issues.append(("SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL", ",".join(actual_anchors)))
        issues.append(("SOURCE_HELPER_LOCAL_ANCHORS_EXPECTED", ",".join(REQUIRED_ANCHORS)))

    for symbol in REQUIRED_API_SURFACE:
        if symbol not in actual_symbols:
            issues.append(("MISSING_REQUIRED_PUBLIC_SYMBOL", symbol))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> None:
    print("PHASE8_SUBCMD_EXEC_CMD_DIFF=fail")
    for code, value in issues:
        print(f"{code}={value}")
    raise SystemExit(1)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_self_test_source() -> str:
    blocks = [f'test "{anchor}" {{\n    try std.testing.expect(true);\n}}\n' for anchor in REQUIRED_ANCHORS]
    return (
        'const std = @import("std");\n\n'
        "pub const max_execl_slots: usize = 32;\n"
        "pub fn systemPath() void {}\n"
        "pub fn getArgvExecPath() void {}\n"
        "pub fn buildSearchPath() void {}\n"
        "pub fn setupPath() void {}\n"
        "pub fn setupPathWithPwd() void {}\n"
        "pub fn prepareExecCmd() void {}\n"
        "pub fn collectExeclArgs() void {}\n"
        "pub fn buildDeferredExeclCall() void {}\n"
        "pub fn buildDeferredExecvCall() void {}\n\n"
        + "\n".join(blocks)
    )


def render_manifest() -> str:
    return json.dumps(
        {
            "tool": "tools/lib/subcmd/exec-cmd.zig",
            "status": "closed",
            "mode": "bounded exec handoff helper",
            "test_case_count": len(REQUIRED_ANCHORS),
            "helper_api_surface": REQUIRED_API_SURFACE,
            "helper_local_anchors": REQUIRED_ANCHORS,
            "handoff_focus": REQUIRED_HANDOFF_FOCUS,
        },
        indent=2,
    ) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(root / "tools" / "lib" / "subcmd" / "exec-cmd.zig", render_self_test_source())
    write_text(root / "zigux" / "tests" / "fixtures" / "phase8_subcmd_exec_cmd_manifest.json", render_manifest())
    write_text(root / "scripts" / "zigux" / "check-phase8-subcmd-exec-cmd.py", "# self-test placeholder\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_exec_cmd_") as tmp_dir_str:
        root = Path(tmp_dir_str)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        source_path = root / "tools" / "lib" / "subcmd" / "exec-cmd.zig"
        write_text(source_path, source_path.read_text(encoding="utf-8").replace(REQUIRED_ANCHORS[0], "drifted anchor", 1))
        assert any(code == "SOURCE_HELPER_LOCAL_ANCHORS_ACTUAL" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / "zigux" / "tests" / "fixtures" / "phase8_subcmd_exec_cmd_manifest.json"
        manifest = read_manifest(manifest_path)
        manifest["test_case_count"] = 7
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "MANIFEST_TEST_CASE_COUNT_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest = read_manifest(manifest_path)
        manifest["helper_api_surface"] = REQUIRED_API_SURFACE[:-1]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "MANIFEST_HELPER_API_SURFACE_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        source_text = source_path.read_text(encoding="utf-8").replace("pub fn buildDeferredExecvCall() void {}\n", "", 1)
        write_text(source_path, source_text)
        assert ("MISSING_REQUIRED_PUBLIC_SYMBOL", "buildDeferredExecvCall") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = read_manifest(manifest_path)
        manifest["handoff_focus"] = REQUIRED_HANDOFF_FOCUS[:-1]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "MANIFEST_HANDOFF_FOCUS_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("PHASE8_SUBCMD_EXEC_CMD_SELF_TEST=fail")
        print(f"PHASE8_SUBCMD_EXEC_CMD_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE8_SUBCMD_EXEC_CMD_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("PHASE8_SUBCMD_EXEC_CMD_SELF_TEST=pass")
    print(f"PHASE8_SUBCMD_EXEC_CMD_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded Phase 8 exec-cmd handoff coverage.")
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(ROOT)
    if issues:
        emit_issues(issues)

    zig = find_zig(args.zig)
    run([zig, "test", str(SOURCE)], cwd=str(ROOT))

    print("PHASE8_SUBCMD_EXEC_CMD_MANIFEST=pass")
    print("PHASE8_SUBCMD_EXEC_CMD_ZIG_TEST=pass")
    print(f"PHASE8_SUBCMD_EXEC_CMD_TEST_COUNT={len(REQUIRED_ANCHORS)}")
    print("PHASE8_SUBCMD_EXEC_CMD_CHECKS_START")
    for anchor in REQUIRED_ANCHORS:
        print(anchor)
    print("PHASE8_SUBCMD_EXEC_CMD_CHECKS_END")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
