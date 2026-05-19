#!/usr/bin/env python3
"""Fail-close the adjacent support surfaces for the shared Phase 3 ABI packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ABI_SLICE_NOTE = Path("Documentation/zigux/phase3-abi-slice.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_SUPPORT_FILES = (
    Path("Documentation/zigux/phase3-bindings-governance.md"),
    Path("Documentation/zigux/phase3-abi-bindings-survey.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    MANIFEST_PATH,
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
)

REQUIRED_SLICE_MARKERS = (
    "Documentation/zigux/phase3-bindings-governance.md",
    "Documentation/zigux/phase3-abi-bindings-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/zigux/dev_t.h",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
)

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "include/zigux/abi.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump_current.zig",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    slice_note_path = repo_root / ABI_SLICE_NOTE
    if not slice_note_path.is_file():
        issues.append(f"missing repo file: {ABI_SLICE_NOTE.as_posix()}")
        slice_text = None
    else:
        slice_text = _read(slice_note_path)

    for rel_path in REQUIRED_SUPPORT_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    if slice_text is not None:
        for marker in REQUIRED_SLICE_MARKERS:
            if marker not in slice_text:
                issues.append(
                    f"missing {ABI_SLICE_NOTE.as_posix()} marker: {marker}"
                )

    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return issues

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid phase3 ABI manifest JSON: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                "phase3_abi_manifest.json wrong "
                f"{field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for rel_path in REQUIRED_PACKET_FILES:
            if rel_path not in packet_files:
                issues.append(
                    "phase3_abi_manifest.json missing packet_files entry: "
                    f"{rel_path}"
                )

    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    else:
        for rel_path in REQUIRED_SUPPORT_FILES:
            rel = rel_path.as_posix()
            if rel in repo_reality_gaps:
                issues.append(
                    "phase3_abi_manifest.json misclassifies support file as a repo gap: "
                    f"{rel}"
                )

    return issues


def _manifest_payload(
    packet_files: list[str] | None = None,
    repo_reality_gaps: list[str] | None = None,
) -> str:
    payload = {
        "phase": "Phase 3",
        "lane": "abi-runtime",
        "slug": "phase3-abi-packet",
        "status": "shared_abi_binding_surface_present",
        "scope": "shared ABI bindings, notifier layouts, export-status layout, and header-compatibility replay",
        "packet_files": list(REQUIRED_PACKET_FILES if packet_files is None else packet_files),
        "replay_routes": [
            "python3 scripts/zigux/check-phase3-abi.py --self-test",
            "python3 scripts/zigux/check-phase3-abi.py",
            "zig build phase3-abi-core-packet --build-file zigux/tests/build.zig",
            "zig build phase3-dump --build-file zigux/tests/build.zig",
        ],
        "repo_reality_gaps": list(
            ["scripts/zigux/check-phase3-catalog-selftest.py"]
            if repo_reality_gaps is None
            else repo_reality_gaps
        ),
        "next_safe_step": "keep the shared ABI packet bounded to manifest-backed binding parity, dump-route reviewability, and directly coupled header-to-binding checks before widening into broader Phase 3 catalog or export/UAPI survey work",
    }
    return json.dumps(payload, indent=2) + "\n"


def _populate_repo(root: Path) -> None:
    _write(root / ABI_SLICE_NOTE, "\n".join(REQUIRED_SLICE_MARKERS) + "\n")
    for rel_path in REQUIRED_SUPPORT_FILES:
        if rel_path == MANIFEST_PATH:
            continue
        _write(root / rel_path, "# stub\n")
    _write(root / MANIFEST_PATH, _manifest_payload())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_support_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker in REQUIRED_SLICE_MARKERS:
            _populate_repo(root)
            _write(
                root / ABI_SLICE_NOTE,
                _read(root / ABI_SLICE_NOTE).replace(marker, "", 1),
            )
            issues = validate_repo(root)
            expected = f"missing {ABI_SLICE_NOTE.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print("expected missing slice marker was not reported")
                return 1

        for rel_path in REQUIRED_SUPPORT_FILES:
            _populate_repo(root)
            if rel_path == MANIFEST_PATH:
                manifest = json.loads(_read(root / MANIFEST_PATH))
                manifest["repo_reality_gaps"].append(
                    "zigux/bindings/notifier_abi.zig"
                )
                _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
                issues = validate_repo(root)
                expected = (
                    "phase3_abi_manifest.json misclassifies support file as a repo gap: "
                    "zigux/bindings/notifier_abi.zig"
                )
                if expected not in issues:
                    print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                    print("expected support-file repo-gap drift was not reported")
                    return 1
                continue

            (root / rel_path).unlink()
            issues = validate_repo(root)
            expected = f"missing repo file: {rel_path.as_posix()}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print("expected missing support file was not reported")
                return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"] = [
            entry
            for entry in manifest["packet_files"]
            if entry != "zigux/tests/phase3_abi_dump_current.zig"
        ]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing packet_files entry: "
            "zigux/tests/phase3_abi_dump_current.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("expected missing packet_files entry was not reported")
            return 1

    print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass")
    print(
        "PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT="
        f"{len(REQUIRED_SLICE_MARKERS) + len(REQUIRED_SUPPORT_FILES) + 1}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the adjacent support surfaces for the shared Phase 3 ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 ABI packet and support surfaces",
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

    print("PHASE3_ABI_SUPPORT_PACKET=pass")
    print("PHASE3_ABI_SUPPORT_SCOPE=adjacent-shared-abi-support-surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
