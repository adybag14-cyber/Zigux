#!/usr/bin/env python3
"""Fail-closed survey for the Phase 11 ABI layout-assert boundary."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[3]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)

UAPI_SURVEY = Path("Documentation/zigux/phase11-uapi-header-parity-survey.md")
HV_OPS_PROOF = Path("zigux/tests/phase11_hvc_hv_ops_layout_proof.zig")
EXPORT_SURFACE_PROOF = Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig")
BUILD_INVENTORY = Path("zigux/tests/fixtures/phase11_build_inventory.json")

RETIRED_SHARED_REPLAY_PATHS = (
    Path("zigux/tests/phase11_uapi_header_parity_manifest.json"),
    Path("zigux/tests/phase11_uapi_header_parity_survey.zig"),
    Path("zigux/tests/phase11_build.zig"),
)

SURVEY_MARKERS = (
    "`zigux/helpers/layout_assert.zig`",
    "that narrower proof packet remains `layout_assert`-backed",
    "current `master` still lacks the broader shared ABI replay",
    "`phase11-shared-reminder-surface-gap`",
)

HV_OPS_PROOF_MARKERS = (
    'const layout_assert = @import("layout_assert");',
    "try layout_assert.expectSize(HvOps, 72);",
    'try layout_assert.expectOffset(HvOps, "dtr_rts", 64);',
    "try layout_assert.expectSize(hvc_console.HvOps, 72);",
    'try layout_assert.expectOffset(hvc_console.HvOps, "notifier_hangup", 40);',
    '@FieldType(hvc_console.HvOps, "notifier_hangup")',
)

EXPORT_PROOF_MARKERS = (
    'const layout_assert = @import("layout_assert");',
    "try layout_assert.expectSize(WinsizeLayout, 8);",
    'try layout_assert.expectOffset(WinsizeLayout, "ws_ypixel", 6);',
    'assertExactType(@FieldType(WinsizeLayout, "ws_row"), u16);',
    "try layout_assert.expectSize(HvcExportSurface, 72);",
    'try layout_assert.expectOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    "@TypeOf(hvc_console.notifier_hangup_irq)",
    "void notifier_hangup_irq(struct hvc_struct *hp, int irq);",
)

INVENTORY_MARKERS = (
    '"phase11-hvc-hv-ops-layout-proof-tests"',
    '"phase11-hvc-export-surface-layout-proof-tests"',
    '"zigux/tests/phase11_hvc_hv_ops_layout_build.zig"',
    '"zigux/tests/phase11_hvc_export_surface_layout_build.zig"',
)


class CheckError(Exception):
    pass


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    if not path.is_file():
        raise CheckError(f"missing_required_path:{relpath}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, relpath: Path, markers: tuple[str, ...]) -> None:
    text = read_text(root, relpath)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise CheckError(f"missing_marker:{relpath}:{missing[0]}")


def run_check(root: Path) -> None:
    require_markers(root, UAPI_SURVEY, SURVEY_MARKERS)
    require_markers(root, HV_OPS_PROOF, HV_OPS_PROOF_MARKERS)
    require_markers(root, EXPORT_SURFACE_PROOF, EXPORT_PROOF_MARKERS)
    require_markers(root, BUILD_INVENTORY, INVENTORY_MARKERS)

    for relpath in RETIRED_SHARED_REPLAY_PATHS:
        if (root / relpath).exists():
            raise CheckError(f"retired_shared_replay_returned:{relpath}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / UAPI_SURVEY,
        "\n".join(
            [
                "# Phase 11 UAPI Header Parity Survey",
                "- `zigux/helpers/layout_assert.zig`",
                "- that narrower proof packet remains `layout_assert`-backed",
                "- current `master` still lacks the broader shared ABI replay",
                "- `phase11-shared-reminder-surface-gap`",
                "",
            ]
        ),
    )
    write(root / HV_OPS_PROOF, "\n".join(HV_OPS_PROOF_MARKERS) + "\n")
    write(root / EXPORT_SURFACE_PROOF, "\n".join(EXPORT_PROOF_MARKERS) + "\n")
    write(root / BUILD_INVENTORY, "\n".join(INVENTORY_MARKERS) + "\n")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11-layout-assert-gap-survey-"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        cases = (
            (UAPI_SURVEY, "current `master` still lacks the broader shared ABI replay", "missing_marker"),
            (HV_OPS_PROOF, "try layout_assert.expectSize(HvOps, 72);", "missing_marker"),
            (EXPORT_SURFACE_PROOF, 'assertExactType(@FieldType(WinsizeLayout, "ws_row"), u16);', "missing_marker"),
            (EXPORT_SURFACE_PROOF, 'try layout_assert.expectOffset(HvcExportSurface, "notifier_hangup_irq", 64);', "missing_marker"),
            (BUILD_INVENTORY, '"phase11-hvc-export-surface-layout-proof-tests"', "missing_marker"),
        )
        for relpath, marker, expected in cases:
            case_root = tmpdir / f"case-{case_count}"
            shutil.copytree(fixture, case_root)
            text = (case_root / relpath).read_text(encoding="utf-8")
            write(case_root / relpath, text.replace(marker, "", 1))
            try:
                run_check(case_root)
            except CheckError as exc:
                if expected not in str(exc):
                    raise SystemExit(f"phase11-layout-assert-gap-survey-self-test:wrong_error:{exc}")
            else:
                raise SystemExit("phase11-layout-assert-gap-survey-self-test:expected_failure_missing")
            case_count += 1

        returned_route = tmpdir / "returned-route"
        shutil.copytree(fixture, returned_route)
        write(returned_route / RETIRED_SHARED_REPLAY_PATHS[0], "{}\n")
        try:
            run_check(returned_route)
        except CheckError as exc:
            if "retired_shared_replay_returned" not in str(exc):
                raise SystemExit(f"phase11-layout-assert-gap-survey-self-test:wrong_error:{exc}")
        else:
            raise SystemExit("phase11-layout-assert-gap-survey-self-test:expected_retired_route_failure")
        case_count += 1

        print("PHASE11_LAYOUT_ASSERT_GAP_SURVEY_SELF_TEST=pass")
        print(f"PHASE11_LAYOUT_ASSERT_GAP_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_LAYOUT_ASSERT_GAP_SURVEY=fail: {exc}")
        return 1

    print("PHASE11_LAYOUT_ASSERT_GAP_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())