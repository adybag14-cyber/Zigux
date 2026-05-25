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
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)

REQUIRED_PHONY_TARGETS = {
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


def read_json_dict(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing {label}: {path.as_posix()}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid {label} json: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid {label} root object")
    return payload


def sample_manifest(wrappers: list[str] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "make_wrappers": list(EXPECTED_WRAPPERS if wrappers is None else wrappers),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def sample_makefile(*, include_cross: bool = True) -> str:
    lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
        "",
        ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2 phase3-validate",
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
    if include_cross:
        lines.extend(["phase2-cross:", "\t@true", ""])
    lines.extend(
        [
            "phase2-genksyms:",
            "\t@true",
            "",
            "phase2-fixdep:",
            "\t@true",
            "",
            "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
            "\t@true",
            "",
            "phase2: phase2-validate",
            "\t@true",
            "",
        ]
    )
    return "\n".join(lines)


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    makefile_path = repo_root / MAKEFILE_PATH

    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]
    if not makefile_path.is_file():
        return [f"missing makefile: {MAKEFILE_PATH.as_posix()}"]

    manifest = read_json_dict(manifest_path, label="manifest file")
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    wrappers = surfaces.get("make_wrappers")
    if not isinstance(wrappers, list):
        return ["invalid make_wrappers list"]

    issues: list[str] = []
    string_entries: list[str] = []
    for index, entry in enumerate(wrappers):
        if not isinstance(entry, str):
            issues.append(f"invalid make_wrappers entry at index {index}: {entry!r}")
            continue
        string_entries.append(entry)

    seen: set[str] = set()
    for entry in string_entries:
        if entry in seen:
            issues.append(f"duplicate make_wrappers entry: {entry}")
        seen.add(entry)

    if len(wrappers) != len(EXPECTED_WRAPPERS):
        issues.append(
            "make_wrappers count drift: "
            f"expected {len(EXPECTED_WRAPPERS)}, found {len(wrappers)}"
        )

    for expected in EXPECTED_WRAPPERS:
        if expected not in string_entries:
            issues.append(f"missing make_wrappers entry: {expected}")

    for index, expected in enumerate(EXPECTED_WRAPPERS):
        if index >= len(wrappers):
            continue
        actual = wrappers[index]
        if actual != expected:
            issues.append(
                f"make_wrappers order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_WRAPPERS:
            issues.append(f"unexpected make_wrappers entry: {entry}")

    makefile_text = makefile_path.read_text(encoding="utf-8")
    present_phony_targets = phony_targets_present(makefile_text)
    for target in sorted(REQUIRED_PHONY_TARGETS):
        if target not in present_phony_targets:
            issues.append(f"missing phony target: {target}")

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
        write_text(root / MANIFEST_PATH, sample_manifest())
        write_text(root / MAKEFILE_PATH, sample_makefile())

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

        write_text(root / MANIFEST_PATH, sample_manifest())
        (root / MAKEFILE_PATH).unlink()
        issues = validate(root)
        if f"missing makefile: {MAKEFILE_PATH.as_posix()}" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing makefile was not reported")
            return 1
        case_count += 1

        write_text(root / MAKEFILE_PATH, sample_makefile())
        write_text(root / MANIFEST_PATH, "{\n")
        try:
            validate(root)
        except SystemExit as exc:
            if "invalid manifest file json:" not in str(exc):
                print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
                print("expected invalid manifest json was not reported")
                return 1
        else:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("invalid manifest json did not abort validation")
            return 1
        case_count += 1

        write_text(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": []}\n',
        )
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        write_text(root / MANIFEST_PATH, sample_manifest(list(EXPECTED_WRAPPERS[:-1])))
        issues = validate(root)
        if "missing make_wrappers entry: make -C zigux phase2" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing phase2 wrapper entry was not reported")
            return 1
        case_count += 1

        write_text(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"make_wrappers": ["zigux/Makefile", 17]}}\n',
        )
        issues = validate(root)
        if "invalid make_wrappers entry at index 1: 17" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected invalid make_wrappers entry type was not reported")
            return 1
        case_count += 1

        duplicate_wrappers = list(EXPECTED_WRAPPERS)
        duplicate_wrappers[-1] = duplicate_wrappers[-2]
        write_text(root / MANIFEST_PATH, sample_manifest(duplicate_wrappers))
        issues = validate(root)
        if "duplicate make_wrappers entry: make -C zigux phase2-validate" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected duplicate wrapper entry was not reported")
            return 1
        case_count += 1

        order_drift_wrappers = list(EXPECTED_WRAPPERS)
        order_drift_wrappers[3], order_drift_wrappers[4] = (
            order_drift_wrappers[4],
            order_drift_wrappers[3],
        )
        write_text(root / MANIFEST_PATH, sample_manifest(order_drift_wrappers))
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

        extra_wrappers = list(EXPECTED_WRAPPERS) + ["make -C zigux phase2-future"]
        write_text(root / MANIFEST_PATH, sample_manifest(extra_wrappers))
        issues = validate(root)
        if "unexpected make_wrappers entry: make -C zigux phase2-future" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected unexpected make_wrappers entry was not reported")
            return 1
        case_count += 1

        write_text(root / MANIFEST_PATH, sample_manifest())
        makefile_text = sample_makefile().replace(
            "phase2-cross ",
            "",
            1,
        )
        write_text(root / MAKEFILE_PATH, makefile_text)
        issues = validate(root)
        if "missing phony target: phase2-cross" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing phony target was not reported")
            return 1
        case_count += 1

        write_text(root / MAKEFILE_PATH, sample_makefile(include_cross=False))
        issues = validate(root)
        if "missing makefile line: phase2-cross:" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected missing phase2-cross target was not reported")
            return 1
        case_count += 1

        write_text(
            root / MAKEFILE_PATH,
            sample_makefile().replace(
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "phase2-validate: phase2-toolchain phase2-tools",
                1,
            ),
        )
        issues = validate(root)
        expected_validate_issue = (
            "missing makefile line: "
            "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig "
            "phase2-cross phase2-genksyms phase2-fixdep"
        )
        if expected_validate_issue not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected phase2-validate dependency drift was not reported")
            return 1
        case_count += 1

        write_text(
            root / MAKEFILE_PATH,
            sample_makefile() + "phase2-cross:\n\t@true\n",
        )
        issues = validate(root)
        if "duplicate makefile line: phase2-cross::count=2" not in issues:
            print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=fail")
            print("expected duplicate phase2-cross target was not reported")
            return 1
        case_count += 1

    print("PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_MAKE_WRAPPER_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    write_text(root / MANIFEST_PATH, sample_manifest())
    write_text(root / MAKEFILE_PATH, sample_makefile())


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
