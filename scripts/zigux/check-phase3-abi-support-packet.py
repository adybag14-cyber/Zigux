#!/usr/bin/env python3
"""Fail-close the adjacent support surfaces around the shared Phase 3 ABI packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_NOTE_MARKERS = (
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase3-abi-support-packet.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
)

REQUIRED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": (
        "shared ABI bindings, directly coupled helper decoding, header-family "
        "follow-through, notifier layouts, export-status layout, and "
        "header-compatibility replay"
    ),
    "next_safe_step": (
        "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet "
        "aligned with the dedicated replay routes and only reopen this manifest if the "
        "checker, focused builds, or reminder surfaces drift again"
    ),
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "scripts/zigux/check-phase3-abi-support-packet.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "zigux/tests/phase3_export_uapi_c_header_smoke.c",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zigux/tests/phase3_export_shim_build.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/Makefile",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-abi-support-packet.py",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-export-uapi-survey.py",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test",
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-low-level-wrappers-test",
)

SUPPORT_GAP_PATHS = set(REQUIRED_PACKET_FILES) - {
    "Documentation/zigux/phase3-abi-slice.md",
    "zigux/tests/build.zig",
    "zigux/tests/README.md",
    "zigux/Makefile",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    note_path = repo_root / NOTE_PATH
    manifest_path = repo_root / MANIFEST_PATH

    if not note_path.is_file():
        issues.append(f"missing repo file: {NOTE_PATH.as_posix()}")
    else:
        note_text = _read(note_path)
        for marker in REQUIRED_NOTE_MARKERS:
            if marker not in note_text:
                issues.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")

    if not manifest_path.is_file():
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                f"phase3_abi_manifest.json wrong {field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json packet_files", packet_files, issues
        )
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(
                    f"phase3_abi_manifest.json missing packet_files entry: {entry}"
                )

    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase3_abi_manifest.json replay_routes", replay_routes, issues
        )
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(
                    f"phase3_abi_manifest.json missing replay route: {entry}"
                )

    if not isinstance(repo_reality_gaps, list):
        issues.append("phase3_abi_manifest.json repo_reality_gaps is not a list")
    else:
        for gap in repo_reality_gaps:
            if gap in SUPPORT_GAP_PATHS:
                issues.append(
                    "phase3_abi_manifest.json misclassified support path as repo gap: "
                    f"{gap}"
                )

    return issues


def _sample_manifest() -> dict[str, object]:
    return {
        "phase": REQUIRED_MANIFEST_FIELDS["phase"],
        "lane": REQUIRED_MANIFEST_FIELDS["lane"],
        "slug": REQUIRED_MANIFEST_FIELDS["slug"],
        "status": REQUIRED_MANIFEST_FIELDS["status"],
        "scope": REQUIRED_MANIFEST_FIELDS["scope"],
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        "repo_reality_gaps": [],
        "next_safe_step": REQUIRED_MANIFEST_FIELDS["next_safe_step"],
    }


def _populate_repo(root: Path) -> None:
    _write(root / NOTE_PATH, "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    _write(root / MANIFEST_PATH, json.dumps(_sample_manifest(), indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_support_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        note_cases = (
            "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
            "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
            "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
            "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
            "make -C zigux phase3-low-level-wrappers-test",
        )
        for marker in note_cases:
            _populate_repo(root)
            note_path = root / NOTE_PATH
            _write(note_path, _read(note_path).replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {NOTE_PATH.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print(f"expected missing note marker was not reported: {expected}")
                return 1

        manifest_packet_cases = (
            "scripts/zigux/phase3_catalog.py",
            "scripts/zigux/check-phase3-abi-support-packet.py",
            "zigux/tests/phase3_export_shim_build.zig",
            "zigux/tests/phase3_low_level_wrappers_build.zig",
        )
        for entry in manifest_packet_cases:
            _populate_repo(root)
            manifest_path = root / MANIFEST_PATH
            manifest = json.loads(_read(manifest_path))
            manifest["packet_files"].remove(entry)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(root)
            expected = f"phase3_abi_manifest.json missing packet_files entry: {entry}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print(f"expected missing packet file was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["packet_files"].append("scripts/zigux/phase3_catalog.py")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json packet_files duplicate entry: "
            "'scripts/zigux/phase3_catalog.py' (first index 6, duplicate index 27)"
        )
        if expected not in issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("expected duplicate packet file entry was not reported")
            return 1

        manifest_route_cases = (
            "python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test",
            "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
            "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
            "make -C zigux phase3-low-level-wrappers-test",
        )
        for entry in manifest_route_cases:
            _populate_repo(root)
            manifest_path = root / MANIFEST_PATH
            manifest = json.loads(_read(manifest_path))
            manifest["replay_routes"].remove(entry)
            _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
            issues = validate_repo(root)
            expected = f"phase3_abi_manifest.json missing replay route: {entry}"
            if expected not in issues:
                print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
                print(f"expected missing replay route was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append("python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test")
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json replay_routes duplicate entry: "
            "'python3 scripts/zigux/check-phase3-abi-support-packet.py --self-test' "
            "(first index 0, duplicate index 20)"
        )
        if expected not in issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("expected duplicate replay route entry was not reported")
            return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = ["scripts/zigux/phase3_catalog.py"]
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json misclassified support path as repo gap: "
            "scripts/zigux/phase3_catalog.py"
        )
        if expected not in issues:
            print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=fail")
            print("expected repo-reality gap misclassification was not reported")
            return 1

    case_count = 4 + len(note_cases) + len(manifest_packet_cases) + len(manifest_route_cases)
    print("PHASE3_ABI_SUPPORT_PACKET_SELF_TEST=pass")
    print(f"PHASE3_ABI_SUPPORT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the adjacent support surfaces around the shared Phase 3 ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 ABI packet",
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
