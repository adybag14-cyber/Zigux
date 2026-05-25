#!/usr/bin/env python3
"""Fail closed when the Phase 2 fixdep manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_FIXDEP_SUPPORT = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
    "zigux/tests/fixtures/fixdep/dep:colon.so",
    "zigux/tests/fixtures/fixdep/dep\\ name.rmeta",
    "zigux/tests/fixtures/fixdep/escaped\\ space-config.h",
    "zigux/tests/fixtures/fixdep/sample-config.h",
    "zigux/tests/fixtures/fixdep/sample.c",
    "zigux/tests/fixtures/fixdep/sample.d",
    "zigux/tests/fixtures/fixdep/sample.h",
    "zigux/tests/fixtures/fixdep/sample.rmeta",
    "zigux/tests/fixtures/fixdep/sample2-config.h",
    "zigux/tests/fixtures/fixdep/sample2.c",
    "zigux/tests/fixtures/fixdep/sample2.so",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation.d",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_comment_only.d",
    "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_concatenated.d",
    "zigux/tests/fixtures/fixdep/sample_concatenated_dep.h",
    "zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_concatenated_source.c",
    "zigux/tests/fixtures/fixdep/sample_concatenated_temp.c",
    "zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation.d",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_dep.so",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon.d",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_escaped_space.d",
    "zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_escaped_space_source.c",
    "zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
    "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_missing_dep_source.c",
    "zigux/tests/fixtures/fixdep/sample_multi_target.d",
    "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt",
    "zigux/tests/fixtures/fixdep/shared#config.h",
    "zigux/tests/fixtures/fixdep/shared:config.h",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")



def _sample_manifest(
    fixdep_support: list[object] | None = None,
    *,
    present_surfaces: object | None = None,
) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": (
            {"fixdep_support": list(EXPECTED_FIXDEP_SUPPORT)}
            if present_surfaces is None
            else present_surfaces
        ),
    }
    if fixdep_support is not None:
        payload["present_surfaces"] = {"fixdep_support": list(fixdep_support)}
    return json.dumps(payload, indent=2) + "\n"



def validate(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    fixdep_support = surfaces.get("fixdep_support")
    if not isinstance(fixdep_support, list):
        return ["invalid fixdep_support list"]

    issues: list[str] = []
    seen: set[str] = set()
    for index, entry in enumerate(fixdep_support):
        if not isinstance(entry, str):
            issues.append(f"invalid fixdep_support entry at index {index}: {entry!r}")
            continue
        if entry in seen:
            issues.append(f"duplicate fixdep_support entry: {entry}")
        seen.add(entry)

    if len(fixdep_support) != len(EXPECTED_FIXDEP_SUPPORT):
        issues.append(
            "fixdep_support count drift: "
            f"expected {len(EXPECTED_FIXDEP_SUPPORT)}, found {len(fixdep_support)}"
        )

    for index, expected in enumerate(EXPECTED_FIXDEP_SUPPORT):
        if index >= len(fixdep_support):
            issues.append(f"missing fixdep_support entry: {expected}")
            continue
        actual = fixdep_support[index]
        if actual != expected:
            issues.append(
                f"fixdep_support order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for rel in EXPECTED_FIXDEP_SUPPORT:
        if not (root / rel).is_file():
            issues.append(f"missing fixdep_support path: {rel}")

    return issues



def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for rel in EXPECTED_FIXDEP_SUPPORT:
        _write(root / rel, "present\n")



def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_fixdep_support_surface_") as temp_dir:
        root = Path(temp_dir)

        write_sample_root(root)
        issues = validate(root)
        if issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest([]))
        issues = validate(root)
        if (
            "fixdep_support count drift: expected 57, found 0" not in issues
            or "missing fixdep_support entry: scripts/zigux/check-phase2-fixdep-gate.py"
            not in issues
        ):
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected empty fixdep_support drift was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, _sample_manifest([123]))
        issues = validate(root)
        if "invalid fixdep_support entry at index 0: 123" not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid fixdep_support entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(
            root / MANIFEST_PATH,
            _sample_manifest(
                [
                    "scripts/zigux/check-phase2-fixdep-gate.py",
                    "scripts/zigux/check-phase2-fixdep-gate.py",
                ]
            ),
        )
        issues = validate(root)
        if "duplicate fixdep_support entry: scripts/zigux/check-phase2-fixdep-gate.py" not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected duplicate fixdep_support entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, _sample_manifest(present_surfaces="bad"))
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        manifest_entries = list(EXPECTED_FIXDEP_SUPPORT)
        manifest_entries[0], manifest_entries[1] = manifest_entries[1], manifest_entries[0]
        _write(root / MANIFEST_PATH, _sample_manifest(manifest_entries))
        issues = validate(root)
        if (
            "fixdep_support order drift at index 0: expected "
            "'scripts/zigux/check-phase2-fixdep-gate.py', found "
            "'scripts/zigux/check-fixdep-diff.py'"
        ) not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected fixdep_support order drift was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        (root / "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt").unlink()
        issues = validate(root)
        if (
            "missing fixdep_support path: "
            "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt"
        ) not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing fixdep_support path was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_FIXDEP_SUPPORT) + ["zigux/tests/fixtures/fixdep/extra.txt"]),
        )
        issues = validate(root)
        if "fixdep_support count drift: expected 57, found 58" not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected fixdep_support count drift was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","present_surfaces": }\n')
        issues = validate(root)
        if "invalid manifest json: Expecting value" not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if "missing manifest file: zigux/tests/fixtures/phase2_tool_manifest.json" not in issues:
            print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

    print("PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_SUPPORT_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 fixdep support surface."
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
        print("PHASE2_FIXDEP_SUPPORT_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_FIXDEP_SUPPORT_SURFACE=pass")
    print(f"PHASE2_FIXDEP_SUPPORT_SURFACE_COUNT={len(EXPECTED_FIXDEP_SUPPORT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
