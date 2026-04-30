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
        (beta_fixture_dir / "expected.json").write_text(
            json.dumps({"abi_version": 1, "constants": ABI_REQUIRED_EXPECTED_CONSTANTS, "structs": {}}),
            encoding="utf-8",
            newline="\n",
        )
        (beta_fixture_dir / "phase3_beta_c_harness.c").write_text("// beta harness\n", encoding="utf-8", newline="\n")
        (paths.fixtures_dir / "phase3_beta_manifest.json").write_text(
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
        (paths.docs_dir / "artifact-diff.md").write_text(
            "\n".join(
                [
                    "Current Phase 3 use",
                    "- `zigux/tests/fixtures/phase3_alpha/expected.json` anchors the bounded Phase 3 alpha parity claim.",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug alpha` compares that committed JSON fixture against both the bounded C harness and the Zig alpha dump.",
                    "- `zigux/tests/fixtures/phase3_beta/expected.json` anchors the bounded Phase 3 beta parity claim.",
                    "- `python3 scripts/zigux/run-phase3-checks.py --slug beta` compares that committed JSON fixture against both the bounded C harness and the Zig beta dump.",
                    "",
                    "Rules",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        refreshed_entries = discover_phase3_slices(paths)
        alpha_entry = select_slices(refreshed_entries, ["alpha"])
        assert validate_slices(
            root,
            alpha_entry,
            check_artifact_diff=False,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=True,
            zig_path=None,
        ) == []

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

        (paths.tests_dir / "phase3_policy_unsafe.zig").write_text(
            "const abi = @import(\"abi_bindings\");\n"
            "const allocator_policy = @import(\"allocator_policy\");\n"
            "const narrow = @import(\"narrow_unsafe\");\n"
            "const panic_policy = @import(\"panic_policy\");\n"
            "const std = @import(\"std\");\n\n"
            'test "phase3 policy helpers stay ABI aligned" {\n'
            "    _ = panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn));\n"
            "    _ = allocator_policy.permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap));\n"
            "    _ = allocator_policy.requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena));\n"
            "}\n"
            'test "phase3 policy decoder validates the whole interop record" {}\n'
            'test "phase3 policy decoder rejects partial or reserved policy bytes" {}\n'
            'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly" {}\n'
            'test "phase3 policy gate enforces the declared unsafe scope" {\n'
            "    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedPointerAt(u32, .none, base, 0));\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstSliceAt(u32, .volatile_mmio, base, 1));\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstPointerAt(u32, .volatile_mmio, base));\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        policy_unsafe_drift_issues = validate_source_markers(
            root,
            {"zigux/tests/phase3_policy_unsafe.zig": ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_policy_unsafe.zig"]},
        )
        assert policy_unsafe_drift_issues == [
            "source-marker: zigux/tests/phase3_policy_unsafe.zig missing const invalid_scope_policy = abi.InteropPolicy{",
            "source-marker: zigux/tests/phase3_policy_unsafe.zig missing const reserved_policy = abi.InteropPolicy{",
            "source-marker: zigux/tests/phase3_policy_unsafe.zig missing try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));",
            "source-marker: zigux/tests/phase3_policy_unsafe.zig missing try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));",
        ]
        (paths.tests_dir / "phase3_policy_unsafe.zig").write_text(
            "const abi = @import(\"abi_bindings\");\n"
            "const narrow = @import(\"narrow_unsafe\");\n"
            "const std = @import(\"std\");\n\n"
            'test "phase3 policy helpers stay ABI aligned" {\n'
            "    _ = panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn));\n"
            "    _ = allocator_policy.permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap));\n"
            "    _ = allocator_policy.requiresResetOnInitPolicyByte(@intFromEnum(abi.AllocatorMode.arena));\n"
            "}\n"
            'test "phase3 policy decoder validates the whole interop record" {}\n'
            'test "phase3 policy decoder rejects partial or reserved policy bytes" {}\n'
            'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly" {\n'
            "    const invalid_scope_policy = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 9, .reserved = 0 };\n"
            "    const reserved_policy = abi.InteropPolicy{ .panic_mode = 0, .allocator_mode = 0, .unsafe_scope = 0, .reserved = 1 };\n"
            "    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));\n"
            "    try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));\n"
            "}\n"
            'test "phase3 policy gate enforces the declared unsafe scope" {\n'
            "    const base: usize = 0;\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedPointerAt(u32, .none, base, 0));\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstSliceAt(u32, .volatile_mmio, base, 1));\n"
            "    try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstPointerAt(u32, .volatile_mmio, base));\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_policy_unsafe_build.zig").write_text(
            'const phase3_policy_unsafe_step = b.step("phase3-policy-unsafe-test", "Run focused Phase 3 policy and unsafe substrate tests");\n',
            encoding="utf-8",
            newline="\n",
        )
        policy_unsafe_build_drift_issues = validate_source_markers(
            root,
            {
                "zigux/tests/phase3_policy_unsafe_build.zig": ABI_REQUIRED_SOURCE_MARKERS[
                    "zigux/tests/phase3_policy_unsafe_build.zig"
                ]
            },
        )
        assert policy_unsafe_build_drift_issues == [
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing .root_source_file = b.path("phase3_policy_unsafe.zig"),',
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("panic_policy", panic_policy_module);',
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("allocator_policy", allocator_policy_module);',
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("layout_assert", layout_assert_module);',
            'source-marker: zigux/tests/phase3_policy_unsafe_build.zig missing root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
        ]

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    return 0
