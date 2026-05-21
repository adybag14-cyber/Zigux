#!/usr/bin/env python3
"""Guard the current Phase 2 validator-entrypoint packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[0]

VALIDATOR_REL = Path("scripts/zigux/validate-phase2.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
BOOTSTRAP_NOTE_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_VALIDATOR_MARKERS = (
    'WORKFLOW = ".github/workflows/zigux-bootstrap.yml"',
    'MAKEFILE = "zigux/Makefile"',
    'GENKSYMS_VERSION_SIDE_EFFECT_TEST = "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"',
    '"Documentation/zigux/phase2-closure.md",',
    '"Documentation/zigux/phase2-toolchain-bootstrap-notes.md",',
    '"scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"scripts/zigux/check-phase2-fixdep-gate.py",',
    '"scripts/zigux/check-fixdep-diff.py",',
    '"run: python3 scripts/zigux/check-phase2-tool-manifest.py",',
    '"run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",',
    '"run: python3 scripts/zigux/check-phase2-fixdep-gate.py",',
    '"run: python3 scripts/zigux/check-fixdep-diff.py",',
    '"run: make -C zigux phase2-validate",',
    'REQUIRED_PHASE2_PHONY_LINE = ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",',
)

REQUIRED_CLOSURE_NOTE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-validate`",
)

REQUIRED_BOOTSTRAP_NOTE_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `zigux/tests/README.md`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/fixdep/cases.json`, and the `zigux/tests/fixtures/kconfig_bridge/` manifest roster keep the bounded closure-side, closure-validator, validator-entrypoint, tests-facing, tool-manifest, fixture-backed artifact-support, primary artifact-diff helper, fixdep, and bridge packet reviewable without widening back into older validator-first claims.",
    "`scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` are the current shipped Phase 2 reminder, parity, and alignment guards visible on `master`.",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "`python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "`python3 scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-validate`",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

EXPECTED_MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)
EXPECTED_MANIFEST_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)
EXPECTED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)
EXPECTED_MANIFEST_FIXDEP_SUPPORT = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
)
EXPECTED_MANIFEST_ARTIFACT_SUPPORT = (
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)
EXPECTED_MANIFEST_MAKE_WRAPPERS = (
    "make -C zigux phase2-tools",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
)
EXPECTED_MANIFEST_NOTE = (
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and "
    "scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose."
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def load_manifest(path: Path) -> dict:
    return json.loads(read_text(path))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    validator_text = read_text(root / VALIDATOR_REL)
    closure_note_text = read_text(root / CLOSURE_NOTE_REL)
    bootstrap_note_text = read_text(root / BOOTSTRAP_NOTE_REL)
    workflow_text = read_text(root / WORKFLOW_REL)
    makefile_text = read_text(root / MAKEFILE_REL)
    manifest = load_manifest(root / MANIFEST_REL)

    for marker in REQUIRED_VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))

    for marker in REQUIRED_CLOSURE_NOTE_MARKERS:
        if marker not in closure_note_text:
            issues.append(("MISSING_CLOSURE_NOTE_MARKER", marker))

    for marker in REQUIRED_BOOTSTRAP_NOTE_MARKERS:
        if marker not in bootstrap_note_text:
            issues.append(("MISSING_BOOTSTRAP_NOTE_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces"))
        return issues

    validators = present_surfaces.get("validators")
    if not isinstance(validators, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.validators"))
    else:
        for marker in EXPECTED_MANIFEST_VALIDATORS:
            if marker not in validators:
                issues.append(("MISSING_MANIFEST_VALIDATOR", marker))

    closure_notes = present_surfaces.get("closure_notes")
    if not isinstance(closure_notes, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.closure_notes"))
    else:
        for marker in EXPECTED_MANIFEST_CLOSURE_NOTES:
            if marker not in closure_notes:
                issues.append(("MISSING_MANIFEST_CLOSURE_NOTE", marker))

    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.checkers"))
    else:
        for marker in EXPECTED_MANIFEST_CHECKERS:
            if marker not in checkers:
                issues.append(("MISSING_MANIFEST_CHECKER", marker))

    artifact_support = present_surfaces.get("artifact_support")
    if not isinstance(artifact_support, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.artifact_support"))
    else:
        for marker in EXPECTED_MANIFEST_ARTIFACT_SUPPORT:
            if marker not in artifact_support:
                issues.append(("MISSING_MANIFEST_ARTIFACT_SUPPORT", marker))

    fixdep_support = present_surfaces.get("fixdep_support")
    if not isinstance(fixdep_support, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.fixdep_support"))
    else:
        for marker in EXPECTED_MANIFEST_FIXDEP_SUPPORT:
            if marker not in fixdep_support:
                issues.append(("MISSING_MANIFEST_FIXDEP_SUPPORT", marker))

    make_wrappers = present_surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.make_wrappers"))
    else:
        for marker in EXPECTED_MANIFEST_MAKE_WRAPPERS:
            if marker not in make_wrappers:
                issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", marker))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_MANIFEST_SECTION", "notes"))
    elif EXPECTED_MANIFEST_NOTE not in notes:
        issues.append(("MISSING_MANIFEST_NOTE", EXPECTED_MANIFEST_NOTE))

    return issues


def run_checker(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE2_VALIDATOR_ENTRYPOINT_PACKET=fail")
        for code, detail in issues:
            print(f"PHASE2_VALIDATOR_ENTRYPOINT_PACKET_ISSUE={code}:{detail}")
        return 1

    print("PHASE2_VALIDATOR_ENTRYPOINT_PACKET=pass")
    return 0


def build_sample_root(root: Path) -> None:
    write_text(root / VALIDATOR_REL, "\n".join(REQUIRED_VALIDATOR_MARKERS) + "\n")
    write_text(root / CLOSURE_NOTE_REL, "\n".join(REQUIRED_CLOSURE_NOTE_MARKERS) + "\n")
    write_text(root / BOOTSTRAP_NOTE_REL, "\n".join(REQUIRED_BOOTSTRAP_NOTE_MARKERS) + "\n")
    write_text(root / WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(root / MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "present_surfaces": {
                    "validators": list(EXPECTED_MANIFEST_VALIDATORS),
                    "closure_notes": list(EXPECTED_MANIFEST_CLOSURE_NOTES),
                    "checkers": list(EXPECTED_MANIFEST_CHECKERS),
                    "artifact_support": list(EXPECTED_MANIFEST_ARTIFACT_SUPPORT),
                    "fixdep_support": list(EXPECTED_MANIFEST_FIXDEP_SUPPORT),
                    "make_wrappers": list(EXPECTED_MANIFEST_MAKE_WRAPPERS),
                },
                "notes": [EXPECTED_MANIFEST_NOTE],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validator_entrypoint_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert collect_issues(root) == []
        cases += 1

        path = root / VALIDATOR_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_VALIDATOR_MARKERS[0]))
        assert ("MISSING_VALIDATOR_MARKER", REQUIRED_VALIDATOR_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / CLOSURE_NOTE_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_CLOSURE_NOTE_MARKERS[0]))
        assert ("MISSING_CLOSURE_NOTE_MARKER", REQUIRED_CLOSURE_NOTE_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / BOOTSTRAP_NOTE_REL
        text = read_text(path)
        write_text(path, replace_once(text, REQUIRED_BOOTSTRAP_NOTE_MARKERS[0]))
        assert ("MISSING_BOOTSTRAP_NOTE_MARKER", REQUIRED_BOOTSTRAP_NOTE_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / WORKFLOW_REL
        text = read_text(path)
        write_text(path, replace_exact_line(text, REQUIRED_WORKFLOW_LINES[0]))
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        text = read_text(path)
        write_text(path, duplicate_exact_line(text, REQUIRED_WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / MAKEFILE_REL
        text = read_text(path)
        write_text(path, replace_exact_line(text, REQUIRED_MAKEFILE_LINES[0]))
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        text = read_text(path)
        write_text(path, duplicate_exact_line(text, REQUIRED_MAKEFILE_LINES[1]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2") in collect_issues(root)
        cases += 1
        build_sample_root(root)

        path = root / MANIFEST_REL
        manifest = load_manifest(path)
        manifest["present_surfaces"]["checkers"] = []
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_CHECKER", "scripts/zigux/check-phase2-tool-manifest.py") in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest = load_manifest(path)
        manifest["present_surfaces"]["fixdep_support"] = []
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_FIXDEP_SUPPORT", "scripts/zigux/check-phase2-fixdep-gate.py") in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest = load_manifest(path)
        manifest["notes"] = []
        write_text(path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_NOTE", EXPECTED_MANIFEST_NOTE) in collect_issues(root)
        cases += 1

    print("PHASE2_VALIDATOR_ENTRYPOINT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_VALIDATOR_ENTRYPOINT_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to check")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_VALIDATOR_ENTRYPOINT_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    return run_checker(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
