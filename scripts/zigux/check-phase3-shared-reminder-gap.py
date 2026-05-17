#!/usr/bin/env python3
"""Fail-close the Phase 3 shared reminder gap note against current repo reality."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")

REQUIRED_NOTE_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now carries a bounded dev_t starter packet plus one focused helper-local err_ptr/xarray slice, but the shared tests-root and docs-root reminder surfaces still overclaim a broader ABI, export/UAPI, and validator packet as if it already ships",
    "PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback now confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig, while broader reminder surfaces still describe absent wider packet members and replay routes",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=narrow the Phase 3 section in zigux/tests/README.md and the docs-root Phase 3 summary in Documentation/zigux/README.md so they match the current starter packet plus helper-slice posture before any new slug-sanity or wider ABI reminder work",
    "issue `#325` remains the operational tracker for this broader reminder drift while the shared surfaces are narrowed one bounded slice at a time.",
)

CURRENT_PACKET_PATHS = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-errptr-xarray-slice.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("include/linux/zigux.h"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/helpers/err_ptr.zig"),
    Path("zigux/helpers/xa_value.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet_build.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig"),
)

SHARED_REMINDER_SURFACES = (
    Path("zigux/tests/README.md"),
    Path("Documentation/zigux/README.md"),
)

SAMPLED_MISSING_PATHS = (
    Path("include/zigux/abi.h"),
    Path("zigux/tests/phase3_export_uapi_layout.zig"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("zigux/kernel/export_shim.zig"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    note_path = repo_root / NOTE_PATH
    try:
        note_text = _read(note_path)
    except FileNotFoundError:
        return [f"missing repo file: {NOTE_PATH.as_posix()}"]

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"missing note marker: {marker}")

    for rel_path in CURRENT_PACKET_PATHS:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing current packet path: {rel_path.as_posix()}")

    for rel_path in SHARED_REMINDER_SURFACES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing shared reminder surface: {rel_path.as_posix()}")

    for rel_path in SAMPLED_MISSING_PATHS:
        if (repo_root / rel_path).exists():
            issues.append(f"sampled missing path unexpectedly present: {rel_path.as_posix()}")

    return issues


def _populate_repo(root: Path) -> None:
    _write(
        root / NOTE_PATH,
        "\n".join(
            (
                "# Phase 3 Shared Reminder Gap",
                "",
                "## Current Status",
                "",
                f"- `{REQUIRED_NOTE_MARKERS[0]}`",
                f"- `{REQUIRED_NOTE_MARKERS[1]}`",
                f"- `{REQUIRED_NOTE_MARKERS[2]}`",
                "",
                "## Directly Readable Current Packet",
                "",
                *[f"- `{path.as_posix()}`" for path in CURRENT_PACKET_PATHS],
                "",
                "## Remaining Broad Reminder Surfaces",
                "",
                "- `zigux/tests/README.md` still presents the broader ABI, export/UAPI, low-level-wrapper, and validator packet as if those reminder members and replay routes are all shipped current-`master` evidence.",
                "- `Documentation/zigux/README.md` still presents the broader ABI, export/UAPI, low-level-wrapper, catalog, and shared replay packet as if those wider reminder members already ship on current `master`.",
                f"- {REQUIRED_NOTE_MARKERS[3]}",
                "",
                "## Sampled Missing Wider Packet Members",
                "",
                *[f"- `{path.as_posix()}`" for path in SAMPLED_MISSING_PATHS],
            )
        )
        + "\n",
    )

    for rel_path in CURRENT_PACKET_PATHS + SHARED_REMINDER_SURFACES:
        _write(root / rel_path, "# synthetic\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_shared_gap_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        note_path = root / NOTE_PATH
        note_path.write_text(
            _read(note_path).replace(REQUIRED_NOTE_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = f"missing note marker: {REQUIRED_NOTE_MARKERS[0]}"
        if expected not in issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("expected missing lead marker was not reported")
            return 1

        _populate_repo(root)
        (root / CURRENT_PACKET_PATHS[-1]).unlink()
        issues = validate_repo(root)
        expected = (
            "missing current packet path: "
            + CURRENT_PACKET_PATHS[-1].as_posix()
        )
        if expected not in issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("expected missing starter packet path was not reported")
            return 1

        _populate_repo(root)
        _write(root / SAMPLED_MISSING_PATHS[0], "# synthetic unexpected\n")
        issues = validate_repo(root)
        expected = (
            "sampled missing path unexpectedly present: "
            + SAMPLED_MISSING_PATHS[0].as_posix()
        )
        if expected not in issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("expected unexpected sampled-missing path was not reported")
            return 1

        _populate_repo(root)
        (root / SHARED_REMINDER_SURFACES[1]).unlink()
        issues = validate_repo(root)
        expected = (
            "missing shared reminder surface: "
            + SHARED_REMINDER_SURFACES[1].as_posix()
        )
        if expected not in issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("expected missing shared reminder surface was not reported")
            return 1

    print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=pass")
    print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 shared reminder gap note."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 reminder-gap note",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_SHARED_REMINDER_GAP=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
