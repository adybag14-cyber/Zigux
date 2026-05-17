#!/usr/bin/env python3
"""Fail-close the Phase 3 shared reminder gap note against current repo reality."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")

REQUIRED_NOTE_MARKERS = (
    "PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus one focused helper-local err_ptr/xarray slice aligned across the docs root, tests root, and dedicated Phase 3 support notes",
    "PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig; Documentation/zigux/README.md and zigux/tests/README.md now match that bounded posture on current master",
    "PHASE3_SHARED_REMINDER_NEXT_STEP=keep future shared Phase 3 follow-up anchored to the bounded starter packet and helper slice, and only reopen the broader reminder lane if new current-tree evidence lands or one of the shared summaries drifts again",
    "issue `#325` is closed because the docs-root and tests-root Phase 3 summaries now match the current-tree-backed starter packet.",
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

NOTE_TEXT = """# Phase 3 Shared Reminder Gap

This note records that the earlier shared Phase 3 reminder drift has been cleared on current `master` and keeps the bounded current packet explicit for future follow-up.

## Current Status

- `PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus one focused helper-local err_ptr/xarray slice aligned across the docs root, tests root, and dedicated Phase 3 support notes`
- `PHASE3_SHARED_REMINDER_GAP_DETAIL=direct current-head readback confirms the starter packet through Documentation/zigux/phase3-abi-slice.md, Documentation/zigux/phase3-validator-support-surface.md, include/linux/zigux.h, include/zigux/dev_t.h, zigux/uapi/version.zig, zigux/uapi/dev_t.zig, zigux/bindings/dev_t.zig, zigux/tests/phase3_dev_t_starter_packet.zig, and zigux/tests/phase3_dev_t_starter_packet_build.zig, plus the focused helper slice through Documentation/zigux/phase3-errptr-xarray-slice.md, zigux/helpers/err_ptr.zig, zigux/helpers/xa_value.zig, zigux/tests/phase3_errptr_xarray_starter_packet.zig, and zigux/tests/phase3_errptr_xarray_starter_packet_build.zig; Documentation/zigux/README.md and zigux/tests/README.md now match that bounded posture on current master`
- `PHASE3_SHARED_REMINDER_NEXT_STEP=keep future shared Phase 3 follow-up anchored to the bounded starter packet and helper slice, and only reopen the broader reminder lane if new current-tree evidence lands or one of the shared summaries drifts again`

## Directly Readable Current Packet

- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`

## Shared Reminder Surfaces

- `Documentation/zigux/README.md` now matches the bounded starter packet plus helper-local slice posture and no longer presents the broader validator, export/UAPI, low-level-wrapper, catalog, or shared replay packet as shipped current-`master` evidence.
- `zigux/tests/README.md` now matches the same bounded posture and keeps broader Phase 3 routes framed as repo-reality gaps.
- issue `#325` is closed because the docs-root and tests-root Phase 3 summaries now match the current-tree-backed starter packet.

## Sampled Missing Wider Packet Members

- `include/zigux/abi.h`
- `zigux/tests/phase3_export_uapi_layout.zig`
- `scripts/zigux/validate-phase3-export-uapi-survey.py`
- `zigux/kernel/export_shim.zig`

## Current Gap

The earlier shared Phase 3 reminder drift is cleared on current `master`. Dedicated Phase 3 notes, the docs root, and the tests root now all point at the same bounded `dev_t` starter packet plus the helper-local `err_ptr` / `xarray` slice, while sampled broader ABI, export/UAPI, low-level-wrapper, and validator routes remain explicitly parked as repo-reality gaps.

That means the next truthful step is not another reminder-surface cleanup pass. Future Phase 3 work should either materialize one of the wider sampled packet members or keep the current bounded packet aligned if a shared summary drifts again.

## Scope

This note is limited to the bounded current Phase 3 shared packet and the fact that the earlier shared reminder drift is now cleared. It records the directly readable starter packet, confirms that the docs-root and tests-root summaries are aligned, samples wider packet members that remain absent, and keeps the reopen condition explicit. It does not claim that the broader Phase 3 ABI, export/UAPI, low-level-wrapper, or validator packet has returned.
"""


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
    _write(root / NOTE_PATH, NOTE_TEXT)
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
        expected = "missing current packet path: " + CURRENT_PACKET_PATHS[-1].as_posix()
        if expected not in issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("expected missing starter packet path was not reported")
            return 1

        _populate_repo(root)
        _write(root / SAMPLED_MISSING_PATHS[0], "# synthetic unexpected\n")
        issues = validate_repo(root)
        expected = "sampled missing path unexpectedly present: " + SAMPLED_MISSING_PATHS[0].as_posix()
        if expected not in issues:
            print("PHASE3_SHARED_REMINDER_GAP_SELF_TEST=fail")
            print("expected unexpected sampled-missing path was not reported")
            return 1

        _populate_repo(root)
        (root / SHARED_REMINDER_SURFACES[1]).unlink()
        issues = validate_repo(root)
        expected = "missing shared reminder surface: " + SHARED_REMINDER_SURFACES[1].as_posix()
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
