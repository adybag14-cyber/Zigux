#!/usr/bin/env python3
"""Guard the shared Phase 2 closure parked-state packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
VALIDATE_PHASE2_REL = Path("scripts/zigux/validate-phase2.py")
VALIDATE_PHASE2_CLOSURE_REL = Path("scripts/zigux/validate-phase2-closure.py")

EXPECTED_STATUS_LINE = "- `PHASE2_STATUS=parked`"
EXPECTED_RESTORE_STATE_LINE = "- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`"
EXPECTED_MANIFEST_LINE = "- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`"
EXPECTED_SHARED_NOTE_LINE = (
    "- shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`"
)
EXPECTED_VALIDATOR_PAIR_LINE = (
    "- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and "
    "`python3 scripts/zigux/validate-phase2-closure.py`"
)

REQUIRED_CLOSURE_MARKERS = (
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
)

REQUIRED_BOOTSTRAP_MARKERS = (
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
)

REQUIRED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

REQUIRED_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)

REQUIRED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

README_SECTION_MARKERS = (
    (DOCS_README_REL, "Phase 2 notes"),
    (REVIEW_CHECKLIST_REL, "if the change touches the shared Phase 2 toolchain packet"),
    (SCRIPTS_README_REL, "## Phase 2"),
    (TESTS_README_REL, "## Phase 2 review packet"),
)


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


def require_string_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str]:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return []
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return []
    return list(value)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    bootstrap_text = read_text(root / PHASE2_BOOTSTRAP_NOTES_REL)
    manifest = read_json(root / PHASE2_TOOL_MANIFEST_REL)

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for rel in (VALIDATE_PHASE2_REL, VALIDATE_PHASE2_CLOSURE_REL):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))

    expected_lines = (
        EXPECTED_STATUS_LINE,
        EXPECTED_RESTORE_STATE_LINE,
        EXPECTED_MANIFEST_LINE,
        EXPECTED_SHARED_NOTE_LINE,
        EXPECTED_VALIDATOR_PAIR_LINE,
    )
    for marker in expected_lines:
        count = count_exact_lines(closure_text, marker)
        if count == 0:
            issues.append(("MISSING_CLOSURE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CLOSURE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if f"`{marker}`" not in closure_text and marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_BOOTSTRAP_MARKERS:
        if f"`{marker}`" not in bootstrap_text and marker not in bootstrap_text:
            issues.append(("MISSING_BOOTSTRAP_MARKER", marker))

    if manifest.get("status") != "active":
        issues.append(("MANIFEST_STATUS_MISMATCH", repr(manifest.get("status"))))

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    review_surfaces = require_string_list(issues, manifest, "review_surfaces")
    closure_notes = require_string_list(issues, manifest, "closure_notes")
    validators = require_string_list(issues, manifest, "validators")
    if issues:
        return issues

    for surface in REQUIRED_REVIEW_SURFACES:
        if surface not in review_surfaces:
            issues.append(("MISSING_REVIEW_SURFACE", surface))

    for note in REQUIRED_CLOSURE_NOTES:
        if note not in closure_notes:
            issues.append(("MISSING_CLOSURE_NOTE", note))

    for validator in REQUIRED_VALIDATORS:
        if validator not in validators:
            issues.append(("MISSING_VALIDATOR", validator))

    for rel, marker in README_SECTION_MARKERS:
        text = read_text(root / rel)
        if marker not in text:
            issues.append(("MISSING_REMINDER_MARKER", f"{rel.as_posix()}:{marker}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_STATE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": [],
        "present_surfaces": {
            "review_surfaces": list(REQUIRED_REVIEW_SURFACES),
            "closure_notes": list(REQUIRED_CLOSURE_NOTES),
            "validators": list(REQUIRED_VALIDATORS),
        },
    }
    write_text(
        root / PHASE2_CLOSURE_REL,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                "## Status",
                "",
                EXPECTED_STATUS_LINE,
                EXPECTED_RESTORE_STATE_LINE,
                EXPECTED_MANIFEST_LINE,
                EXPECTED_SHARED_NOTE_LINE,
                EXPECTED_VALIDATOR_PAIR_LINE,
            )
        )
        + "\n",
    )
    write_text(
        root / PHASE2_BOOTSTRAP_NOTES_REL,
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "- `Documentation/zigux/phase2-closure.md`",
                "- `scripts/zigux/validate-phase2.py`",
                "- `scripts/zigux/validate-phase2-closure.py`",
                "- `zigux/tests/fixtures/phase2_tool_manifest.json`",
            )
        )
        + "\n",
    )
    write_text(root / DOCS_README_REL, "# Zigux Documentation\n\nPhase 2 notes\n")
    write_text(
        root / REVIEW_CHECKLIST_REL,
        "# Zigux Review Checklist\n\nif the change touches the shared Phase 2 toolchain packet\n",
    )
    write_text(root / SCRIPTS_README_REL, "# scripts/zigux\n\n## Phase 2\n")
    write_text(root / TESTS_README_REL, "# zigux/tests\n\n## Phase 2 review packet\n")
    write_text(root / VALIDATE_PHASE2_REL, "print('phase2')\n")
    write_text(root / VALIDATE_PHASE2_CLOSURE_REL, "print('phase2-closure')\n")
    write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_state_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        write_text(
            root / PHASE2_CLOSURE_REL,
            read_text(root / PHASE2_CLOSURE_REL).replace(
                EXPECTED_STATUS_LINE,
                "- `PHASE2_STATUS=active`",
                1,
            ),
        )
        assert (
            "MISSING_CLOSURE_LINE",
            EXPECTED_STATUS_LINE,
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        write_text(
            root / PHASE2_CLOSURE_REL,
            read_text(root / PHASE2_CLOSURE_REL).replace(
                EXPECTED_RESTORE_STATE_LINE,
                "- `PHASE2_CLOSURE_RESTORE_STATE=manifest_only`",
                1,
            ),
        )
        assert (
            "MISSING_CLOSURE_LINE",
            EXPECTED_RESTORE_STATE_LINE,
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        write_text(
            root / PHASE2_BOOTSTRAP_NOTES_REL,
            read_text(root / PHASE2_BOOTSTRAP_NOTES_REL).replace(
                "- `scripts/zigux/validate-phase2-closure.py`\n",
                "",
                1,
            ),
        )
        assert (
            "MISSING_BOOTSTRAP_MARKER",
            "scripts/zigux/validate-phase2-closure.py",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = read_json(root / PHASE2_TOOL_MANIFEST_REL)
        assert isinstance(manifest, dict)
        manifest["status"] = "parked"
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_STATUS_MISMATCH", "'parked'") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = read_json(root / PHASE2_TOOL_MANIFEST_REL)
        assert isinstance(manifest, dict)
        manifest["repo_reality_gaps"] = ["drift"]
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert ("UNEXPECTED_MANIFEST_GAPS", "['drift']") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = read_json(root / PHASE2_TOOL_MANIFEST_REL)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["closure_notes"] = ["Documentation/zigux/phase2-closure.md"]
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert (
            "MISSING_CLOSURE_NOTE",
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        write_text(root / TESTS_README_REL, "# zigux/tests\n")
        assert (
            "MISSING_REMINDER_MARKER",
            "zigux/tests/README.md:## Phase 2 review packet",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_STATE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_STATE_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 2 closure parked-state packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_STATE_PACKET=pass")
    print("PHASE2_CLOSURE_STATE_PACKET_STATUS=parked")
    print("PHASE2_CLOSURE_STATE_PACKET_RESTORE_STATE=docs_plus_manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
