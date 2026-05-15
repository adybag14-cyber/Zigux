#!/usr/bin/env python3
"""Fail-close the core Phase 3 ABI manifest anchor set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_CORE_ENTRIES = (
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3.py",
    "Documentation/zigux/phase3-abi-slice.md",
    "zigux/Makefile",
)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(repo_root: Path) -> list[str]:
    manifest_path = repo_root / ABI_MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing ABI manifest: {ABI_MANIFEST_PATH.as_posix()}"]

    try:
        payload = _read_json(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"invalid ABI manifest JSON: {exc.msg}"]

    if not isinstance(payload, dict):
        return ["invalid ABI manifest payload"]

    files = payload.get("files")
    if not isinstance(files, list):
        return ["invalid ABI manifest files list"]

    issues: list[str] = []
    file_count = payload.get("file_count")
    if isinstance(file_count, int) and file_count != len(files):
        issues.append(
            f"phase3 ABI manifest file_count drift: expected {len(files)}, found {file_count}"
        )

    seen: dict[str, int] = {}
    for index, entry in enumerate(files, start=1):
        if not isinstance(entry, str):
            issues.append(f"invalid ABI manifest file entry: {entry!r}")
            continue
        previous = seen.get(entry)
        if previous is None:
            seen[entry] = index
            continue
        issues.append(
            "duplicate ABI manifest entry: "
            f"{entry} (first index {previous}, duplicate index {index})"
        )

    for entry in REQUIRED_CORE_ENTRIES:
        if entry not in seen:
            issues.append(f"missing ABI manifest core entry: {entry}")

    return issues


def _write_manifest(root: Path, files: list[object], file_count: int | None = None) -> None:
    payload = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files) if file_count is None else file_count,
        "files": files,
    }
    path = root / ABI_MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    baseline = list(REQUIRED_CORE_ENTRIES) + [
        "Documentation/zigux/phase3-validator-support-surface.md",
        "scripts/zigux/validate-phase3-validator-support-surface.py",
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_manifest_core_") as temp_dir:
        root = Path(temp_dir)

        _write_manifest(root, baseline)
        issues = validate_manifest(root)
        if issues:
            print("PHASE3_ABI_MANIFEST_CORE_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        broken = [entry for entry in baseline if entry != "zigux/kernel/export_shim.zig"]
        _write_manifest(root, broken)
        issues = validate_manifest(root)
        expected = "missing ABI manifest core entry: zigux/kernel/export_shim.zig"
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_CORE_SURFACE_SELF_TEST=fail")
            print("expected missing export shim anchor was not reported")
            return 1

        duplicated = baseline + ["zigux/bindings/abi.zig"]
        _write_manifest(root, duplicated)
        issues = validate_manifest(root)
        expected = (
            "duplicate ABI manifest entry: zigux/bindings/abi.zig "
            "(first index 3, duplicate index 24)"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_CORE_SURFACE_SELF_TEST=fail")
            print("expected duplicate manifest anchor was not reported")
            return 1

        malformed = list(baseline)
        malformed[0] = 42
        _write_manifest(root, malformed)
        issues = validate_manifest(root)
        expected = "invalid ABI manifest file entry: 42"
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_CORE_SURFACE_SELF_TEST=fail")
            print("expected non-string manifest entry was not reported")
            return 1

        _write_manifest(root, baseline, file_count=len(baseline) - 2)
        issues = validate_manifest(root)
        expected = (
            f"phase3 ABI manifest file_count drift: expected {len(baseline)}, "
            f"found {len(baseline) - 2}"
        )
        if expected not in issues:
            print("PHASE3_ABI_MANIFEST_CORE_SURFACE_SELF_TEST=fail")
            print("expected manifest file_count drift was not reported")
            return 1

    print("PHASE3_ABI_MANIFEST_CORE_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the core Phase 3 ABI manifest anchor set."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains zigux/tests/fixtures/phase3_abi_manifest.json",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_manifest(args.repo_root)
    if issues:
        print("PHASE3_ABI_MANIFEST_CORE_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / ABI_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
