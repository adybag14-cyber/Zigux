#!/usr/bin/env python3
"""Fail-closed checker for the focused Phase 11 HVC exported-helper proof companion."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


REQUIRED_FILES = {
    "note": Path("Documentation/zigux/phase11-hvc-export-surface-proof-note.md"),
    "proof": Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig"),
    "build": Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
}

NOTE_MARKERS = [
    "`PHASE11_HVC_EXPORT_SURFACE_PROOF_STATUS=companion_proof_landed`",
    "lane continuity: `P11-L16`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "does not replace `zigux/tests/phase11_hvc_console_survey.zig`",
    "size `72` with alignment `8`",
    "`notifier_hangup_irq`",
    "does not claim that the dedicated proof already runs through `make -C zigux phase11-hvc-survey`",
]

PROOF_MARKERS = [
    'test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {',
    "layout_assert.assertSize(HvcExportSurface, 72);",
    "layout_assert.assertAlign(HvcExportSurface, 8);",
    'layout_assert.assertOffset(HvcExportSurface, "hvc_instantiate", 0);',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    'test "phase11 HVC exported helper proof keeps exported helper signatures exact" {',
    'assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);',
]

BUILD_MARKERS = [
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    '.name = "phase11-hvc-export-surface-layout-proof",',
    'b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def require_markers(path: Path, markers: list[str]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"missing marker in {path}: {marker}")


def check(root: Path) -> None:
    for relpath in REQUIRED_FILES.values():
        if not (root / relpath).is_file():
            raise SystemExit(f"missing required file: {root / relpath}")
    require_markers(root / REQUIRED_FILES["note"], NOTE_MARKERS)
    require_markers(root / REQUIRED_FILES["proof"], PROOF_MARKERS)
    require_markers(root / REQUIRED_FILES["build"], BUILD_MARKERS)


def write_fixture(root: Path) -> None:
    for relpath in REQUIRED_FILES.values():
        (root / relpath).parent.mkdir(parents=True, exist_ok=True)

    (root / REQUIRED_FILES["note"]).write_text(
        "\n".join(
            [
                "# Phase 11 HVC Exported-Helper Proof Note",
                "",
                "* `PHASE11_HVC_EXPORT_SURFACE_PROOF_STATUS=companion_proof_landed`",
                "* lane continuity: `P11-L16`",
                "* proof source: `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "* focused build route: `zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "* relationship to the archival survey packet: this proof stays a direct HVC companion and does not replace `zigux/tests/phase11_hvc_console_survey.zig`",
                "* the exported `hvc_*` surface keeps `HvcExportSurface` at size `72` with alignment `8`",
                "* the focused proof also keeps the exported helper signatures exact through `notifier_hangup_irq`",
                "* this note does not claim that the dedicated proof already runs through `make -C zigux phase11-hvc-survey`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (root / REQUIRED_FILES["proof"]).write_text(
        "\n".join(
            [
                'test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {',
                "    layout_assert.assertSize(HvcExportSurface, 72);",
                "    layout_assert.assertAlign(HvcExportSurface, 8);",
                '    layout_assert.assertOffset(HvcExportSurface, "hvc_instantiate", 0);',
                '    layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
                "}",
                'test "phase11 HVC exported helper proof keeps exported helper signatures exact" {',
                '    assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);',
                "}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (root / REQUIRED_FILES["build"]).write_text(
        "\n".join(
            [
                'const proof_module = b.createModule(.{',
                '    .root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
                '});',
                'const proof_tests = b.addTest(.{',
                '    .name = "phase11-hvc-export-surface-layout-proof",',
                '});',
                'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_fixture(root)
        check(root)
        cases += 1

        broken = root / REQUIRED_FILES["note"]
        broken.write_text(broken.read_text(encoding="utf-8").replace("`P11-L16`", "`P11-L99`"), encoding="utf-8")
        try:
            check(root)
        except SystemExit as exc:
            if "missing marker" not in str(exc):
                raise
            cases += 1
        else:
            raise SystemExit("expected note marker failure")

        write_fixture(root)
        broken = root / REQUIRED_FILES["proof"]
        broken.write_text(broken.read_text(encoding="utf-8").replace("72", "71", 1), encoding="utf-8")
        try:
            check(root)
        except SystemExit as exc:
            if "missing marker" not in str(exc):
                raise
            cases += 1
        else:
            raise SystemExit("expected proof marker failure")

        write_fixture(root)
        (root / REQUIRED_FILES["build"]).unlink()
        try:
            check(root)
        except SystemExit as exc:
            if "missing required file" not in str(exc):
                raise
            cases += 1
        else:
            raise SystemExit("expected missing build failure")

    print("PHASE11_HVC_EXPORT_SURFACE_PROOF_NOTE_SELF_TEST=pass")
    print(f"PHASE11_HVC_EXPORT_SURFACE_PROOF_NOTE_SELF_TEST_CASE_COUNT={cases}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    check(args.root)
    print("PHASE11_HVC_EXPORT_SURFACE_PROOF_NOTE_CHECK=pass")


if __name__ == "__main__":
    main()
