#!/usr/bin/env python3
"""Fail closed when the Phase 2 make-wrapper manifest surface drifts from zigux/Makefile."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_WRAPPERS = (
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

REQUIRED_MAKEFILE_LINES = (
    ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(wrappers: list[str] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "make_wrappers": list(EXPECTED_WRAPPERS if wrappers is None else wrappers),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def _sample_makefile(
    *,
    include_phony: bool = True,
    validate_line: str | None = None,
    include_phase2_cross: bool = True,
) -> str:
    lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
    ]
    if include_phony:
        lines.append(REQUIRED_MAKEFILE_LINES[0])
    lines.extend(
        [
            "",
            "phase2-toolchain:",
            "\t@true",
            "",
            "phase2-tools:",
            "\t@true",
            "",
            "phase2-kconfig:",
            "\t@true",
            "",
        ]
    )
    if include_phase2_cross:
        lines.extend(
            [
                "phase2-cross:",
                "\t@true",
                "",
            ]
        )
    lines.extend(
        [
            "phase2-genksyms:",
            "\t@true",
            "",
            "phase2-fixdep:",
            "\t@true",
            "",
            validate_line
            if validate_line is not None
            else REQUIRED_MAKEFILE_LINES[-2],
            "\t@true",
            "",
            REQUIRED_MAKEFILE_LINES[-1],
            "",
        ]
    )
    return "\n".join(lines)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    makefile_path = repo_root / MAKEFILE_PATH

    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]
    if not makefile_path.is_file():
        return [f"missing makefile: {MAKEFILE_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    issues: list[str] = []
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    wrappers = surfaces.get("make_wrappers")
    if not isinstance(wrappers, list):
        return ["invalid make_wrappers list"]

    seen: set[str] = set()
    for index, entry in enumerate(wrappers):
        if not isinstance(entry, str):
            issues.append(f"invalid make_wrappers entry at index {index}: {entry!r}")
            continue
        if entry in seen:
            issues.append(f"duplicate make_wrappers entry: {entry}")
        seen.add(entry)

    if len(wrappers) != len(EXPECTED_WRAPPERS):
        issues.append(
            "make_wrappers count drift: "
            f"expected {len(EXPECTED_WRAPPERS)}, found {len(wrappers)}"
        )

    for index, expected in enumerate(EXPECTED_WRAPPERS):
        if index >= len(wrappers):
            issues.append(f"missing make_wrappers entry: {expected}")
            continue
        actual = wrappers[index]
        if actual != expected:
            issues.append(
                f"make_wrappers order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    makefile_text = makefile_path.read_text(encoding="utf-8")
    for line in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, line)
        if count == 0:
            issues.append(f"missing makefile line: {line}")
        elif count != 1:
            issues.append(f"duplicate makefile line: {line}:count={count}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_make_wrapper_surface_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(root / MAKEFILE_PATH, _sample_makefile())

        issues = validate(root)
        if issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        (root / MAKEFILE_PATH).unlink()
        issues = validate(root)
        if f"missing makefile: {MAKEFILE_PATH.as_posix()}" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing makefile was not reported")
            return 1
        case_count += 1

        _write(root / MAKEFILE_PATH, _sample_makefile())
        _write(root / MANIFEST_PATH, '{"phase": "Phase 2",\n')
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "present_surfaces": []}\n')
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest(list(EXPECTED_WRAPPERS[:-1])))
        issues = validate(root)
        if "missing make_wrappers entry: make -C zigux phase2" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing phase2 wrapper entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"make_wrappers": ['
            '"zigux/Makefile", 17, "make -C zigux phase2-tools", '
            '"make -C zigux phase2-kconfig", "make -C zigux phase2-cross", '
            '"make -C zigux phase2-genksyms", "make -C zigux phase2-fixdep", '
            '"make -C zigux phase2-validate", "make -C zigux phase2"]}}\n',
        )
        issues = validate(root)
        if "invalid make_wrappers entry at index 1: 17" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected invalid make_wrappers entry type was not reported")
            return 1
        case_count += 1

        duplicate_wrappers = list(EXPECTED_WRAPPERS)
        duplicate_wrappers[-1] = EXPECTED_WRAPPERS[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_wrappers))
        issues = validate(root)
        duplicate_issue = "duplicate make_wrappers entry: make -C zigux phase2-validate"
        if duplicate_issue not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected duplicate phase2-validate wrapper entry was not reported")
            return 1
        case_count += 1

        order_drift_wrappers = list(EXPECTED_WRAPPERS)
        order_drift_wrappers[3], order_drift_wrappers[4] = (
            order_drift_wrappers[4],
            order_drift_wrappers[3],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(order_drift_wrappers))
        issues = validate(root)
        order_issue = (
            "make_wrappers order drift at index 3: "
            "expected 'make -C zigux phase2-kconfig', found 'make -C zigux phase2-cross'"
        )
        if order_issue not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected make_wrappers order drift was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, _sample_manifest())
        _write(
            root / MAKEFILE_PATH,
            _sample_makefile(include_phony=False),
        )
        issues = validate(root)
        if f"missing makefile line: {REQUIRED_MAKEFILE_LINES[0]}" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected phony-line drift was not reported")
            return 1
        case_count += 1

        _write(
            root / MAKEFILE_PATH,
            _sample_makefile(include_phase2_cross=False),
        )
        issues = validate(root)
        if "missing makefile line: phase2-cross:" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing phase2-cross target was not reported")
            return 1
        case_count += 1

        _write(
            root / MAKEFILE_PATH,
            _sample_makefile(validate_line="phase2-validate: phase2-toolchain phase2-tools"),
        )
        issues = validate(root)
        if f"missing makefile line: {REQUIRED_MAKEFILE_LINES[-2]}" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected phase2-validate dependency drift was not reported")
            return 1
        case_count += 1

        duplicate_makefile = _sample_makefile() + "\n" + REQUIRED_MAKEFILE_LINES[4] + "\n\t@true\n"
        _write(root / MAKEFILE_PATH, duplicate_makefile)
        issues = validate(root)
        if "duplicate makefile line: phase2-cross::count=2" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected duplicate phase2-cross target was not reported")
            return 1
        case_count += 1

        duplicate_phony = _sample_makefile() + "\n" + REQUIRED_MAKEFILE_LINES[0] + "\n"
        _write(root / MAKEFILE_PATH, duplicate_phony)
        issues = validate(root)
        if f"duplicate makefile line: {REQUIRED_MAKEFILE_LINES[0]}:count=2" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected duplicate phony line was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "present_surfaces": {"make_wrappers": "bad"}}\n')
        issues = validate(root)
        if "invalid make_wrappers list" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected invalid make_wrappers list was not reported")
            return 1
        case_count += 1

    print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / MAKEFILE_PATH, _sample_makefile())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 make-wrapper surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 2 manifest and zigux/Makefile",
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
        print("PHASE2_MAKE_WRAPPER_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_MAKE_WRAPPER_SURFACE=pass")
    print(f"PHASE2_MAKE_WRAPPER_SURFACE_COUNT={len(EXPECTED_WRAPPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
