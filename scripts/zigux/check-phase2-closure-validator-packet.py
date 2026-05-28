#!/usr/bin/env python3
"""Fail-closed guard for the shared Phase 2 closure-validator packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    VALIDATOR_REL,
    CLOSURE_NOTE_REL,
    PHASE2_BOOTSTRAP_NOTES_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
)

REQUIRED_VALIDATOR_MARKERS = (
    'WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")',
    'PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")',
    'PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")',
    'PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")',
    'PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")',
    'MAKEFILE_REL = Path("zigux/Makefile")',
    'PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")',
    'issues.append(("MISSING_MANIFEST_SURFACE", "validators:scripts/zigux/validate-phase2.py"))',
    'issues.append(("MISSING_MANIFEST_SURFACE", "validators:scripts/zigux/validate-phase2-closure.py"))',
    'print("PHASE2_CLOSURE_VALIDATION=pass")',
    'print("PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure")',
)

REQUIRED_CLOSURE_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-validate`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

REQUIRED_TESTS_README_MARKERS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-validate",
)

REQUIRED_WORKFLOW_LINES = (
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_MANIFEST_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_manifest_members(
    issues: list[tuple[str, str]], label: str, actual: list[str] | None, expected: tuple[str, ...]
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    validator_text = read_text(resolve(root, VALIDATOR_REL))
    closure_text = read_text(resolve(root, CLOSURE_NOTE_REL))
    scripts_text = read_text(resolve(root, SCRIPTS_README_REL))
    tests_text = read_text(resolve(root, TESTS_README_REL))
    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in REQUIRED_VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_SCRIPTS_README_MARKERS:
        if marker not in scripts_text:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_text:
            issues.append(("MISSING_TESTS_README_MARKER", marker))

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

    expect_manifest_members(
        issues,
        "validators",
        require_manifest_list(issues, manifest, "validators"),
        EXPECTED_MANIFEST_VALIDATORS,
    )
    expect_manifest_members(
        issues,
        "closure_notes",
        require_manifest_list(issues, manifest, "closure_notes"),
        EXPECTED_MANIFEST_CLOSURE_NOTES,
    )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATOR_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    validator_body = "\n".join(
        (
            "#!/usr/bin/env python3",
            *REQUIRED_VALIDATOR_MARKERS,
            "",
        )
    )
    closure_body = "\n".join(("# Phase 2 Closure", *REQUIRED_CLOSURE_MARKERS, ""))
    bootstrap_notes_body = "# Phase 2 Toolchain Bootstrap Notes\n"
    scripts_body = "\n".join(("# scripts/zigux", *REQUIRED_SCRIPTS_README_MARKERS, ""))
    tests_body = "\n".join(("# zigux/tests", *REQUIRED_TESTS_README_MARKERS, ""))
    workflow_body = "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES, "")) + "\n"
    makefile_body = "\n".join(
        (
            "PYTHON ?= python3",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            *REQUIRED_MAKEFILE_LINES,
            "",
        )
    )
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": [],
        "present_surfaces": {
            "validators": list(EXPECTED_MANIFEST_VALIDATORS),
            "closure_notes": list(EXPECTED_MANIFEST_CLOSURE_NOTES),
        },
    }

    write_text(resolve(root, VALIDATOR_REL), validator_body)
    write_text(resolve(root, CLOSURE_NOTE_REL), closure_body)
    write_text(resolve(root, PHASE2_BOOTSTRAP_NOTES_REL), bootstrap_notes_body)
    write_text(resolve(root, SCRIPTS_README_REL), scripts_body)
    write_text(resolve(root, TESTS_README_REL), tests_body)
    write_text(resolve(root, WORKFLOW_REL), workflow_body)
    write_text(resolve(root, MAKEFILE_REL), makefile_body)
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            replace_once(validator_path.read_text(encoding="utf-8"), REQUIRED_VALIDATOR_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MARKER", REQUIRED_VALIDATOR_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve(root, CLOSURE_NOTE_REL)
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), REQUIRED_CLOSURE_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        scripts_path = resolve(root, SCRIPTS_README_REL)
        scripts_path.write_text(
            replace_once(scripts_path.read_text(encoding="utf-8"), REQUIRED_SCRIPTS_README_MARKERS[1]),
            encoding="utf-8",
        )
        assert (
            "MISSING_SCRIPTS_README_MARKER",
            REQUIRED_SCRIPTS_README_MARKERS[1],
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        tests_path = resolve(root, TESTS_README_REL)
        tests_path.write_text(
            replace_once(tests_path.read_text(encoding="utf-8"), REQUIRED_TESTS_README_MARKERS[2]),
            encoding="utf-8",
        )
        assert ("MISSING_TESTS_README_MARKER", REQUIRED_TESTS_README_MARKERS[2]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve(root, WORKFLOW_REL)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                REQUIRED_WORKFLOW_LINES[0],
                "run: python3 scripts/zigux/other.py",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve(root, WORKFLOW_REL)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[1]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_WORKFLOW_LINE",
            f"{REQUIRED_WORKFLOW_LINES[1]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve(root, MAKEFILE_REL)
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                REQUIRED_MAKEFILE_LINES[1],
                "# removed",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"] = ["scripts/zigux/validate-phase2.py"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "validators:scripts/zigux/validate-phase2-closure.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["closure_notes"] = ["Documentation/zigux/phase2-closure.md"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "closure_notes:Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve(root, PHASE2_BOOTSTRAP_NOTES_REL).unlink()
        assert (
            "MISSING_REQUIRED_FILE",
            PHASE2_BOOTSTRAP_NOTES_REL.as_posix(),
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the shared Phase 2 closure-validator packet drifts."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_VALIDATOR_MARKER_COUNT={len(REQUIRED_VALIDATOR_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
