#!/usr/bin/env python3
"""Guard the current Phase 2 closure-validator packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REQUIRED_VALIDATOR_MARKERS = (
    'PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")',
    'PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")',
    'MAKEFILE_REL = Path("zigux/Makefile")',
    'MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")',
    '"`scripts/zigux/validate-phase2.py`",',
    '"`python3 scripts/zigux/validate-phase2-closure.py --self-test`",',
    '"`python3 scripts/zigux/validate-phase2-closure.py`",',
    '"run: python3 scripts/zigux/validate-phase2.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",',
    'EXPECTED_MANIFEST_VALIDATORS = (',
)

REQUIRED_CLOSURE_NOTE_MARKERS = (
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
    "`PHASE2_CLOSURE_VALIDATORS=",
    "`PHASE2_SHARED_MAKE_ROUTES=",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: make -C zigux phase2-validate",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
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

EXPECTED_MANIFEST_MAKE_WRAPPER = "make -C zigux phase2-validate"
EXPECTED_MANIFEST_NOTE = (
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py "
    "and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet "
    "implied only in prose."
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
    raise AssertionError(f"line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def load_manifest(path: Path) -> dict:
    return json.loads(read_text(path))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    validator_text = read_text(root / "scripts" / "zigux" / "validate-phase2-closure.py")
    closure_text = read_text(root / "Documentation" / "zigux" / "phase2-closure.md")
    workflow_text = read_text(root / ".github" / "workflows" / "zigux-bootstrap.yml")
    makefile_text = read_text(root / "zigux" / "Makefile")
    manifest = load_manifest(root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json")

    for marker in REQUIRED_VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))

    for marker in REQUIRED_CLOSURE_NOTE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

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

    make_wrappers = present_surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list):
        issues.append(("MISSING_MANIFEST_SECTION", "present_surfaces.make_wrappers"))
    elif EXPECTED_MANIFEST_MAKE_WRAPPER not in make_wrappers:
        issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", EXPECTED_MANIFEST_MAKE_WRAPPER))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_MANIFEST_SECTION", "notes"))
    elif EXPECTED_MANIFEST_NOTE not in notes:
        issues.append(("MISSING_MANIFEST_NOTE", EXPECTED_MANIFEST_NOTE))

    return issues


def run_checker(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE2_CLOSURE_VALIDATOR_PACKET=fail")
        for code, detail in issues:
            print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_ISSUE={code}:{detail}")
        return 1
    print("PHASE2_CLOSURE_VALIDATOR_PACKET=pass")
    return 0


def build_sample_root(root: Path) -> None:
    write_text(
        root / "scripts" / "zigux" / "validate-phase2-closure.py",
        "\n".join(REQUIRED_VALIDATOR_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation" / "zigux" / "phase2-closure.md",
        "\n".join(REQUIRED_CLOSURE_NOTE_MARKERS) + "\n",
    )
    write_text(
        root / ".github" / "workflows" / "zigux-bootstrap.yml",
        "\n".join(REQUIRED_WORKFLOW_LINES) + "\n",
    )
    write_text(
        root / "zigux" / "Makefile",
        "\n".join(REQUIRED_MAKEFILE_LINES) + "\n",
    )
    write_text(
        root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json",
        json.dumps(
            {
                "present_surfaces": {
                    "validators": list(EXPECTED_MANIFEST_VALIDATORS),
                    "closure_notes": list(EXPECTED_MANIFEST_CLOSURE_NOTES),
                    "make_wrappers": [EXPECTED_MANIFEST_MAKE_WRAPPER],
                },
                "notes": [EXPECTED_MANIFEST_NOTE],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)

        assert collect_issues(root) == []
        cases += 1

        validator_path = root / "scripts" / "zigux" / "validate-phase2-closure.py"
        validator_text = read_text(validator_path)
        write_text(validator_path, replace_once(validator_text, REQUIRED_VALIDATOR_MARKERS[0]))
        assert ("MISSING_VALIDATOR_MARKER", REQUIRED_VALIDATOR_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        closure_path = root / "Documentation" / "zigux" / "phase2-closure.md"
        closure_text = read_text(closure_path)
        write_text(closure_path, replace_once(closure_text, REQUIRED_CLOSURE_NOTE_MARKERS[0]))
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_NOTE_MARKERS[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        workflow_path = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_text = read_text(workflow_path)
        write_text(workflow_path, replace_exact_line(workflow_text, REQUIRED_WORKFLOW_LINES[0]))
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        workflow_text = read_text(workflow_path)
        write_text(workflow_path, duplicate_exact_line(workflow_text, REQUIRED_WORKFLOW_LINES[0]))
        assert (
            "DUPLICATE_WORKFLOW_LINE",
            f"{REQUIRED_WORKFLOW_LINES[0]}:count=2",
        ) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        makefile_path = root / "zigux" / "Makefile"
        makefile_text = read_text(makefile_path)
        write_text(makefile_path, replace_exact_line(makefile_text, REQUIRED_MAKEFILE_LINES[0]))
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        makefile_text = read_text(makefile_path)
        write_text(makefile_path, duplicate_exact_line(makefile_text, REQUIRED_MAKEFILE_LINES[1]))
        assert (
            "DUPLICATE_MAKEFILE_LINE",
            f"{REQUIRED_MAKEFILE_LINES[1]}:count=2",
        ) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest_path = root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
        manifest = load_manifest(manifest_path)
        manifest["present_surfaces"]["validators"] = ["scripts/zigux/validate-phase2.py"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert (
            "MISSING_MANIFEST_VALIDATOR",
            "scripts/zigux/validate-phase2-closure.py",
        ) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest = load_manifest(manifest_path)
        manifest["present_surfaces"]["make_wrappers"] = []
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert (
            "MISSING_MANIFEST_MAKE_WRAPPER",
            EXPECTED_MANIFEST_MAKE_WRAPPER,
        ) in collect_issues(root)
        cases += 1
        build_sample_root(root)

        manifest = load_manifest(manifest_path)
        manifest["notes"] = []
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_NOTE", EXPECTED_MANIFEST_NOTE) in collect_issues(root)
        cases += 1

    print("PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to check")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    return run_checker(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
