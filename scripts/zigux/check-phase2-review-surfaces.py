#!/usr/bin/env python3
"""Fail closed when the Phase 2 review-surfaces manifest packet drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
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
            "review_surfaces": list(EXPECTED_REVIEW_SURFACES if entries is None else entries),
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

    review_surfaces = surfaces.get("review_surfaces")
    if not isinstance(review_surfaces, list):
        return ["invalid review_surfaces list"]

    issues: list[str] = []
    for index, entry in enumerate(review_surfaces):
        if not isinstance(entry, str):
            issues.append(f"invalid review_surfaces entry at index {index}: {entry!r}")

    string_entries = [entry for entry in review_surfaces if isinstance(entry, str)]
    if len(review_surfaces) != len(EXPECTED_REVIEW_SURFACES):
        issues.append(
            "review_surfaces count drift: "
            f"expected {len(EXPECTED_REVIEW_SURFACES)}, found {len(review_surfaces)}"
        )

    for expected in EXPECTED_REVIEW_SURFACES:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing review_surfaces entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate review_surfaces entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_REVIEW_SURFACES):
        if index >= len(review_surfaces):
            continue
        actual = review_surfaces[index]
        if actual != expected:
            issues.append(
                f"review_surfaces order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_REVIEW_SURFACES:
            issues.append(f"unexpected review_surfaces entry: {entry}")
        else:
            entry_path = repo_root / entry
            if not entry_path.exists():
                issues.append(f"missing review_surfaces path: {entry}")
            elif not entry_path.is_file():
                issues.append(f"non-file review_surfaces path: {entry}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_surfaces_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        for relative_path in EXPECTED_REVIEW_SURFACES:
            _write(root / relative_path, "present\n")

        issues = validate(root)
        if issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","phase":"Phase 3"}\n')
        issues = validate(root)
        if "duplicate json key: phase" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected duplicate json key was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "[]\n")
        issues = validate(root)
        if "invalid manifest root object" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected invalid manifest root object was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","present_surfaces":{"review_surfaces":[],"review_surfaces":[]}}\n')
        issues = validate(root)
        if "duplicate json key: review_surfaces" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected duplicate nested json key was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "present_surfaces": []}\n')
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "present_surfaces": {"review_surfaces": "bad"}}\n')
        issues = validate(root)
        if "invalid review_surfaces list" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected invalid review_surfaces list was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest(list(EXPECTED_REVIEW_SURFACES[:-1])))
        issues = validate(root)
        missing_issue = "missing review_surfaces entry: zigux/tests/README.md"
        if missing_issue not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected missing review_surfaces entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"review_surfaces": ['
            '"Documentation/zigux/README.md", 7, '
            '"Documentation/zigux/review-checklist.md", "scripts/zigux/README.md", "zigux/tests/README.md"]}}\n',
        )
        issues = validate(root)
        if "invalid review_surfaces entry at index 1: 7" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected invalid review_surfaces entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_REVIEW_SURFACES)
        duplicate_entries[-1] = EXPECTED_REVIEW_SURFACES[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = "duplicate review_surfaces entry: scripts/zigux/README.md:count=2"
        if duplicate_issue not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected duplicate review_surfaces entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_REVIEW_SURFACES)
        reordered_entries[0], reordered_entries[1] = reordered_entries[1], reordered_entries[0]
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "review_surfaces order drift at index 0: "
            "expected 'Documentation/zigux/README.md', "
            "found 'Documentation/zigux/phase2-closure.md'"
        )
        if order_issue not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected review_surfaces order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_REVIEW_SURFACES) + ["Documentation/zigux/extra.md"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "Documentation/zigux/extra.md", "present\n")
        issues = validate(root)
        if "unexpected review_surfaces entry: Documentation/zigux/extra.md" not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected unexpected review_surfaces entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        non_file_path = root / EXPECTED_REVIEW_SURFACES[-1]
        non_file_path.unlink()
        non_file_path.mkdir()
        issues = validate(root)
        non_file_issue = "non-file review_surfaces path: zigux/tests/README.md"
        if non_file_issue not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected non-file review_surfaces path was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        missing_path = root / EXPECTED_REVIEW_SURFACES[-1]
        if missing_path.exists():
            if missing_path.is_dir():
                missing_path.rmdir()
            else:
                missing_path.unlink()
        issues = validate(root)
        missing_path_issue = "missing review_surfaces path: zigux/tests/README.md"
        if missing_path_issue not in issues:
            print("PHASE2_REVIEW_SURFACES_SELF_TEST=fail")
            print("expected missing review_surfaces path was not reported")
            return 1
        case_count += 1

    print("PHASE2_REVIEW_SURFACES_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_SURFACES_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_REVIEW_SURFACES:
        _write(root / relative_path, "present\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 review-surfaces packet."
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
        print("PHASE2_REVIEW_SURFACES=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_REVIEW_SURFACES=pass")
    print(f"PHASE2_REVIEW_SURFACES_COUNT={len(EXPECTED_REVIEW_SURFACES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
