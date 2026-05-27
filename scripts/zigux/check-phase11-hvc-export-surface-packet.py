#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC export-surface proof packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[0] if len(SELF_PATH.parents) > 0 else Path.cwd()

SURVEY_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
PROOF_PATH = "zigux/tests/phase11_hvc_export_surface_layout_proof.zig"
BUILD_PATH = "zigux/tests/phase11_hvc_export_surface_layout_build.zig"

SURVEY_MARKERS = (
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "focused export-surface proofs",
    "`zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
)

MATRIX_MARKERS = (
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "focused exported surface proofs",
    "`zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
)

PROOF_MARKERS = (
    "const HvcExportSurface = extern struct {",
    'try layout_assert.expectSize(HvcExportSurface, 72);',
    'try layout_assert.expectOffset(HvcExportSurface, "hvc_instantiate", 0);',
    'try layout_assert.expectOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    'assertExactType(@FieldType(HvcExportSurface, "hvc_alloc"), HvcAllocFn);',
    'try expectContains(hvc_header, "int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);");',
)

BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    'proof_module.addImport("hvc_console", hvc_console_module);',
    '.name = "phase11-hvc-export-surface-layout-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckError(f"missing required file: {relative_path}") from exc


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(root: Path, relative_path: str, markers: tuple[str, ...]) -> None:
    text = read_text(root, relative_path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{relative_path} is missing required marker: {marker!r}")


def validate(root: Path) -> None:
    require_markers(root, SURVEY_PATH, SURVEY_MARKERS)
    require_markers(root, MATRIX_PATH, MATRIX_MARKERS)
    require_markers(root, PROOF_PATH, PROOF_MARKERS)
    require_markers(root, BUILD_PATH, BUILD_MARKERS)


def build_fixture(root: Path) -> None:
    write_text(
        root,
        SURVEY_PATH,
        "\n".join(
            (
                "# survey",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "focused export-surface proofs",
                "`zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MATRIX_PATH,
        "\n".join(
            (
                "# matrix",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "focused exported surface proofs",
                "`zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        PROOF_PATH,
        "\n".join(
            (
                "const HvcExportSurface = extern struct {",
                'try layout_assert.expectSize(HvcExportSurface, 72);',
                'try layout_assert.expectOffset(HvcExportSurface, "hvc_instantiate", 0);',
                'try layout_assert.expectOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
                'assertExactType(@FieldType(HvcExportSurface, "hvc_alloc"), HvcAllocFn);',
                'try expectContains(hvc_header, "int hvc_instantiate(uint32_t vtermno, int index, const struct hv_ops *ops);");',
            )
        )
        + "\n",
    )
    write_text(
        root,
        BUILD_PATH,
        "\n".join(
            (
                '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
                'proof_module.addImport("hvc_console", hvc_console_module);',
                '.name = "phase11-hvc-export-surface-layout-proof",',
                'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
            )
        )
        + "\n",
    )


def expect_failure(root: Path, mutate, fragment: str) -> None:
    mutate(root)
    try:
        validate(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-export-surface-packet-"))
    cases = 0
    try:
        fixture = temp_dir / "fixture"
        build_fixture(fixture)
        validate(fixture)
        cases += 1

        mutations = (
            (SURVEY_PATH, SURVEY_MARKERS[2], "", SURVEY_PATH),
            (MATRIX_PATH, MATRIX_MARKERS[3], "", MATRIX_PATH),
            (PROOF_PATH, PROOF_MARKERS[1], "", PROOF_PATH),
            (BUILD_PATH, BUILD_MARKERS[2], "", BUILD_PATH),
        )
        for index, (relative_path, old, new, fragment) in enumerate(mutations, start=1):
            broken = temp_dir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(
                broken,
                lambda root, rel=relative_path, before=old, after=new: write_text(
                    root,
                    rel,
                    read_text(root, rel).replace(before, after, 1),
                ),
                fragment,
            )
            cases += 1

        missing = temp_dir / "missing"
        shutil.copytree(fixture, missing, dirs_exist_ok=True)
        expect_failure(missing, lambda root: (root / PROOF_PATH).unlink(), PROOF_PATH)
        cases += 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PHASE11_HVC_EXPORT_SURFACE_PACKET_SELF_TEST=pass")
    print(f"PHASE11_HVC_EXPORT_SURFACE_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 HVC export-surface proof packet for drift."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--write-sample-root",
        default="",
        help="Optional directory to populate with a passing sample packet tree.",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        if sample_root.exists():
            shutil.rmtree(sample_root)
        build_fixture(sample_root)
        print(f"PHASE11_HVC_EXPORT_SURFACE_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    try:
        validate(Path(args.root).resolve())
    except CheckError as exc:
        print(f"PHASE11_HVC_EXPORT_SURFACE_PACKET=fail: {exc}")
        return 1

    print("PHASE11_HVC_EXPORT_SURFACE_PACKET=pass")
    print("PHASE11_HVC_EXPORT_SURFACE_PACKET_FILE_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
