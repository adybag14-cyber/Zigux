#!/usr/bin/env python3
"""Check the focused Phase 3 ABI support packet under the shared manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
REQUIRED_SUPPORT_FILES = (
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing repo file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid phase3 ABI manifest JSON: {exc.msg}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return ["invalid phase3 ABI manifest files list"]

    file_entries = {
        entry for entry in files if isinstance(entry, str)
    }
    for rel_path in REQUIRED_SUPPORT_FILES:
        rel = rel_path.as_posix()
        if rel not in file_entries:
            issues.append(f"missing phase3 ABI support manifest entry: {rel}")
            continue
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing manifest-tracked repo file: {rel}")

    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_payload(files: list[str]) -> str:
    payload = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files),
        "files": files,
    }
    return json.dumps(payload, indent=2) + "\n"


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_SUPPORT_FILES:
        _write(root / rel_path, "# stub\n")
    _write(
        root / MANIFEST_PATH,
        _manifest_payload([rel_path.as_posix() for rel_path in REQUIRED_SUPPORT_FILES]),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_support_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for rel_path in REQUIRED_SUPPORT_FILES:
            _populate_repo(root)
            manifest = json.loads(_read(root / MANIFEST_PATH))
            manifest["files"] = [
                entry for entry in manifest["files"] if entry != rel_path.as_posix()
            ]
            manifest["file_count"] = len(manifest["files"])
            _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(root)
            expected = f"missing phase3 ABI support manifest entry: {rel_path.as_posix()}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print("expected missing manifest entry was not reported")
                return 1

        for rel_path in REQUIRED_SUPPORT_FILES:
            _populate_repo(root)
            (root / rel_path).unlink()
            issues = validate_repo(root)
            expected = f"missing manifest-tracked repo file: {rel_path.as_posix()}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print("expected missing manifest-tracked repo file was not reported")
                return 1

    print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass")
    print(f"PHASE3_ABI_SUPPORT_PACKET_COUNT={len(REQUIRED_SUPPORT_FILES)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 ABI support packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ABI manifest",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_SUPPORT_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
