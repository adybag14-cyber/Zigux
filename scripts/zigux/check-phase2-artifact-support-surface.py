#!/usr/bin/env python3
"""Fail closed when the Phase 2 artifact-support manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_ARTIFACT_SUPPORT = (
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(entries: list[str] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "artifact_support": list(
                EXPECTED_ARTIFACT_SUPPORT if entries is None else entries
            ),
        },
    }
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
        return ["invalid manifest root object"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    artifact_support = surfaces.get("artifact_support")
    if not isinstance(artifact_support, list):
        return ["invalid artifact_support list"]

    issues: list[str] = []
    for index, entry in enumerate(artifact_support):
        if not isinstance(entry, str):
            issues.append(f"invalid artifact_support entry at index {index}: {entry!r}")

    string_entries = [entry for entry in artifact_support if isinstance(entry, str)]
    if len(artifact_support) != len(EXPECTED_ARTIFACT_SUPPORT):
        issues.append(
            "artifact_support count drift: "
            f"expected {len(EXPECTED_ARTIFACT_SUPPORT)}, found {len(artifact_support)}"
        )

    for expected in EXPECTED_ARTIFACT_SUPPORT:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing artifact_support entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate artifact_support entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_ARTIFACT_SUPPORT):
        if index >= len(artifact_support):
            continue
        actual = artifact_support[index]
        if actual != expected:
            issues.append(
                f"artifact_support order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_ARTIFACT_SUPPORT:
            issues.append(f"unexpected artifact_support entry: {entry}")
        elif not (repo_root / entry).exists():
            issues.append(f"missing artifact_support path: {entry}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_support_surface_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        for relative_path in EXPECTED_ARTIFACT_SUPPORT:
            _write(root / relative_path, "present\n")

        issues = validate(root)
        if issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "[]\n")
        issues = validate(root)
        if "invalid manifest root object" not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest root object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": []}\n',
        )
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"artifact_support": "bad"}}\n',
        )
        issues = validate(root)
        if "invalid artifact_support list" not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid artifact_support list was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_ARTIFACT_SUPPORT[:-1])),
        )
        issues = validate(root)
        missing_issue = (
            "missing artifact_support entry: "
            "zigux/tests/fixtures/phase2_artifact_tools_manifest.json"
        )
        if missing_issue not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing artifact_support entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"artifact_support": ['
            '"scripts/zigux/artifact_diff.py", 7, '
            '"zigux/tests/fixtures/phase2_artifact_tools_manifest.json"]}}\n',
        )
        issues = validate(root)
        if "invalid artifact_support entry at index 1: 7" not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid artifact_support entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_ARTIFACT_SUPPORT)
        duplicate_entries[-1] = EXPECTED_ARTIFACT_SUPPORT[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = (
            "duplicate artifact_support entry: "
            "scripts/zigux/check-phase2-artifact-tools-manifest.py:count=2"
        )
        if duplicate_issue not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected duplicate artifact_support entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_ARTIFACT_SUPPORT)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "artifact_support order drift at index 0: "
            "expected 'scripts/zigux/artifact_diff.py', "
            "found 'scripts/zigux/check-phase2-artifact-tools-manifest.py'"
        )
        if order_issue not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected artifact_support order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_ARTIFACT_SUPPORT) + ["scripts/zigux/unexpected.py"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "scripts/zigux/unexpected.py", "present\n")
        issues = validate(root)
        if "unexpected artifact_support entry: scripts/zigux/unexpected.py" not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected unexpected artifact_support entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        missing_path = root / EXPECTED_ARTIFACT_SUPPORT[-1]
        missing_path.unlink()
        issues = validate(root)
        missing_path_issue = (
            "missing artifact_support path: "
            "zigux/tests/fixtures/phase2_artifact_tools_manifest.json"
        )
        if missing_path_issue not in issues:
            print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing artifact_support path was not reported")
            return 1
        case_count += 1

    print("PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_ARTIFACT_SUPPORT:
        _write(root / relative_path, "present\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 artifact-support surface."
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
        print("PHASE2_ARTIFACT_SUPPORT_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_ARTIFACT_SUPPORT_SURFACE=pass")
    print(f"PHASE2_ARTIFACT_SUPPORT_SURFACE_COUNT={len(EXPECTED_ARTIFACT_SUPPORT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
