from __future__ import annotations

import json
import tempfile
from pathlib import Path

from phase3_catalog import Phase3Paths, Phase3Slice, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub, shared_runner_gate_for_slug
from validate_phase3_core import (
    ABI_REQUIRED_DOC_MARKERS,
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_SOURCE_MARKERS,
    build_smoke_commands,
    select_slices,
    validate_abi_expected_fixture,
    validate_export_uapi_boundary,
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
        assert build_smoke_commands(entry) == (("phase3-alpha-dump", "zigux/tests/build.zig"),)
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
        assert (
            "PHASE3_MMIO_SCOPE=range-read8-read16-read32-write8-write16-write32-plus-scoped-read8-write8-read16-write16-read32-write32"
            in ABI_REQUIRED_DOC_MARKERS
        )
        assert (
            "PHASE3_MMIO_SCOPE=range-read16-read32-write16-write32-plus-scoped-read16-write16-read32-write32"
            not in ABI_REQUIRED_DOC_MARKERS
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
        abi_marker_fixture = root / "zigux/tests/phase3_abi.zig"
        abi_marker_fixture.parent.mkdir(parents=True, exist_ok=True)
        abi_marker_fixture.write_text(
            "\n".join(
                [
                    'test "phase3 abi slice uses stable canonical layouts" {',
                    "    comptime {",
                    "        layout_assert.assertMmioRangeLayout();",
                    "    }",
                    "}",
                    "",
                    'test "phase3 abi slice keeps explicit constants and statuses reviewable" {',
                    "    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));",
                    "}",
                    "",
                    'test "phase3 abi slice keeps the boundary helpers constructible" {',
                    "    try std.testing.expect(export_shim.isCanonicalHeader(header));",
                    "    try std.testing.expect(uapi_version.isCanonical(header));",
                    "    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));",
                    "    try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));",
                    "    const range = mmio.range(0x1000, 0x40, 4);",
                    "    try std.testing.expectEqual(narrow.UnsafeScopeTag.raw_pointer_bridge, narrow.scopeFromInteropPolicyBytes(2, 0).?);",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {"zigux/tests/phase3_abi.zig": ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_abi.zig"]},
        ) == []
        abi_marker_fixture.write_text(
            abi_marker_fixture.read_text(encoding="utf-8").replace(
                "try std.testing.expect(uapi_version.isCanonical(header));",
                "",
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {"zigux/tests/phase3_abi.zig": ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_abi.zig"]},
        ) == [
            "source-marker: zigux/tests/phase3_abi.zig missing try std.testing.expect(uapi_version.isCanonical(header));"
        ]
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

        beta_fixture_dir = paths.fixtures_dir / "phase3_beta"
        beta_fixture_dir.mkdir(parents=True, exist_ok=True)
        (paths.docs_dir / "phase3-beta-slice.md").write_text(
            "\n".join(
                [
                    "PHASE3_STATUS=ready",
                    "PHASE3_SLICE=beta-slice",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                    shared_runner_gate_for_slug("beta"),
                    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.scripts_dir / "check-phase3-beta.py").write_text(
            render_wrapper_stub(), encoding="utf-8", newline="\n"
        )
        (paths.tests_dir / "phase3_beta_dump.zig").write_text("// beta dump\n", encoding="utf-8", newline="\n")
        (beta_fixture_dir / "expected.json").writeText if False else None
