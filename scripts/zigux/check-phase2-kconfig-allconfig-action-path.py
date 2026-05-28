#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
PHASE2_VALIDATE = "scripts/zigux/validate-phase2.py"
PHASE2_CLOSURE_VALIDATE = "scripts/zigux/validate-phase2-closure.py"
PHASE2_TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"
HELPER_PACKET = "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py"

VALIDATE_MARKERS = (
    f"\"{HELPER_PACKET}\",",
    f"\"run: python3 {HELPER_PACKET} --self-test\",",
    f"\"run: python3 {HELPER_PACKET}\",",
    f"\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test\",",
    f"\"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py\",",
)

CLOSURE_VALIDATE_MARKERS = (
    f"\"`{HELPER_PACKET}`\",",
    f"KCONFIG_ALLCONFIG_HELPER_PACKET_REL = Path(\"{HELPER_PACKET}\")",
)

TOOL_MANIFEST_MARKERS = (
    f"\"{HELPER_PACKET}\"",
)

WORKFLOW_MARKERS = (
    f"run: python3 {HELPER_PACKET} --self-test",
    f"run: python3 {HELPER_PACKET}",
)

MAKEFILE_MARKERS = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_marker_issues(
    path: Path, display_path: str, markers: tuple[str, ...], issue_code: str
) -> list[tuple[str, str]]:
    text = read_text(path)
    lines = set(text.splitlines())
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in lines:
            issues.append((issue_code, f"{display_path}::{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    helper_path = root / HELPER_PACKET
    if not helper_path.exists():
        issues.append(("MISSING_HELPER_PACKET", HELPER_PACKET))

    issues.extend(
        collect_marker_issues(
            root / PHASE2_VALIDATE,
            PHASE2_VALIDATE,
            VALIDATE_MARKERS,
            "MISSING_VALIDATE_MARKER",
        )
    )
    issues.extend(
        collect_marker_issues(
            root / PHASE2_CLOSURE_VALIDATE,
            PHASE2_CLOSURE_VALIDATE,
            CLOSURE_VALIDATE_MARKERS,
            "MISSING_CLOSURE_VALIDATE_MARKER",
        )
    )
    issues.extend(
        collect_marker_issues(
            root / PHASE2_TOOL_MANIFEST,
            PHASE2_TOOL_MANIFEST,
            TOOL_MANIFEST_MARKERS,
            "MISSING_TOOL_MANIFEST_MARKER",
        )
    )
    issues.extend(collect_marker_issues(root / WORKFLOW, WORKFLOW, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKER"))
    issues.extend(collect_marker_issues(root / MAKEFILE, MAKEFILE, MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKER"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_fixture_tree(root: Path) -> None:
    write_text(root / HELPER_PACKET, "# helper present\n")
    write_text(root / PHASE2_VALIDATE, "\n".join(VALIDATE_MARKERS) + "\n")
    write_text(root / PHASE2_CLOSURE_VALIDATE, "\n".join(CLOSURE_VALIDATE_MARKERS) + "\n")
    write_text(root / PHASE2_TOOL_MANIFEST, "\n".join(TOOL_MANIFEST_MARKERS) + "\n")
    write_text(root / WORKFLOW, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root / MAKEFILE, "\n".join(MAKEFILE_MARKERS) + "\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def run_self_test() -> int:
    expected_case_count = (
        1
        + 1
        + len(VALIDATE_MARKERS)
        + len(CLOSURE_VALIDATE_MARKERS)
        + len(TOOL_MANIFEST_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(MAKEFILE_MARKERS)
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_allconfig_action_path_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        assert collect_issues(root) == []
        checks += 1

        build_fixture_tree(root)
        (root / HELPER_PACKET).unlink()
        expect_issue(root, ("MISSING_HELPER_PACKET", HELPER_PACKET))
        checks += 1

        for marker in VALIDATE_MARKERS:
            build_fixture_tree(root)
            write_text(
                root / PHASE2_VALIDATE,
                replace_exact_line(read_text(root / PHASE2_VALIDATE), marker, "\"placeholder\""),
            )
            expect_issue(root, ("MISSING_VALIDATE_MARKER", f"{PHASE2_VALIDATE}::{marker}"))
            checks += 1

        for marker in CLOSURE_VALIDATE_MARKERS:
            build_fixture_tree(root)
            write_text(
                root / PHASE2_CLOSURE_VALIDATE,
                replace_exact_line(read_text(root / PHASE2_CLOSURE_VALIDATE), marker, "placeholder"),
            )
            expect_issue(root, ("MISSING_CLOSURE_VALIDATE_MARKER", f"{PHASE2_CLOSURE_VALIDATE}::{marker}"))
            checks += 1

        for marker in TOOL_MANIFEST_MARKERS:
            build_fixture_tree(root)
            write_text(
                root / PHASE2_TOOL_MANIFEST,
                replace_exact_line(read_text(root / PHASE2_TOOL_MANIFEST), marker, "\"placeholder\""),
            )
            expect_issue(root, ("MISSING_TOOL_MANIFEST_MARKER", f"{PHASE2_TOOL_MANIFEST}::{marker}"))
            checks += 1

        for marker in WORKFLOW_MARKERS:
            build_fixture_tree(root)
            write_text(root / WORKFLOW, replace_exact_line(read_text(root / WORKFLOW), marker, "placeholder"))
            expect_issue(root, ("MISSING_WORKFLOW_MARKER", f"{WORKFLOW}::{marker}"))
            checks += 1

        for marker in MAKEFILE_MARKERS:
            build_fixture_tree(root)
            write_text(root / MAKEFILE, replace_exact_line(read_text(root / MAKEFILE), marker, "placeholder"))
            expect_issue(root, ("MISSING_MAKEFILE_MARKER", f"{MAKEFILE}::{marker}"))
            checks += 1

    assert checks == expected_case_count
    print("PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 kconfig allconfig helper packet stays wired through the shared validators, manifest, workflow, and Makefile routes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH=pass")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_VALIDATE_MARKER_COUNT={len(VALIDATE_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALLCONFIG_ACTION_PATH_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
