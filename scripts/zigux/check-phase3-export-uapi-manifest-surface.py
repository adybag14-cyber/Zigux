#!/usr/bin/env python3
"""Fail closed when the Phase 3 ABI manifest drifts from the shipped export/UAPI starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
REQUIRED_EXPORT_UAPI_MANIFEST_ENTRIES = (
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("include/linux/zigux.h"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_payload(files: list[str], file_count: int | None = None) -> str:
    payload = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files) if file_count is None else file_count,
        "files": files,
    }
    return json.dumps(payload, indent=2) + "\n"


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / ABI_MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {ABI_MANIFEST_PATH.as_posix()}"]

    issues: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return ["invalid manifest files list"]

    file_count = manifest.get("file_count")
    if isinstance(file_count, int) and file_count != len(files):
        issues.append(f"manifest file_count drift: expected {len(files)}, found {file_count}")

    entries: set[str] = set()
    for entry in files:
        if not isinstance(entry, str):
            issues.append(f"invalid manifest entry: {entry!r}")
            continue
        entries.add(entry)
        if not (repo_root / entry).is_file():
            issues.append(f"missing manifest-tracked repo file: {entry}")

    for rel_path in REQUIRED_EXPORT_UAPI_MANIFEST_ENTRIES:
        if rel_path.as_posix() not in entries:
            issues.append(f"missing export/uapi manifest entry: {rel_path.as_posix()}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_manifest_") as temp_dir:
        root = Path(temp_dir)
        all_files = [rel.as_posix() for rel in REQUIRED_EXPORT_UAPI_MANIFEST_ENTRIES]
        for rel_path in REQUIRED_EXPORT_UAPI_MANIFEST_ENTRIES:
            _write(root / rel_path, "# stub\n")
        _write(root / ABI_MANIFEST_PATH, _manifest_payload(all_files))

        issues = validate(root)
        if issues:
            print("PHASE3_EXPORT_UAPI_MANIFEST_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        _write(root / ABI_MANIFEST_PATH, _manifest_payload(all_files[1:]))
        issues = validate(root)
        expected_missing = (
            "missing export/uapi manifest entry: "
            "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
        )
        if expected_missing not in issues:
            print("PHASE3_EXPORT_UAPI_MANIFEST_SURFACE_SELF_TEST=fail")
            print("expected survey-manifest drift was not reported")
            return 1
        case_count += 1

        _write(root / ABI_MANIFEST_PATH, _manifest_payload(all_files, file_count=2))
        issues = validate(root)
        expected_count_drift = (
            f"manifest file_count drift: expected {len(all_files)}, found 2"
        )
        if expected_count_drift not in issues:
            print("PHASE3_EXPORT_UAPI_MANIFEST_SURFACE_SELF_TEST=fail")
            print("expected manifest file_count drift was not reported")
            return 1
        case_count += 1

        _write(root / ABI_MANIFEST_PATH, _manifest_payload(all_files))
        (root / "include/zigux/dev_t.h").unlink()
        issues = validate(root)
        expected_tracked_missing = "missing manifest-tracked repo file: include/zigux/dev_t.h"
        if expected_tracked_missing not in issues:
            print("PHASE3_EXPORT_UAPI_MANIFEST_SURFACE_SELF_TEST=fail")
            print("expected tracked dev_t header drift was not reported")
            return 1
        case_count += 1

    print("PHASE3_EXPORT_UAPI_MANIFEST_SURFACE_SELF_TEST=pass")
    print(f"PHASE3_EXPORT_UAPI_MANIFEST_SURFACE_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 3 export/UAPI starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shipped Phase 3 ABI manifest",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.repo_root)
    if issues:
        print("PHASE3_EXPORT_UAPI_MANIFEST_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / ABI_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
