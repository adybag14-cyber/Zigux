#!/usr/bin/env python3
"""Fail closed when the Phase 2 checkers manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
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
            "checkers": list(EXPECTED_CHECKERS if entries is None else entries),
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

    checkers = surfaces.get("checkers")
    if not isinstance(checkers, list):
        return ["invalid checkers list"]

    issues: list[str] = []
    for index, entry in enumerate(checkers):
        if not isinstance(entry, str):
            issues.append(f"invalid checkers entry at index {index}: {entry!r}")

    string_entries = [entry for entry in checkers if isinstance(entry, str)]
    if len(checkers) != len(EXPECTED_CHECKERS):
        issues.append(
            "checkers count drift: "
            f"expected {len(EXPECTED_CHECKERS)}, found {len(checkers)}"
        )

    for expected in EXPECTED_CHECKERS:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing checkers entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate checkers entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_CHECKERS):
        if index >= len(checkers):
            continue
        actual = checkers[index]
        if actual != expected:
            issues.append(
                f"checkers order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_CHECKERS:
            issues.append(f"unexpected checkers entry: {entry}")
            continue

        checker_path = repo_root / entry
        if not checker_path.exists():
            issues.append(f"missing checkers path: {entry}")
        elif not checker_path.is_file():
            issues.append(f"non-file checkers path: {entry}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_checkers_surface_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        for relative_path in EXPECTED_CHECKERS:
            _write(root / relative_path, "present\n")

        issues = validate(root)
        if issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","phase":"Phase 3"}\n')
        issues = validate(root)
        if "duplicate json key: phase" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected duplicate json key was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "[]\n")
        issues = validate(root)
        if "invalid manifest root object" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest root object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": []}\n',
        )
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            (
                '{"phase":"Phase 2","present_surfaces":{"checkers":[],'
                '"checkers":[]}}'
                "\n"
            ),
        )
        issues = validate(root)
        if "duplicate json key: checkers" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected duplicate nested json key was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"checkers": "bad"}}\n',
        )
        issues = validate(root)
        if "invalid checkers list" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected invalid checkers list was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_CHECKERS[:-1])),
        )
        issues = validate(root)
        missing_issue = "missing checkers entry: scripts/zigux/check-fixdep-diff.py"
        if missing_issue not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected missing checkers entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"checkers": ['
            '"scripts/zigux/check-zig-toolchain.py", 7, '
            '"scripts/zigux/check-fixdep-diff.py"]}}\n',
        )
        issues = validate(root)
        if "invalid checkers entry at index 1: 7" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected invalid checkers entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_CHECKERS)
        duplicate_entries[-1] = EXPECTED_CHECKERS[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = (
            "duplicate checkers entry: "
            "scripts/zigux/check-phase2-fixdep-gate.py:count=2"
        )
        if duplicate_issue not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected duplicate checkers entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_CHECKERS)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "checkers order drift at index 0: "
            "expected 'scripts/zigux/check-zig-toolchain.py', "
            "found 'scripts/zigux/check-lane05-local-first-archive-workflow.py'"
        )
        if order_issue not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected checkers order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_CHECKERS) + ["scripts/zigux/unexpected.py"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "scripts/zigux/unexpected.py", "present\n")
        issues = validate(root)
        if "unexpected checkers entry: scripts/zigux/unexpected.py" not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected unexpected checkers entry was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        non_file_path = root / EXPECTED_CHECKERS[-1]
        non_file_path.unlink()
        non_file_path.mkdir()
        issues = validate(root)
        non_file_issue = "non-file checkers path: scripts/zigux/check-fixdep-diff.py"
        if non_file_issue not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected non-file checkers path was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        missing_path = root / EXPECTED_CHECKERS[-1]
        if missing_path.exists():
            if missing_path.is_dir():
                missing_path.rmdir()
            else:
                missing_path.unlink()
        issues = validate(root)
        missing_path_issue = "missing checkers path: scripts/zigux/check-fixdep-diff.py"
        if missing_path_issue not in issues:
            print("PHASE2_CHECKERS_SURFACE_SELF_TEST=fail")
            print("expected missing checkers path was not reported")
            return 1
        case_count += 1

    print("PHASE2_CHECKERS_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_CHECKERS_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_CHECKERS:
        _write(root / relative_path, "present\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 checkers surface."
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
        print("PHASE2_CHECKERS_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CHECKERS_SURFACE=pass")
    print(f"PHASE2_CHECKERS_SURFACE_COUNT={len(EXPECTED_CHECKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())