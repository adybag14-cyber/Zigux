#!/usr/bin/env python3
"""Audit the shipped Phase 3 starter export/UAPI packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
SLICE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
README_PATH = Path("scripts/zigux/README.md")

STARTER_PACKET_FILES = (
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("zigux/tests/phase3_export_uapi_layout_build.zig"),
    Path("zigux/tests/phase3_export_uapi_layout.zig"),
)

README_MARKERS = (
    "validate-phase3-export-uapi-survey.py",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "include/zigux/dev_t.h",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(root: Path) -> list[str]:
    issues: list[str] = []

    required_files = (MANIFEST_PATH, SLICE_PATH, README_PATH, *STARTER_PACKET_FILES)
    for rel_path in required_files:
        if not (root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    manifest_path = root / MANIFEST_PATH
    if manifest_path.is_file():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid phase3 ABI manifest JSON: {exc.msg}")
        else:
            files = manifest.get("files")
            if not isinstance(files, list):
                issues.append("invalid phase3 ABI manifest files list")
            else:
                file_count = manifest.get("file_count")
                if isinstance(file_count, int) and file_count != len(files):
                    issues.append(
                        f"phase3 ABI manifest file_count drift: expected {len(files)}, found {file_count}"
                    )
                file_entries = {entry for entry in files if isinstance(entry, str)}
                for rel_path in STARTER_PACKET_FILES:
                    rel = rel_path.as_posix()
                    if rel not in file_entries:
                        issues.append(f"missing starter packet manifest entry: {rel}")

    slice_path = root / SLICE_PATH
    if slice_path.is_file():
        slice_text = _read(slice_path)
        for rel_path in STARTER_PACKET_FILES:
            marker = rel_path.as_posix()
            if marker not in slice_text:
                issues.append(f"missing phase3 abi slice marker: {marker}")

    readme_path = root / README_PATH
    if readme_path.is_file():
        readme_text = _read(readme_path)
        for marker in README_MARKERS:
            if marker not in readme_text:
                issues.append(f"missing scripts README marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    manifest_files = [rel_path.as_posix() for rel_path in STARTER_PACKET_FILES]
    for rel_path in STARTER_PACKET_FILES:
        _write(root / rel_path, "# stub\n")
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "phase": "Phase 3",
                "status": "active",
                "slice": "abi-substrate-skeleton",
                "file_count": len(manifest_files),
                "files": manifest_files,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / SLICE_PATH,
        "\n".join(rel_path.as_posix() for rel_path in STARTER_PACKET_FILES) + "\n",
    )
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_starter_uapi_packet_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        missing_file = Path("zigux/bindings/notifier_abi.zig")
        (root / missing_file).unlink()
        issues = validate_repo(root)
        expected_missing_file = f"missing repo file: {missing_file.as_posix()}"
        if expected_missing_file not in issues:
            print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=fail")
            print("expected missing starter packet file was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["files"].remove("zigux/uapi/version.zig")
        manifest["file_count"] = len(manifest["files"])
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_manifest_issue = "missing starter packet manifest entry: zigux/uapi/version.zig"
        if expected_manifest_issue not in issues:
            print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=fail")
            print("expected missing starter packet manifest entry was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        _write(
            root / SLICE_PATH,
            _read(root / SLICE_PATH).replace("include/zigux/dev_t.h\n", "", 1),
        )
        issues = validate_repo(root)
        expected_slice_issue = "missing phase3 abi slice marker: include/zigux/dev_t.h"
        if expected_slice_issue not in issues:
            print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=fail")
            print("expected missing Phase 3 ABI slice marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        _write(
            root / README_PATH,
            _read(root / README_PATH).replace("zigux/uapi/dev_t.zig\n", "", 1),
        )
        issues = validate_repo(root)
        expected_readme_issue = "missing scripts README marker: zigux/uapi/dev_t.zig"
        if expected_readme_issue not in issues:
            print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=fail")
            print("expected missing scripts README marker was not reported")
            return 1
        case_count += 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["file_count"] = manifest["file_count"] + 1
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_count_issue = (
            f"phase3 ABI manifest file_count drift: expected {len(manifest['files'])}, found {len(manifest['files']) + 1}"
        )
        if expected_count_issue not in issues:
            print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=fail")
            print("expected manifest file_count drift was not reported")
            return 1
        case_count += 1

    print("PHASE3_STARTER_UAPI_PACKET_SELF_TEST=pass")
    print(f"PHASE3_STARTER_UAPI_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the shipped Phase 3 starter export/UAPI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root that contains Documentation/, scripts/, include/, and zigux/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_STARTER_UAPI_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_STARTER_UAPI_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
