#!/usr/bin/env python3
"""Fail closed when the Phase 2 validators surface drifts."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")

EXPECTED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

REMINDER_SURFACES = (
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
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


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_VALIDATORS_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_json(root / MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [("INVALID_MANIFEST_SHAPE", "root")]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return [("INVALID_MANIFEST_SHAPE", "present_surfaces")]

    validators = surfaces.get("validators")
    if not isinstance(validators, list) or not all(isinstance(item, str) for item in validators):
        return [("INVALID_MANIFEST_SHAPE", "validators")]

    issues: list[tuple[str, str]] = []

    for expected in EXPECTED_VALIDATORS:
        if expected not in validators:
            issues.append(("MISSING_VALIDATOR_ENTRY", expected))

    if len(validators) != len(EXPECTED_VALIDATORS):
        issues.append(("UNEXPECTED_VALIDATOR_COUNT", str(len(validators))))

    if tuple(validators) != EXPECTED_VALIDATORS:
        issues.append(("VALIDATOR_ORDER_DRIFT", repr(tuple(validators))))

    for expected in EXPECTED_VALIDATORS:
        count = validators.count(expected)
        if count != 1:
            issues.append(("DUPLICATE_VALIDATOR_ENTRY", f"{expected}:count={count}"))
        if not (root / expected).exists():
            issues.append(("MISSING_VALIDATOR_PATH", expected))

    for rel in REMINDER_SURFACES:
        text = read_text(root / rel)
        for expected in EXPECTED_VALIDATORS:
            if count_occurrences(text, f"`{expected}`") == 0 and count_occurrences(text, expected) == 0:
                issues.append(("MISSING_REMINDER_MARKER", f"{rel.as_posix()}:{expected}"))

    return issues


def build_sample_root(root: Path) -> None:
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "scope": "sample validators packet",
        "repo_reality_gaps": [],
        "present_surfaces": {
            "validators": list(EXPECTED_VALIDATORS),
        },
        "notes": [
            "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose."
        ],
        "workflow": ".github/workflows/zigux-bootstrap.yml",
    }
    write_text(root / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
    write_text(root / EXPECTED_VALIDATORS[0], "present\n")
    write_text(root / EXPECTED_VALIDATORS[1], "present\n")

    reminder_text = (
        "Keep `scripts/zigux/validate-phase2.py` and "
        "`scripts/zigux/validate-phase2-closure.py` explicit.\n"
    )
    for rel in REMINDER_SURFACES:
        write_text(root / rel, reminder_text)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validators_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        payload = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"] = "drifted"
        write_text(root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_MANIFEST_SHAPE", "validators") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"].remove(EXPECTED_VALIDATORS[1])
        write_text(root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_ENTRY", EXPECTED_VALIDATORS[1]) in issues
        checks += 1

        build_sample_root(root)
        payload = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"] = [EXPECTED_VALIDATORS[1], EXPECTED_VALIDATORS[0]]
        write_text(root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        assert any(code == "VALIDATOR_ORDER_DRIFT" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        payload = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        payload["present_surfaces"]["validators"].append(EXPECTED_VALIDATORS[1])
        write_text(root / MANIFEST_REL, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("DUPLICATE_VALIDATOR_ENTRY", f"{EXPECTED_VALIDATORS[1]}:count=2") in issues
        assert ("UNEXPECTED_VALIDATOR_COUNT", "3") in issues
        checks += 1

        build_sample_root(root)
        (root / EXPECTED_VALIDATORS[0]).unlink()
        assert ("MISSING_VALIDATOR_PATH", EXPECTED_VALIDATORS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / DOCS_README_REL, "missing\n")
        assert ("MISSING_REMINDER_MARKER", f"{DOCS_README_REL.as_posix()}:{EXPECTED_VALIDATORS[0]}") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / REVIEW_CHECKLIST_REL, "missing\n")
        assert ("MISSING_REMINDER_MARKER", f"{REVIEW_CHECKLIST_REL.as_posix()}:{EXPECTED_VALIDATORS[1]}") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / TESTS_README_REL, "missing\n")
        assert ("MISSING_REMINDER_MARKER", f"{TESTS_README_REL.as_posix()}:{EXPECTED_VALIDATORS[0]}") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / SCRIPTS_README_REL, "missing\n")
        assert ("MISSING_REMINDER_MARKER", f"{SCRIPTS_README_REL.as_posix()}:{EXPECTED_VALIDATORS[1]}") in collect_issues(root)
        checks += 1

    print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_VALIDATORS_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail closed when the Phase 2 validators surface drifts.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root for focused replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        target = args.write_sample_root.resolve()
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        build_sample_root(target)
        print(f"PHASE2_VALIDATORS_SURFACE_SAMPLE_ROOT={target}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATORS_SURFACE=pass")
    print(f"PHASE2_VALIDATORS_SURFACE_COUNT={len(EXPECTED_VALIDATORS)}")
    print(f"PHASE2_VALIDATORS_SURFACE_REMINDER_COUNT={len(REMINDER_SURFACES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
