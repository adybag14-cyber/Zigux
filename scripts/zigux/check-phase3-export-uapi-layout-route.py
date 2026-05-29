#!/usr/bin/env python3
"""Validate the focused Phase 3 export/UAPI layout build routes."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
LAYOUT_BUILD_PATH = Path("zigux/tests/phase3_export_uapi_layout_build.zig")

SHARED_FUNCTION = "fn addPhase3ExportUapiLayout("
NEXT_FUNCTION = "\nfn addPhase3LowLevelWrappers("
HEADER_MODULE = 'const header_family_binding = b.createModule(.{'
HEADER_IMPORT = 'root_module.addImport("header_family_binding", header_family_binding);'
EXPORT_IMPORT = 'root_module.addImport("export_shim", export_shim);'
SHARED_STEP = '"phase3-export-uapi-layout"'
DEDICATED_STEP = '"phase3-export-uapi-layout-test"'


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _extract_shared_layout_function(text: str) -> str | None:
    start = text.find(SHARED_FUNCTION)
    if start == -1:
        return None
    end = text.find(NEXT_FUNCTION, start)
    if end == -1:
        return text[start:]
    return text[start:end]


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    tests_build = repo_root / TESTS_BUILD_PATH
    try:
        shared_text = _read(tests_build)
    except FileNotFoundError:
        return [f"missing repo file: {TESTS_BUILD_PATH.as_posix()}"]

    shared_function = _extract_shared_layout_function(shared_text)
    if shared_function is None:
        issues.append(
            f"missing {TESTS_BUILD_PATH.as_posix()} function: addPhase3ExportUapiLayout"
        )
    else:
        for marker in (HEADER_MODULE, HEADER_IMPORT, EXPORT_IMPORT, SHARED_STEP):
            if marker not in shared_function:
                issues.append(
                    "missing scoped export/UAPI layout route marker in "
                    f"{TESTS_BUILD_PATH.as_posix()}: {marker}"
                )

    dedicated_build = repo_root / LAYOUT_BUILD_PATH
    try:
        dedicated_text = _read(dedicated_build)
    except FileNotFoundError:
        issues.append(f"missing repo file: {LAYOUT_BUILD_PATH.as_posix()}")
    else:
        for marker in (HEADER_MODULE, HEADER_IMPORT, EXPORT_IMPORT, DEDICATED_STEP):
            if marker not in dedicated_text:
                issues.append(
                    f"missing dedicated export/UAPI layout marker in {LAYOUT_BUILD_PATH.as_posix()}: {marker}"
                )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_layout_route_") as temp_dir:
        root = Path(temp_dir)
        shared_text = f"""
const std = @import("std");

fn addPhase3ExportUapiLayout() void {{
    {HEADER_MODULE}
    }});
    {HEADER_IMPORT}
    {EXPORT_IMPORT}
    const step = {SHARED_STEP};
}}

fn addPhase3LowLevelWrappers() void {{}}
"""
        dedicated_text = f"""
const std = @import("std");

pub fn build() void {{
    {HEADER_MODULE}
    }});
    {HEADER_IMPORT}
    {EXPORT_IMPORT}
    const step = {DEDICATED_STEP};
}}
"""

        _write(root / TESTS_BUILD_PATH, shared_text)
        _write(root / LAYOUT_BUILD_PATH, dedicated_text)
        issues = validate_repo(root)
        if issues:
            print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        _write(root / TESTS_BUILD_PATH, shared_text.replace(HEADER_IMPORT, "", 1))
        issues = validate_repo(root)
        expected = (
            "missing scoped export/UAPI layout route marker in "
            f"{TESTS_BUILD_PATH.as_posix()}: {HEADER_IMPORT}"
        )
        if expected not in issues:
            print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE_SELF_TEST=fail")
            print("expected missing shared scoped header-family import to fail validation")
            return 1

        _write(root / TESTS_BUILD_PATH, shared_text.replace(NEXT_FUNCTION, "", 1))
        _write(root / LAYOUT_BUILD_PATH, dedicated_text.replace(HEADER_IMPORT, "", 1))
        issues = validate_repo(root)
        expected = (
            f"missing dedicated export/UAPI layout marker in {LAYOUT_BUILD_PATH.as_posix()}: "
            f"{HEADER_IMPORT}"
        )
        if expected not in issues:
            print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE_SELF_TEST=fail")
            print("expected missing dedicated header-family import to fail validation")
            return 1

    print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE_SELF_TEST_CASES=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 export/UAPI layout build routes."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains zigux/tests/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TESTS_BUILD_PATH}")
    print(f"validated {args.repo_root / LAYOUT_BUILD_PATH}")
    print("PHASE3_EXPORT_UAPI_LAYOUT_ROUTE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
