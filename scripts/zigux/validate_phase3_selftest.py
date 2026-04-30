from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validate_phase3_core import (
    ABI_REQUIRED_DOC_MARKERS,
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_MANIFEST_FILES,
    ABI_REQUIRED_SOURCE_MARKERS,
    Phase3Paths,
    discover_phase3_slices,
    render_wrapper_stub,
    validate_abi_expected_fixture,
    validate_manifest,
    validate_slices,
    validate_source_markers,
)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_validator_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        paths = Phase3Paths(
            root=root,
            docs_dir=root / "Documentation" / "zigux",
            scripts_dir=root / "scripts" / "zigux",
            tests_dir=root / "zigux" / "tests",
            fixtures_dir=root / "zigux" / "tests" / "fixtures",
        )
        fixture_dir = paths.fixtures_dir / "phase3_alpha"
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, fixture_dir):
            path.mkdir(parents=True, exist_ok=True)

        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_alpha_dump.zig").write_text("// alpha dump\n", encoding="utf-8", newline="\n")
        (fixture_dir / "expected.json").write_text("{}", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_c_harness.c").write_text("// alpha harness\n", encoding="utf-8", newline="\n")
        (fixture_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-slice",
                    "files": [
                        "Documentation/zigux/phase3-alpha-slice.md",
                        "zigux/tests/phase3_alpha_dump.zig",
                        "zigux/tests/fixtures/phase3_alpha/expected.json",
                        "zigux/tests/fixtures/phase3_alpha/phase3_alpha_c_harness.c",
                    ],
                    "file_count": 4,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.docs_dir / "phase3-beta-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=beta-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug beta",
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        beta_fixture_dir = paths.fixtures_dir / "phase3_beta"
        beta_fixture_dir.mkdir(parents=True, exist_ok=True)
        (paths.tests_dir / "phase3_beta_dump.zig").write_text("// beta dump\n", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "expected.json").write_text("{}", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "phase3_beta_c_harness.c").write_text("// beta harness\n", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "phase3_beta_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "beta-slice",
                    "files": [
                        "Documentation/zigux/phase3-beta-slice.md",
                        "zigux/tests/phase3_beta_dump.zig",
                        "zigux/tests/fixtures/phase3_beta/expected.json",
                        "zigux/tests/fixtures/phase3_beta/phase3_beta_c_harness.c",
                    ],
                    "file_count": 4,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )

        for rel in ABI_REQUIRED_MANIFEST_FILES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("// abi boundary\n", encoding="utf-8", newline="\n")

        (root / "zigux" / "helpers" / "layout_assert.zig").write_text(
            'test "phase3 layout assertions cover canonical bindings" {\n'
            '    comptime {\n'
            '        assertOffset(abi.InteropPolicy, "unsafe_scope", 2);\n'
            "    }\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "kernel" / "export_shim.zig").write_text(
            "pub fn header(flags: u16) abi.BoundaryHeader {\n"
            "    _ = flags;\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn isCompatibleHeader(boundary_header: abi.BoundaryHeader) bool {\n"
            "    _ = boundary_header;\n"
            "    return true;\n"
            "}\n\n"
            "pub fn isCanonicalHeader(boundary_header: abi.BoundaryHeader) bool {\n"
            "    _ = boundary_header;\n"
            "    return true;\n"
            "}\n\n"
            "pub fn normalize(status: abi.ExportStatus) abi.ExportStatus {\n"
            "    return status;\n"
            "}\n\n"
            'test "phase3 export shim keeps failure encoding explicit" {}\n'
            'test "phase3 export shim normalizes explicit status decoding" {}\n'
            'test "phase3 export shim separates canonical headers from broader compatibility" {}\n',
            encoding="utf-8",
            newline="\n",
        )
        (root / "zigux" / "uapi" / "version.zig").write_text(
            "pub const abi_version: u16 = abi.ABI_VERSION;\n\n"
            "pub fn boundaryHeader(flags: u16) Header {\n"
            "    _ = flags;\n"
            "    return undefined;\n"
            "}\n\n"
            "pub fn isCompatible(header: Header) bool {\n"
            "    _ = header;\n"
            "    return true;\n"
            "}\n\n"
            "pub fn isCanonical(header: Header) bool {\n"
            "    _ = header;\n"
            "    return true;\n"
            "}\n\n"
            'test "phase3 uapi version follows abi version" {}\n'
            'test "phase3 uapi boundary header stays explicit and compatible" {}\n'
            'test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {}\n',
            encoding="utf-8",
            newline="\n",
        )