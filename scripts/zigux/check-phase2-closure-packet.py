#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_NOTE_MARKERS = (
    "# Phase 2 Closure",
    "This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, installer, cross-route, kconfig-bridge, genksyms bridge, fixdep, make-wrapper, manifest-guard, and validator surfaces on current `master`.",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`PHASE2_CURRENT_CLOSURE_PACKET=",
    "`PHASE2_CURRENT_GAP_PACKET=`",
    "`python3 scripts/zigux/validate-phase2.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`PHASE2_CLOSURE_VALIDATORS=",
    "`PHASE2_SHARED_MAKE_ROUTES=",
    "`PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again; if the shared backlog reopens first, start with one smallest truthfulness repair in Documentation/zigux/README.md, zigux/tests/README.md, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes`",
)

EXACT_COUNT_NOTE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`python3 scripts/zigux/validate-phase2.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

FORBIDDEN_NOTE_MARKERS = (
    "missing installer or direct cross-route proof text",
    "older validator-first-only Phase 2 names",
    "repo-reality-gap bucket",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_MANIFEST_SURFACES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/fixdep.zig",
    "third_party/README.md",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(REQUIRED_NOTE_MARKERS)
    + len(EXACT_COUNT_NOTE_MARKERS)
    + len(FORBIDDEN_NOTE_MARKERS)
    + len(REQUIRED_WORKFLOW_LINES)
    + len(REQUIRED_MAKEFILE_LINES)
    + len(REQUIRED_MANIFEST_SURFACES)
    + 6
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"required file unreadable: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        values: set[str] = set()
        for item in value:
            values.update(collect_strings(item))
        return values
    if isinstance(value, dict):
        values: set[str] = set()
        for item in value.values():
            values.update(collect_strings(item))
        return values
    return set()


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    note_text = read_text(resolve(root, NOTE_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest_strings = collect_strings(read_manifest(resolve(root, MANIFEST_REL)))

    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))

    for marker in EXACT_COUNT_NOTE_MARKERS:
        count = note_text.count(marker)
        if count != 1:
            issues.append(("EXACT_COUNT_NOTE_MARKER", f"{count}::{marker}"))

    for marker in FORBIDDEN_NOTE_MARKERS:
        if marker in note_text:
            issues.append(("FORBIDDEN_NOTE_MARKER", marker))

    workflow_lines = set(workflow_text.splitlines())
    for marker in REQUIRED_WORKFLOW_LINES:
        if marker not in workflow_lines:
            issues.append(("MISSING_WORKFLOW_LINE", marker))

    makefile_lines = set(makefile_text.splitlines())
    for marker in REQUIRED_MAKEFILE_LINES:
        if marker not in makefile_lines:
            issues.append(("MISSING_MAKEFILE_LINE", marker))

    for marker in REQUIRED_MANIFEST_SURFACES:
        if marker not in manifest_strings:
            issues.append(("MISSING_MANIFEST_SURFACE", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def emit_note(note: str) -> int:
    print("PHASE2_CLOSURE_PACKET=fail")
    print(f"PHASE2_CLOSURE_PACKET_NOTE={note}")
    return 1


def run_checker(root: Path) -> int:
    try:
        issues = collect_issues(root)
    except SystemExit as exc:
        return emit_note(str(exc))

    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_PACKET=pass")
    print(f"PHASE2_CLOSURE_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    print(f"PHASE2_CLOSURE_PACKET_EXACT_COUNT_MARKER_COUNT={len(EXACT_COUNT_NOTE_MARKERS)}")
    print(f"PHASE2_CLOSURE_PACKET_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_NOTE_MARKERS)}")
    print(f"PHASE2_CLOSURE_PACKET_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CLOSURE_PACKET_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_CLOSURE_PACKET_MANIFEST_SURFACE_COUNT={len(REQUIRED_MANIFEST_SURFACES)}")
    return 0


def capture_run_checker(root: Path) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        result = run_checker(root)
    return result, stdout.getvalue()


def build_self_test_root(root: Path) -> None:
    write_text(resolve(root, NOTE_REL), "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES_REL), "present\n")
    write_text(resolve(root, VALIDATE_REL), "present\n")
    write_text(resolve(root, CLOSURE_VALIDATE_REL), "present\n")
    write_text(resolve(root, WORKFLOW_REL), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(
        resolve(root, MAKEFILE_REL),
        "\n".join(
            (
                "PYTHON ?= python3",
                "ZIG ?= zig",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "ZIGUX_ROOT := ..",
                *REQUIRED_MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, MANIFEST_REL),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {"all": list(REQUIRED_MANIFEST_SURFACES)},
                "repo_reality_gaps": [],
                "notes": ["present"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE_REL)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in EXACT_COUNT_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE_REL)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("EXACT_COUNT_NOTE_MARKER", f"2::{marker}") in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve(root, NOTE_REL)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve(root, WORKFLOW_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve(root, MAKEFILE_REL)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MANIFEST_SURFACES:
            build_self_test_root(root)
            path = resolve(root, MANIFEST_REL)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["present_surfaces"]["all"].remove(marker)
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_SURFACE", marker) in collect_issues(root)
            checks_run += 1

        for rel, expected_fragment in (
            (NOTE_REL, "required file missing:"),
            (WORKFLOW_REL, "required file missing:"),
            (MAKEFILE_REL, "required file missing:"),
        ):
            build_self_test_root(root)
            resolve(root, rel).unlink()
            result, output = capture_run_checker(root)
            assert result == 1, output
            assert f"PHASE2_CLOSURE_PACKET_NOTE={expected_fragment}" in output, output
            checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        path.write_text("{\n", encoding="utf-8")
        result, output = capture_run_checker(root)
        assert result == 1, output
        assert "PHASE2_CLOSURE_PACKET_NOTE=required json invalid:" in output, output
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        path.write_text("[]\n", encoding="utf-8")
        result, output = capture_run_checker(root)
        assert result == 1, output
        assert "PHASE2_CLOSURE_PACKET_NOTE=required json has invalid top-level shape:" in output, output
        checks_run += 1

        build_self_test_root(root)
        result, output = capture_run_checker(root)
        assert result == 0, output
        assert "PHASE2_CLOSURE_PACKET=pass" in output, output
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, checks_run
    print("PHASE2_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note aligned with the shipped closure packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_checker(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
