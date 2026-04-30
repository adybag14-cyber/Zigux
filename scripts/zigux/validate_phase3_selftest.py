from __future__ import annotations

import json
import tempfile
from pathlib import Path

from phase3_catalog import Phase3Paths, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub, shared_runner_gate_for_slug
from validate_phase3_core import (
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_SOURCE_MARKERS,
    select_slices,
    validate_abi_expected_fixture,
    validate_export_uapi_boundary,
    validate_manifest,
    validate_slices,
    validate_source_markers,
)


def _assert_source_marker_guard(
    root: Path,
    rel_path: str,
    missing_marker: str,
) -> None:
    markers = ABI_REQUIRED_SOURCE_MARKERS[rel_path]
    fixture_path = root / rel_path
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(
        "\n".join(markers) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    assert validate_source_markers(root, {rel_path: markers}) == []
    fixture_path.write_text(
        fixture_path.read_text(encoding="utf-8").replace(missing_marker, ""),
        encoding="utf-8",
        newline="\n",
    )
    assert validate_source_markers(root, {rel_path: markers}) == [
        f"source-marker: {rel_path} missing {missing_marker}"
    ]


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
        for path in (paths.docs_dir, paths.scripts_dir, paths.tests_dir, paths.fixtures_dir):
            path.mkdir(parents=True, exist_ok=True)

        fixture_dir = paths.fixtures_dir / "phase3_alpha"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        (paths.docs_dir / "phase3-alpha-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=alpha-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    shared_runner_gate_for_slug("alpha"),
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-alpha.py").write_text(
            render_wrapper_stub(), encoding="utf-8", newline="\n"
        )
        (paths.scripts_dir / "validate_phase3_core.py").write_text(
            "# alpha validator core\n", encoding="utf-8", newline="\n"
        )
        (paths.scripts_dir / "validate_phase3_selftest.py").write_text(
            "# alpha validator selftest\n", encoding="utf-8", newline="\n"
        )
        (paths.tests_dir / "phase3_alpha_dump.zig").write_text("// alpha dump\n", encoding="utf-8", newline="\n")
        (fixture_dir / "expected.json").write_text(
            json.dumps({"abi_version": 1, "constants": ABI_REQUIRED_EXPECTED_CONSTANTS, "structs": {}}),
            encoding="utf-8",
            newline="\n",
        )
        (fixture_dir / "phase3_alpha_c_harness.c").write_text("// alpha harness\n", encoding="utf-8", newline="\n")
        (paths.fixtures_dir / "phase3_alpha_manifest.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 3",
                    "status": "ready",
                    "slice": "alpha-slice",
                    "files": [
                        "Documentation/zigux/phase3-alpha-slice.md",
                        "scripts/zigux/validate_phase3_core.py",
                        "scripts/zigux/validate_phase3_selftest.py",
                        "zigux/tests/phase3_alpha_dump.zig",
                        "zigux/tests/fixtures/phase3_alpha/expected.json",
                        "zigux/tests/fixtures/phase3_alpha/phase3_alpha_c_harness.c",
                    ],
                    "file_count": 6,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        entries = discover_phase3_slices(paths)
        assert [entry.slug for entry in select_slices(entries, [])] == ["alpha"]
        assert [entry.slug for entry in select_slices(entries, ["alpha"])] == ["alpha"]
        try:
            select_slices(entries, ["missing"])
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug to fail")

        entry = entries[0]
        assert validate_manifest(entry) == []
        assert validate_manifest(
            entry,
            required_files=(
                "scripts/zigux/validate_phase3_core.py",
                "scripts/zigux/validate_phase3_selftest.py",
            ),
        ) == []
        assert validate_source_markers(root, {}) == []
        source_marker_fixture = root / "marker-fixture.zig"
        source_marker_fixture.write_text(
            "pub fn boundaryMarker() void {}\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {
                "marker-fixture.zig": (
                    "pub fn boundaryMarker() void {}",
                    "pub fn policyByteMarker() void {}",
                )
            },
        ) == ["source-marker: marker-fixture.zig missing pub fn policyByteMarker() void {}"]
        assert "zigux/tests/phase3_abi.zig" in ABI_REQUIRED_SOURCE_MARKERS
        _assert_source_marker_guard(
            root,
            "zigux/tests/phase3_abi.zig",
            "try std.testing.expect(uapi_version.isCanonical(header));",
        )
        _assert_source_marker_guard(
            root,
            "zigux/helpers/layout_assert.zig",
            'assertOffset(abi.InteropPolicy, "unsafe_scope", 2);',
        )
        _assert_source_marker_guard(
            root,
            "zigux/helpers/panic_policy.zig",
            "pub fn canReturnPolicyByte(panic_mode: u8) bool {",
        )
        _assert_source_marker_guard(
            root,
            "zigux/helpers/allocator_policy.zig",
            "pub fn requiresResetOnInitPolicyByte(allocator_mode: u8) bool {",
        )
        _assert_source_marker_guard(
            root,
            "zigux/unsafe/narrow.zig",
            'test "phase3 narrow unsafe scoped helpers reject misaligned addresses"',
        )
        export_uapi_check = root / "scripts/zigux/validate-phase3-export-uapi-survey.py"
        export_uapi_check.write_text(
            "#!/usr/bin/env python3\nprint('PHASE3_EXPORT_UAPI_SURVEY=pass')\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_export_uapi_boundary(root) == []
        export_uapi_check.write_text(
            "#!/usr/bin/env python3\n"
            "print('PHASE3_EXPORT_UAPI_SURVEY=fail')\n"
            "print('missing_survey_marker:PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig')\n",
            encoding="utf-8",
            newline="\n",
        )
        export_uapi_check.write_text(
            export_uapi_check.read_text(encoding="utf-8") + "raise SystemExit(1)\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_export_uapi_boundary(root) == [
            "export-uapi-gate: missing_survey_marker:PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig"
        ]
        assert validate_slices(
            root,
            entries,
            check_artifact_diff=False,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=False,
            zig_path=None,
        ) == []
        assert (paths.scripts_dir / "check-phase3-alpha.py").read_text(encoding="utf-8") == render_wrapper_stub()

        abi_root = root / "abi-fixture"
        (abi_root / "zigux/tests/fixtures/phase3_abi").mkdir(parents=True, exist_ok=True)
        (abi_root / "zigux/tests").mkdir(parents=True, exist_ok=True)
        (abi_root / "zigux/tests/phase3_abi.zig").write_text(
            'test "abi" {\n'
            "    comptime {\n"
            "        layout_assert.assertBoundaryHeaderLayout();\n"
            '        layout_assert.assertExportStatusLayout();\n'
            '        layout_assert.assertInteropPolicyLayout();\n'
            '        layout_assert.assertSize(abi.BitmapSummary, 16);\n'
            "    }\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        (abi_root / "zigux/tests/phase3_abi_dump.zig").write_text(
            'writeLayoutPrefix(writer, "zigux_boundary_header", 0, 0);\n'
            'writeLayoutPrefix(writer, "zigux_export_status", 0, 0);\n'
            'writeLayoutPrefix(writer, "zigux_interop_policy", 0, 0);\n'
            'writeLayoutPrefix(writer, "zigux_bitmap_summary", 0, 0);\n',
            encoding="utf-8",
            newline="\n",
        )
        (abi_root / "zigux/tests/fixtures/phase3_abi/expected.json").write_text(
            json.dumps(
                {
                    "abi_version": 1,
                    "constants": ABI_REQUIRED_EXPECTED_CONSTANTS,
                    "structs": {
                        "zigux_boundary_header": {},
                        "zigux_export_status": {},
                        "zigux_interop_policy": {},
                        "zigux_bitmap_summary": {},
                    },
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        (abi_root / "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c").write_text(
            '\\"zigux_boundary_header\\":{\\"size\\":%zu}\n'
            '\\"zigux_export_status\\":{\\"size\\":%zu}\n'
            '\\"zigux_interop_policy\\":{\\"size\\":%zu}\n'
            '\\"zigux_bitmap_summary\\":{\\"size\\":%zu}\n',
            encoding="utf-8",
            newline="\n",
        )
        assert validate_abi_expected_fixture(abi_root) == []

        (abi_root / "zigux/tests/phase3_abi_dump.zig").write_text(
            'writeLayoutPrefix(writer, "zigux_boundary_header", 0, 0);\n',
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_abi_expected_fixture(abi_root)
        assert any("only emits 1 layouts" in issue for issue in issues)

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    return 0
