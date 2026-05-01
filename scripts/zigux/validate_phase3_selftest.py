from __future__ import annotations

import json
import tempfile
from dataclasses import replace
from pathlib import Path

from phase3_catalog import Phase3Paths, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub, shared_runner_gate_for_slug
from validate_phase3_core import (
    ABI_EXPECTED_LAYOUT_KEYS,
    ABI_REVIEW_CHECKLIST_MARKERS,
    ABI_POLICY_UNSAFE_SURVEY_CHECK_REL,
    ABI_REQUIRED_DOC_MARKERS,
    ABI_REQUIRED_EXPECTED_CONSTANTS,
    ABI_REQUIRED_MANIFEST_FILES,
    ABI_REQUIRED_SOURCE_MARKERS,
    ABI_EXPORT_UAPI_BUILD_FILE_REL,
    ABI_LOW_LEVEL_BUILD_FILE_REL,
    ABI_POLICY_UNSAFE_BUILD_FILE_REL,
    BUILD_FILE_REL,
    build_smoke_commands,
    select_slices,
    validate_abi_expected_fixture,
    validate_export_uapi_boundary,
    validate_low_level_wrapper_exports,
    validate_policy_unsafe_boundary,
    validate_manifest,
    validate_slices,
    validate_source_markers,
)


def _write_phase3_slice(
    paths: Phase3Paths,
    *,
    slug: str,
    status: str = "ready",
) -> None:
    fixture_dir = paths.fixtures_dir / f"phase3_{slug}"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    (paths.docs_dir / f"phase3-{slug}-slice.md").write_text(
        "\n".join(
            [
                f"PHASE3_STATUS={status}",
                f"PHASE3_SLICE={slug}-slice",
                "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
                shared_runner_gate_for_slug(slug),
                "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    (paths.scripts_dir / f"check-phase3-{slug}.py").write_text(
        render_wrapper_stub(),
        encoding="utf-8",
        newline="\n",
    )
    (paths.tests_dir / f"phase3_{slug}_dump.zig").write_text(
        f"// {slug} dump\n",
        encoding="utf-8",
        newline="\n",
    )
    (fixture_dir / "expected.json").write_text(
        json.dumps({"abi_version": 1, "constants": ABI_REQUIRED_EXPECTED_CONSTANTS, "structs": {}}),
        encoding="utf-8",
        newline="\n",
    )
    (fixture_dir / f"phase3_{slug}_c_harness.c").write_text(
        f"// {slug} harness\n",
        encoding="utf-8",
        newline="\n",
    )
    (paths.fixtures_dir / f"phase3_{slug}_manifest.json").write_text(
        json.dumps(
            {
                "phase": "Phase 3",
                "status": status,
                "slice": f"{slug}-slice",
                "files": [
                    f"Documentation/zigux/phase3-{slug}-slice.md",
                    f"zigux/tests/phase3_{slug}_dump.zig",
                    f"zigux/tests/fixtures/phase3_{slug}/expected.json",
                    f"zigux/tests/fixtures/phase3_{slug}/phase3_{slug}_c_harness.c",
                ],
                "file_count": 4,
            }
        ),
        encoding="utf-8",
        newline="\n",
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

        _write_phase3_slice(paths, slug="alpha")
        _write_phase3_slice(paths, slug="beta")

        entries = discover_phase3_slices(paths)
        assert [entry.slug for entry in select_slices(entries, [])] == ["alpha", "beta"]
        assert [entry.slug for entry in select_slices(entries, ["beta"])] == ["beta"]
        try:
            select_slices(entries, ["missing"])
        except SystemExit as exc:
            assert str(exc) == "unknown Phase 3 slugs: missing"
        else:
            raise AssertionError("expected missing slug to fail")

        assert validate_manifest(entries[0]) == []
        abi_entry = replace(entries[0], slug="abi", build_step="phase3-dump")
        assert build_smoke_commands(abi_entry) == (
            ("phase3-dump", BUILD_FILE_REL),
            ("phase3-low-level-wrappers-test", ABI_LOW_LEVEL_BUILD_FILE_REL),
            ("phase3-export-uapi-test", ABI_EXPORT_UAPI_BUILD_FILE_REL),
            ("phase3-policy-unsafe-test", ABI_POLICY_UNSAFE_BUILD_FILE_REL),
        )
        assert validate_slices(
            root,
            entries,
            check_artifact_diff=False,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=False,
            zig_path=None,
        ) == []

        artifact_diff_path = paths.docs_dir / "artifact-diff.md"
        artifact_diff_path.write_text(
            "\n".join(
                [
                    "# Artifact Diff Policy",
                    "",
                    "Current Phase 3 use",
                    "- stale line",
                    "",
                    "Rules",
                    "- keep fixtures reviewable",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_slices(
            root,
            select_slices(entries, ["alpha"]),
            check_artifact_diff=False,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=True,
            zig_path=None,
        ) == []
        assert validate_slices(
            root,
            select_slices(entries, ["alpha"]),
            check_artifact_diff=True,
            check_build_smoke=False,
            check_slug_sanity=False,
            check_all_wrappers=True,
            zig_path=None,
        ) == ["doc-sync: artifact-diff-phase3-stale\tDocumentation/zigux/artifact-diff.md"]

        abi_fixture_dir = paths.fixtures_dir / "phase3_abi"
        abi_fixture_dir.mkdir(parents=True, exist_ok=True)
        (paths.tests_dir / "phase3_abi.zig").write_text(
            "\n".join(
                [
                    "const abi = @import(\"abi_bindings\");",
                    "const layout_assert = @import(\"layout_assert\");",
                    "",
                    'test "phase3 abi slice uses stable canonical layouts" {',
                    "    comptime {",
                    "        layout_assert.assertBoundaryHeaderLayout();",
                    "        layout_assert.assertExportStatusLayout();",
                    "        layout_assert.assertInteropPolicyLayout();",
                    "        layout_assert.assertMmioRangeLayout();",
                    '        layout_assert.assertOffset(abi.MmioRange, "base_addr", 0);',
                    '        layout_assert.assertOffset(abi.MmioRange, "length", @sizeOf(usize));',
                    '        layout_assert.assertOffset(abi.MmioRange, "stride", @sizeOf(usize) + 4);',
                    "    }",
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        (paths.tests_dir / "phase3_abi_dump.zig").write_text(
            "\n".join(
                [
                    "fn writeStructLayout(writer: anytype, comptime name: []const u8, comptime T: type, comma: bool) !void {",
                    "    _ = writer;",
                    "    _ = name;",
                    "    _ = T;",
                    "    _ = comma;",
                    "}",
                    "",
                    "pub fn main() void {",
                    "    const writer = undefined;",
                    '    writeStructLayout(writer, "zigux_boundary_header", void, true) catch unreachable;',
                    '    writeStructLayout(writer, "zigux_export_status", void, true) catch unreachable;',
                    '    writeStructLayout(writer, "zigux_mmio_range", void, true) catch unreachable;',
                    '    writeStructLayout(writer, "zigux_interop_policy", void, false) catch unreachable;',
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        expected_structs = {
            key: {"size": 0, "align": 0, "offsets": {}}
            for key in ABI_EXPECTED_LAYOUT_KEYS
        }
        (abi_fixture_dir / "expected.json").write_text(
            json.dumps(
                {
                    "abi_version": 1,
                    "constants": ABI_REQUIRED_EXPECTED_CONSTANTS,
                    "structs": expected_structs,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        (abi_fixture_dir / "phase3_abi_c_harness.c").write_text(
            "\n".join(
                [
                    "static const struct layout_desc layouts[] = {",
                    '    {"zigux_boundary_header", sizeof(struct zigux_boundary_header), 0, 0, 0},',
                    '    {"zigux_export_status", sizeof(struct zigux_export_status), 0, 0, 0},',
                    '    {"zigux_mmio_range", sizeof(struct zigux_mmio_range), 0, 0, 0},',
                    '    {"zigux_interop_policy", sizeof(struct zigux_interop_policy), 0, 0, 0},',
                    "};",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_abi_expected_fixture(root) == []
        extra_structs = dict(expected_structs)
        extra_structs["zigux_bitmap_view"] = {"size": 0, "align": 0, "offsets": {}}
        (abi_fixture_dir / "expected.json").write_text(
            json.dumps(
                {
                    "abi_version": 1,
                    "constants": ABI_REQUIRED_EXPECTED_CONSTANTS,
                    "structs": extra_structs,
                }
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_abi_expected_fixture(root) == [
            "abi-fixture: expected.json tracks 5 layouts but phase3_abi_dump.zig emits 4",
            "abi-fixture: expected.json tracks 5 layouts but phase3_abi_c_harness.c emits 4",
            "abi-fixture: expected.json and phase3_abi_dump.zig layout keys drift",
            "abi-fixture: expected.json and phase3_abi_c_harness.c layout keys drift",
            "abi-fixture: expected.json layout keys must stay bounded to zigux_boundary_header, zigux_export_status, zigux_interop_policy, zigux_mmio_range",
        ]

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

        policy_marker_fixture = root / "phase3-policy-unsafe-marker-fixture.zig"
        overflow_policy_markers = (
            'test "phase3 policy gate rejects overflowed unsafe address math"',
            "try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));",
            "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanBytes(u32, max));",
            "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanEnd(u32, 4, max));",
            "try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));",
            "try std.testing.expectError(error.AddressOverflow, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));",
        )
        policy_marker_fixture.write_text(
            "\n".join([
                'test "phase3 policy gate rejects overflowed unsafe address math" {}',
                "try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));",
                "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanBytes(u32, max));",
                "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanEnd(u32, 4, max));",
                "try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));",
                "try std.testing.expectError(error.AddressOverflow, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));",
                "",
            ]),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {"phase3-policy-unsafe-marker-fixture.zig": overflow_policy_markers},
        ) == []
        policy_marker_fixture.write_text(
            "\n".join([
                'test "phase3 policy gate rejects overflowed unsafe address math" {}',
                "try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));",
                "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanBytes(u32, max));",
                "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanEnd(u32, 4, max));",
                "try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));",
                "",
            ]),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {"phase3-policy-unsafe-marker-fixture.zig": overflow_policy_markers},
        ) == [
            "source-marker: phase3-policy-unsafe-marker-fixture.zig missing try std.testing.expectError(error.AddressOverflow, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));"
        ]

        low_level_export_fixture = root / "low-level-export-fixture.zig"
        low_level_export_fixture.write_text(
            "\n".join(
                [
                    "pub fn load() void {}",
                    "pub fn store() void {}",
                    "pub fn exchange() void {}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_low_level_wrapper_exports(
            root,
            {"low-level-export-fixture.zig": ("load", "store", "exchange")},
        ) == []
        low_level_export_fixture.write_text(
            "\n".join(
                [
                    "pub fn load() void {}",
                    "pub fn store() void {}",
                    "pub fn unexpected() void {}",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_low_level_wrapper_exports(
            root,
            {"low-level-export-fixture.zig": ("load", "store", "exchange")},
        ) == [
            "low-level-export: low-level-export-fixture.zig exports unexpected public helpers: unexpected",
            "low-level-export: low-level-export-fixture.zig is missing documented public helpers: exchange",
        ]

        assert (
            "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor"
            in ABI_REQUIRED_DOC_MARKERS
        )
        assert (
            "PHASE3_MMIO_SCOPE=range-read8-read16-read32-write8-write16-write32-plus-scoped-read8-write8-read16-write16-read32-write32"
            in ABI_REQUIRED_DOC_MARKERS
        )
        assert "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md" in ABI_REQUIRED_MANIFEST_FILES
        assert "Documentation/zigux/review-checklist.md" in ABI_REQUIRED_MANIFEST_FILES
        assert ABI_POLICY_UNSAFE_SURVEY_CHECK_REL in ABI_REQUIRED_MANIFEST_FILES
        assert any(
            "shared Phase 3 ABI substrate packet" in marker for marker in ABI_REVIEW_CHECKLIST_MARKERS
        )
        low_level_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_low_level_wrappers.zig"]
        assert "atomic.fetchSub(u32, &value, 4, .seq_cst)" in low_level_markers
        assert "atomic.fetchOr(u32, &value, 0b1000, .seq_cst)" in low_level_markers
        assert "atomic.fetchAnd(u32, &value, 0b0111, .seq_cst)" in low_level_markers
        assert "atomic.fetchXor(u32, &value, 0b1111, .seq_cst)" in low_level_markers
        assert (
            "try std.testing.expectError(error.AddressOverflow, mmio.write8Scoped(.volatile_mmio, std.math.maxInt(usize), 1, 0x99));"
            in low_level_markers
        )
        assert (
            "try std.testing.expectError(error.AddressOverflow, mmio.read32Scoped(.volatile_mmio, std.math.maxInt(usize), 4));"
            in low_level_markers
        )
        assert 'test "phase3 low-level wrapper ABI range shape stays stable"' in low_level_markers
        assert 'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit"' in low_level_markers
        mmio_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/helpers/mmio.zig"]
        assert 'test "phase3 mmio wrapper rejects overflowed scoped accesses"' in mmio_markers
        interop_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/helpers/interop_policy.zig"]
        assert "pub fn initializesOwnedState(self: DecodedInteropPolicy) bool {" in interop_markers
        assert "pub fn requiresResetOnInit(self: DecodedInteropPolicy) bool {" in interop_markers
        assert 'test "phase3 interop policy decoder keeps allocator init requirements explicit"' in interop_markers
        narrow_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/unsafe/narrow.zig"]
        assert "pub fn checkedSpanEnd(comptime T: type, base: usize, len: usize) ScopeError!usize {" in narrow_markers
        assert 'test "phase3 narrow unsafe scoped helpers reject overflowed address math"' in narrow_markers
        policy_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_policy_unsafe.zig"]
        assert "try std.testing.expectError(error.InvalidPanicMode, interop_policy.decode(.{" in policy_markers
        assert "try std.testing.expectError(error.InvalidAllocatorMode, interop_policy.decode(.{" in policy_markers
        assert 'test "phase3 policy gate decodes interop-policy unsafe bytes explicitly"' in policy_markers
        assert "const invalid_scope_policy = abi.InteropPolicy{" in policy_markers
        assert "const reserved_policy = abi.InteropPolicy{" in policy_markers
        assert (
            "try std.testing.expect(!narrow.recognizesInteropPolicyBytes(invalid_scope_policy.unsafe_scope, invalid_scope_policy.reserved));"
            in policy_markers
        )
        assert (
            "try std.testing.expect(!narrow.recognizesInteropPolicyBytes(reserved_policy.unsafe_scope, reserved_policy.reserved));"
            in policy_markers
        )
        assert 'test "phase3 policy gate enforces the declared unsafe scope"' in policy_markers
        assert "try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedPointerAt(u32, .none, base, 0));" in policy_markers
        assert (
            "try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstSliceAt(u32, .volatile_mmio, base, 1));"
            in policy_markers
        )
        assert (
            "try std.testing.expectError(error.UnsafeScopeDenied, narrow.scopedConstPointerAt(u32, .volatile_mmio, base));"
            in policy_markers
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
            "print('missing_survey_marker:PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig')\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_export_uapi_boundary(root) == [
            "export-uapi-gate: missing_survey_marker:PHASE3_EXPORT_SHIM_PATH=zigux/kernel/export_shim.zig"
        ]

        policy_unsafe_check = root / ABI_POLICY_UNSAFE_SURVEY_CHECK_REL
        policy_unsafe_check.write_text(
            "#!/usr/bin/env python3\nprint('PHASE3_POLICY_UNSAFE_SURVEY=pass')\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_policy_unsafe_boundary(root) == []
        policy_unsafe_check.write_text(
            "#!/usr/bin/env python3\n"
            "print('PHASE3_POLICY_UNSAFE_SURVEY=fail')\n"
            "print('missing_survey_marker:PHASE3_INTEROP_POLICY_PATH=zigux/helpers/interop_policy.zig')\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_policy_unsafe_boundary(root) == [
            "policy-unsafe-gate: missing_survey_marker:PHASE3_INTEROP_POLICY_PATH=zigux/helpers/interop_policy.zig"
        ]

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    return 0


def main() -> int:
    return run_self_test()


if __name__ == "__main__":
    raise SystemExit(main())
