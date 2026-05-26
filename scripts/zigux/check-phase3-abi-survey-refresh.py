#!/usr/bin/env python3
"""Fail-close the shared Phase 3 ABI survey-refresh packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
CATALOG_PATH = Path("scripts/zigux/phase3_catalog.py")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

DOC_MARKERS = (
    "## 2026-05-26 Survey Refresh",
    "bounded Phase 3 bitmap/cpumask, list/hlist, err_ptr/xarray, and xarray-slot interop survey packet members",
    "`Documentation/zigux/phase3-bitmap-cpumask-slice.md`",
    "`zigux/helpers/bitmap_view.zig`",
    "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
    "`Documentation/zigux/phase3-list-hlist-slice.md`",
    "`zigux/helpers/list_view.zig`",
    "`scripts/zigux/check-phase3-list-hlist-starter-packet.py`",
    "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
    "`zigux/helpers/err_ptr.zig`",
    "`scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`",
    "`Documentation/zigux/phase3-xarray-slot-slice.md`",
    "`zigux/helpers/xarray_slot_view.zig`",
    "`scripts/zigux/check-phase3-xarray-slot-starter-packet.py`",
    "`scripts/zigux/check-phase3-xarray-slot.py`",
)

CATALOG_MARKERS = (
    '"Documentation/zigux/phase3-bitmap-cpumask-slice.md"',
    '"zigux/helpers/bitmap_view.zig"',
    '"zigux/helpers/cpumask_view.zig"',
    '"zigux/tests/phase3_bitmap_cpumask_starter_packet.zig"',
    '"scripts/zigux/check-phase3-bitmap-cpumask.py"',
    '"Documentation/zigux/phase3-list-hlist-slice.md"',
    '"zigux/helpers/list_view.zig"',
    '"zigux/helpers/hlist_view.zig"',
    '"zigux/tests/phase3_list_hlist_starter_packet.zig"',
    '"scripts/zigux/check-phase3-list-hlist-starter-packet.py"',
    '"Documentation/zigux/phase3-errptr-xarray-slice.md"',
    '"zigux/helpers/err_ptr.zig"',
    '"zigux/helpers/xa_value.zig"',
    '"zigux/tests/phase3_errptr_xarray_starter_packet.zig"',
    '"zigux/tests/phase3_errptr_xarray_dump.zig"',
    '"scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"',
    '"Documentation/zigux/phase3-xarray-slot-slice.md"',
    '"zigux/helpers/xarray_slot_view.zig"',
    '"zigux/tests/phase3_xarray_slot_starter_packet.zig"',
    '"zigux/tests/phase3_xarray_slot_dump.zig"',
    '"scripts/zigux/check-phase3-xarray-slot-starter-packet.py"',
    '"scripts/zigux/check-phase3-xarray-slot.py"',
    '"python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test"',
    '"python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test"',
    '"python3 scripts/zigux/check-phase3-xarray-slot.py --self-test"',
    '"zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig"',
    '"zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig"',
    '"zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig"',
    '"zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig"',
    '"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig"',
)

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-bitmap-cpumask-slice.md",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet.zig",
    "zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json",
    "scripts/zigux/check-phase3-bitmap-cpumask.py",
    "Documentation/zigux/phase3-list-hlist-slice.md",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/tests/phase3_list_hlist_starter_packet.zig",
    "zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zigux/tests/fixtures/phase3_list_hlist_manifest.json",
    "scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_manifest.json",
    "zigux/tests/phase3_errptr_xarray_dump.zig",
    "zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "Documentation/zigux/phase3-xarray-slot-slice.md",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_dump.zig",
    "zigux/tests/phase3_xarray_slot_dump_build.zig",
    "zigux/tests/fixtures/phase3_xarray_slot_manifest.json",
    "scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "scripts/zigux/check-phase3-xarray-slot.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test",
    "python3 scripts/zigux/check-phase3-bitmap-cpumask.py",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-list-hlist-starter-packet.py",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot-starter-packet.py",
    "python3 scripts/zigux/check-phase3-xarray-slot.py --self-test",
    "python3 scripts/zigux/check-phase3-xarray-slot.py",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
)

SAMPLE_MANIFEST = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-abi-packet",
    "status": "shared_abi_and_header_family_binding_surface_present",
    "scope": "shared ABI bindings, directly coupled helper decoding, header-family follow-through, notifier layouts, export-status layout, and header-compatibility replay",
    "packet_files": list(REQUIRED_PACKET_FILES),
    "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    "repo_reality_gaps": [],
    "next_safe_step": "keep the shared Phase 3 policy, export/UAPI, and low-level wrapper packet aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _missing_marker_issues(path: Path, markers: tuple[str, ...], text: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"missing {path.as_posix()} marker: {marker}")
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = repo_root / DOC_PATH
    catalog_path = repo_root / CATALOG_PATH
    manifest_path = repo_root / MANIFEST_PATH

    for path in (doc_path, catalog_path, manifest_path):
        if not path.is_file():
            issues.append(f"missing repo file: {path.relative_to(repo_root).as_posix()}")
    if issues:
        return issues

    issues.extend(_missing_marker_issues(DOC_PATH, DOC_MARKERS, _read(doc_path)))
    issues.extend(_missing_marker_issues(CATALOG_PATH, CATALOG_MARKERS, _read(catalog_path)))

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")

    if not isinstance(packet_files, list):
        issues.append("phase3_abi_manifest.json packet_files is not a list")
    else:
        for entry in REQUIRED_PACKET_FILES:
            if entry not in packet_files:
                issues.append(f"phase3_abi_manifest.json missing packet_files entry: {entry}")

    if not isinstance(replay_routes, list):
        issues.append("phase3_abi_manifest.json replay_routes is not a list")
    else:
        for entry in REQUIRED_REPLAY_ROUTES:
            if entry not in replay_routes:
                issues.append(f"phase3_abi_manifest.json missing replay route: {entry}")

    if repo_reality_gaps != []:
        issues.append(
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared survey-refresh packet"
        )

    return issues


def _populate_repo(root: Path) -> None:
    _write(root / DOC_PATH, "\n".join(DOC_MARKERS) + "\n")
    _write(root / CATALOG_PATH, "\n".join(CATALOG_MARKERS) + "\n")
    _write(root / MANIFEST_PATH, json.dumps(SAMPLE_MANIFEST, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_survey_refresh_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                DOC_PATH,
                "`scripts/zigux/check-phase3-bitmap-cpumask.py`",
                "missing Documentation/zigux/phase3-abi-slice.md marker: `scripts/zigux/check-phase3-bitmap-cpumask.py`",
            ),
            (
                CATALOG_PATH,
                '"zigux/tests/phase3_errptr_xarray_dump.zig"',
                'missing scripts/zigux/phase3_catalog.py marker: "zigux/tests/phase3_errptr_xarray_dump.zig"',
            ),
        )

        for relative_path, marker, expected in cases:
            _populate_repo(root)
            path = root / relative_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["packet_files"].remove("zigux/helpers/xarray_slot_view.zig")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase3_abi_manifest.json missing packet_files entry: zigux/helpers/xarray_slot_view.zig"
        if expected not in issues:
            print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=fail")
            print("expected xarray-slot packet-file drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["replay_routes"].remove(
            "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig"
        )
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json missing replay route: "
            "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig"
        )
        if expected not in issues:
            print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=fail")
            print("expected list/hlist replay drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["repo_reality_gaps"] = ["stale-gap"]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_abi_manifest.json repo_reality_gaps drifted from the current shared survey-refresh packet"
        )
        if expected not in issues:
            print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=fail")
            print("expected repo_reality_gaps drift was not reported")
            return 1

    print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=pass")
    print("PHASE3_ABI_SURVEY_REFRESH_SELF_TEST_CASE_COUNT=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 3 ABI survey-refresh packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 ABI survey-refresh packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_SURVEY_REFRESH=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_ABI_SURVEY_REFRESH=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
