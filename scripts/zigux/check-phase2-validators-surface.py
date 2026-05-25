#!/usr/bin/env python3
"""Fail closed when the Phase 2 validators manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_NOTE_MARKER = (
    "Keep the directly readable validator pair explicit through "
    "scripts/zigux/validate-phase2.py and "
    "scripts/zigux/validate-phase2-closure.py instead of leaving the "
    "closure-side replay packet implied only in prose."
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(
    entries: list[object] | None = None,
    *,
    notes: list[object] | None = None,
    present_surfaces: object | None = None,
) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": (
            {"validators": list(EXPECTED_VALIDATORS)}
            if present_surfaces is None
            else present_surfaces
        ),
        "notes": [EXPECTED_NOTE_MARKER] if notes is None else notes,
    }
    if entries is not None:
        payload["present_surfaces"] = {"validators": list(entries)}
    return json.dumps(payload, indent=2) + "\n"


def count_exact_entries(entries: list[str], marker: str) -> int:
    return sum(1 for entry in entries if entry == marker)


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    if not isinstance(manifest, dict):
        return ["invalid manifest root"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    validators = surfaces.get("validators")
    if not isinstance(validators, list):
        return ["invalid validators list"]

    issues: list[str] = []
    for index, entry in enumerate(validators):
        if not isinstance(entry, str):
            issues.append(f"invalid validators entry at index {index}: {entry!r}")

    string_entries = [entry for entry in validators if isinstance(entry, str)]

    if len(validators) != len(EXPECTED_VALIDATORS):
        issues.append(
            "validators count drift: "
            f"expected {len(EXPECTED_VALIDATORS)}, found {len(validators)}"
        )

    for expected in EXPECTED_VALIDATORS:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing validators entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate validators entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_VALIDATORS):
        if index >= len(validators):
            continue
        actual = validators[index]
        if actual != expected:
            issues.append(
                f"validators order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_VALIDATORS:
            issues.append(f"unexpected validators entry: {entry}")
        elif not (repo_root / entry).exists():
            issues.append(f"missing validators path: {entry}")

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append("invalid notes list")
    else:
        string_notes = [note for note in notes if isinstance(note, str)]
        if EXPECTED_NOTE_MARKER not in string_notes:
            issues.append(f"missing validators note marker: {EXPECTED_NOTE_MARKER}")

    return issues


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_VALIDATORS:
        _write(root / relative_path, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validators_surface_") as temp_dir:
        root = Path(temp_dir)

        write_sample_root(root)
        issues = validate(root)
        if issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "present_surfaces": []}\n')
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"validators": "bad"}}\n',
        )
        issues = validate(root)
        if "invalid validators list" not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected invalid validators list was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, _sample_manifest(list(EXPECTED_VALIDATORS[:-1])))
        issues = validate(root)
        missing_issue = (
            "missing validators entry: scripts/zigux/validate-phase2-closure.py"
        )
        if missing_issue not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected missing validators entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(
            root / MANIFEST_PATH,
            _sample_manifest([EXPECTED_VALIDATORS[0], 7]),
        )
        issues = validate(root)
        if "invalid validators entry at index 1: 7" not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected invalid validators entry type was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        duplicate_entries = list(EXPECTED_VALIDATORS)
        duplicate_entries[-1] = EXPECTED_VALIDATORS[0]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = (
            "duplicate validators entry: "
            "scripts/zigux/validate-phase2.py:count=2"
        )
        if duplicate_issue not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected duplicate validators entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        reordered_entries = list(EXPECTED_VALIDATORS)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "validators order drift at index 0: "
            "expected 'scripts/zigux/validate-phase2.py', "
            "found 'scripts/zigux/validate-phase2-closure.py'"
        )
        if order_issue not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected validators order drift was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        extra_entries = list(EXPECTED_VALIDATORS) + ["scripts/zigux/extra.py"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "scripts/zigux/extra.py", "present\n")
        issues = validate(root)
        if "unexpected validators entry: scripts/zigux/extra.py" not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected unexpected validators entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, _sample_manifest(notes=[]))
        issues = validate(root)
        missing_note_issue = f"missing validators note marker: {EXPECTED_NOTE_MARKER}"
        if missing_note_issue not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected missing validators note marker was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        missing_path = root / EXPECTED_VALIDATORS[-1]
        missing_path.unlink()
        issues = validate(root)
        missing_path_issue = (
            "missing validators path: scripts/zigux/validate-phase2-closure.py"
        )
        if missing_path_issue not in issues:
            print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=fail")
            print("expected missing validators path was not reported")
            return 1
        case_count += 1

    print("PHASE2_VALIDATORS_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_VALIDATORS_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 validators surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 2 tool manifest",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"wrote sample root to {args.write_sample_root}")
        return 0

    issues = validate(args.root)
    if issues:
        print("PHASE2_VALIDATORS_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_VALIDATORS_SURFACE=pass")
    print(f"PHASE2_VALIDATORS_SURFACE_COUNT={len(EXPECTED_VALIDATORS)}")
    print("PHASE2_VALIDATORS_SURFACE_NOTE_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())