#!/usr/bin/env python3
"""Fail closed when the Phase 2 closure_notes manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)


class DuplicateKeyError(ValueError):
    """Raised when a manifest JSON object repeats a key."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateKeyError(f"duplicate json key: {key}")
        payload[key] = value
    return payload


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(entries: list[str] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "closure_notes": list(EXPECTED_CLOSURE_NOTES if entries is None else entries),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def count_exact_entries(entries: list[str], marker: str) -> int:
    return sum(1 for entry in entries if entry == marker)


def load_manifest(manifest_path: Path) -> dict[str, object]:
    try:
        return json.loads(
            manifest_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest json: {exc.msg}") from exc
    except DuplicateKeyError as exc:
        raise ValueError(str(exc)) from exc


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = load_manifest(manifest_path)
    except ValueError as exc:
        return [str(exc)]

    if not isinstance(manifest, dict):
        return ["invalid manifest root object"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    closure_notes = surfaces.get("closure_notes")
    if not isinstance(closure_notes, list):
        return ["invalid closure_notes list"]

    issues: list[str] = []
    for index, entry in enumerate(closure_notes):
        if not isinstance(entry, str):
            issues.append(f"invalid closure_notes entry at index {index}: {entry!r}")

    string_entries = [entry for entry in closure_notes if isinstance(entry, str)]
    if len(closure_notes) != len(EXPECTED_CLOSURE_NOTES):
        issues.append(
            "closure_notes count drift: "
            f"expected {len(EXPECTED_CLOSURE_NOTES)}, found {len(closure_notes)}"
        )

    for expected in EXPECTED_CLOSURE_NOTES:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing closure_notes entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate closure_notes entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_CLOSURE_NOTES):
        if index >= len(closure_notes):
            continue
        actual = closure_notes[index]
        if actual != expected:
            issues.append(
                f"closure_notes order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_CLOSURE_NOTES:
            issues.append(f"unexpected closure_notes entry: {entry}")
        elif not (repo_root / entry).exists():
            issues.append(f"missing closure_notes path: {entry}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_notes_surface_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        for relative_path in EXPECTED_CLOSURE_NOTES:
            _write(root / relative_path, "present\n")

        issues = validate(root)
        if issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","phase":"Phase 3"}\n')
        issues = validate(root)
        if "duplicate json key: phase" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected duplicate json key was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "[]\n")
        issues = validate(root)
        if "invalid manifest root object" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest root object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": []}\n',
        )
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            (
                '{"phase":"Phase 2","present_surfaces":{"closure_notes":[],"closure_notes":[]}}'
                "\n"
            ),
        )
        issues = validate(root)
        if "duplicate json key: closure_notes" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected duplicate nested json key was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"closure_notes": "bad"}}\n',
        )
        issues = validate(root)
        if "invalid closure_notes list" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected invalid closure_notes list was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_CLOSURE_NOTES[:-1])),
        )
        issues = validate(root)
        missing_issue = (
            "missing closure_notes entry: "
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        )
        if missing_issue not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected missing closure_notes entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            (
                '{"phase": "Phase 2", "present_surfaces": {"closure_notes": ['
                '"Documentation/zigux/phase2-closure.md", 7]}}\n'
            ),
        )
        issues = validate(root)
        if "invalid closure_notes entry at index 1: 7" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected invalid closure_notes entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_CLOSURE_NOTES)
        duplicate_entries[-1] = EXPECTED_CLOSURE_NOTES[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = (
            "duplicate closure_notes entry: "
            "Documentation/zigux/phase2-closure.md:count=2"
        )
        if duplicate_issue not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected duplicate closure_notes entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_CLOSURE_NOTES)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "closure_notes order drift at index 0: "
            "expected 'Documentation/zigux/phase2-closure.md', "
            "found 'Documentation/zigux/phase2-toolchain-bootstrap-notes.md'"
        )
        if order_issue not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected closure_notes order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_CLOSURE_NOTES) + ["Documentation/zigux/extra.md"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "Documentation/zigux/extra.md", "present\n")
        issues = validate(root)
        if "unexpected closure_notes entry: Documentation/zigux/extra.md" not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected unexpected closure_notes entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        missing_path = root / EXPECTED_CLOSURE_NOTES[-1]
        missing_path.unlink()
        issues = validate(root)
        missing_path_issue = (
            "missing closure_notes path: "
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
        )
        if missing_path_issue not in issues:
            print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=fail")
            print("expected missing closure_notes path was not reported")
            return 1
        case_count += 1

    print("PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_NOTES_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_CLOSURE_NOTES:
        _write(root / relative_path, "present\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 closure_notes surface."
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
        print("PHASE2_CLOSURE_NOTES_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CLOSURE_NOTES_SURFACE=pass")
    print(f"PHASE2_CLOSURE_NOTES_SURFACE_COUNT={len(EXPECTED_CLOSURE_NOTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
