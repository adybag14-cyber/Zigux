from __future__ import annotations

import json
import tempfile
from dataclasses import replace
from pathlib import Path

from phase3_catalog import Phase3Paths, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub, shared_runner_gate_for_slug
from validate_phase3_core import (
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

        export_uapi_build_fixture = root / "zigux/tests/phase3_export_uapi_build.zig"
        export_uapi_build_fixture.write_text(
            "const std = @import(\"std\");\n\n"
            "pub fn build(b: *std.Build) void {\n"
            "    const target = b.standardTargetOptions(.{});\n"
            "    const optimize = b.standardOptimizeOption(.{});\n\n"
            "    const abi_bindings_module = b.createModule(.{\n"
            '        .root_source_file = b.path("../bindings/abi.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            "    const export_shim_module = b.createModule(.{\n"
            '        .root_source_file = b.path("../kernel/export_shim.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            '    export_shim_module.addImport("abi_bindings", abi_bindings_module);\n'
            "    const uapi_version_module = b.createModule(.{\n"
            '        .root_source_file = b.path("../uapi/version.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            '    uapi_version_module.addImport("abi_bindings", abi_bindings_module);\n'
            '    export_shim_module.addImport("uapi_version", uapi_version_module);\n\n'
            "    const root_module = b.createModule(.{\n"
            '        .root_source_file = b.path("phase3_export_uapi.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            '    root_module.addImport("abi_bindings", abi_bindings_module);\n'
            '    root_module.addImport("export_shim", export_shim_module);\n'
            '    root_module.addImport("uapi_version", uapi_version_module);\n\n'
            "    const tests = b.addTest(.{\n"
            '        .name = "phase3-export-uapi-tests",\n'
            "        .root_module = root_module,\n"
            "    });\n"
            "    const run_tests = b.addRunArtifact(tests);\n"
            '    const test_step = b.step("phase3-export-uapi-test", "Run Phase 3 export shim and uapi smoke tests");\n'
            "    test_step.dependOn(&run_tests.step);\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )
        export_uapi_build_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_export_uapi_build.zig"]
        assert validate_source_markers(
            root,
            {"zigux/tests/phase3_export_uapi_build.zig": export_uapi_build_markers},
        ) == []
        export_uapi_build_fixture.write_text(
            export_uapi_build_fixture.read_text(encoding="utf-8").replace(
                '    export_shim_module.addImport("uapi_version", uapi_version_module);\n', "", 1
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert validate_source_markers(
            root,
            {"zigux/tests/phase3_export_uapi_build.zig": export_uapi_build_markers},
        ) == [
            'source-marker: zigux/tests/phase3_export_uapi_build.zig missing export_shim_module.addImport("uapi_version", uapi_version_module);'
        ]
        export_uapi_build_fixture.write_text(
            "const std = @import(\"std\");\n\n"
            "pub fn build(b: *std.Build) void {\n"
            "    const target = b.standardTargetOptions(.{});\n"
            "    const optimize = b.standardOptimizeOption(.{});\n\n"
            "    const abi_bindings_module = b.createModule(.{\n"
            '        .root_source_file = b.path("../bindings/abi.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            "    const export_shim_module = b.createModule(.{\n"
            '        .root_source_file = b.path("../kernel/export_shim.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            '    export_shim_module.addImport("abi_bindings", abi_bindings_module);\n'
            "    const uapi_version_module = b.createModule(.{\n"
            '        .root_source_file = b.path("../uapi/version.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            '    uapi_version_module.addImport("abi_bindings", abi_bindings_module);\n'
            '    export_shim_module.addImport("uapi_version", uapi_version_module);\n\n'
            "    const root_module = b.createModule(.{\n"
            '        .root_source_file = b.path("phase3_export_uapi.zig"),\n'
            "        .target = target,\n"
            "        .optimize = optimize,\n"
            "    });\n"
            '    root_module.addImport("abi_bindings", abi_bindings_module);\n'
            '    root_module.addImport("export_shim", export_shim_module);\n'
            '    root_module.addImport("uapi_version", uapi_version_module);\n\n'
            "    const tests = b.addTest(.{\n"
            '        .name = "phase3-export-uapi-tests",\n'
            "        .root_module = root_module,\n"
            "    });\n"
            "    const run_tests = b.addRunArtifact(tests);\n"
            '    const test_step = b.step("phase3-export-uapi-test", "Run Phase 3 export shim and uapi smoke tests");\n'
            "    test_step.dependOn(&run_tests.step);\n"
            "}\n",
            encoding="utf-8",
            newline="\n",
        )

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
            "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor"
            in ABI_REQUIRED_DOC_MARKERS
        )
        assert (
            "PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64"
            in ABI_REQUIRED_DOC_MARKERS
        )
        assert "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md" in ABI_REQUIRED_MANIFEST_FILES
        assert "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md" in ABI_REQUIRED_MANIFEST_FILES
        assert "Documentation/zigux/phase3-roadmap-gap-survey.md" in ABI_REQUIRED_MANIFEST_FILES
        assert "Documentation/zigux/review-checklist.md" in ABI_REQUIRED_MANIFEST_FILES
        assert ABI_POLICY_UNSAFE_SURVEY_CHECK_REL in ABI_REQUIRED_MANIFEST_FILES
        assert "scripts/zigux/validate-phase3-low-level-wrapper-survey.py" in ABI_REQUIRED_MANIFEST_FILES
        assert "scripts/zigux/validate-phase3-roadmap-gap-survey.py" in ABI_REQUIRED_MANIFEST_FILES
        assert "scripts/zigux/validate_phase3_header_binding_markers.py" in ABI_REQUIRED_MANIFEST_FILES
        assert any(
            "shared Phase 3 ABI substrate packet" in marker for marker in ABI_REVIEW_CHECKLIST_MARKERS
        )
        low_level_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/tests/phase3_low_level_wrappers.zig"]
        assert "atomic.fetchSub(u32, &value, 4, .seq_cst)" in low_level_markers
        assert "atomic.fetchOr(u32, &value, 0b1000, .seq_cst)" in low_level_markers
        assert "atomic.fetchAnd(u32, &value, 0b0111, .seq_cst)" in low_level_markers
        assert "atomic.fetchXor(u32, &value, 0b1111, .seq_cst)" in low_level_markers
        assert "const weak_mismatch = atomic.compareExchangeWeak(u32, &weak_value, 31, 55, .seq_cst, .seq_cst);" in low_level_markers
        assert (
            "try std.testing.expectError(error.AddressOverflow, mmio.write8Scoped(.volatile_mmio, std.math.maxInt(usize), 1, 0x99));"
            in low_level_markers
        )
        assert (
            "try std.testing.expectError(error.AddressOverflow, mmio.read32Scoped(.volatile_mmio, std.math.maxInt(usize), 4));"
            in low_level_markers
        )
        assert "mmio.write64(base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);" in low_level_markers
        assert "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Scoped(.none, base64, 0, 0x99));" in low_level_markers
        assert "try std.testing.expectError(error.MisalignedAccess, mmio.write64Scoped(.volatile_mmio, base64, 4, 0x99));" in low_level_markers
        assert "try std.testing.expectError(error.AddressOverflow, mmio.write64Scoped(.volatile_mmio, std.math.maxInt(usize), 8, 0x99));" in low_level_markers
        assert "try mmio.write64Scoped(.volatile_mmio, base64, 0, 0xfedc_ba98_7654_3210);" in low_level_markers
        assert "try std.testing.expectEqual(@as(u64, 0xfedc_ba98_7654_3210), try mmio.read64Scoped(.volatile_mmio, base64, 0));" in low_level_markers
        assert 'test "phase3 low-level wrapper ABI range shape stays stable"' in low_level_markers
        assert 'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit"' in low_level_markers
        mmio_markers = ABI_REQUIRED_SOURCE_MARKERS["zigux/helpers/mmio.zig"]
        assert "pub fn read64Scoped(scope: narrow.UnsafeScopeTag, base_addr: usize, offset: usize) narrow.ScopeError!u64 {" in mmio_markers
        assert "pub fn write64Scoped(" in mmio_markers
        assert "pub fn read64(base_addr: usize, offset: usize) u64 {" in mmio_markers
        assert "pub fn write64(base_addr: usize, offset: usize, value: u64) void {" in mmio_markers
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
        assert 'test "phase3 policy gate rejects overflowed unsafe address math"' in policy_markers
        assert "try std.testing.expectError(error.AddressOverflow, narrow.checkedByteOffset(max, 1));" in policy_markers
        assert "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanBytes(u32, max));" in policy_markers
        assert "try std.testing.expectError(error.AddressOverflow, narrow.checkedSpanEnd(u32, 4, max));" in policy_markers
        assert "try std.testing.expectError(error.AddressOverflow, narrow.scopedPointerAt(u32, .volatile_mmio, max, 1));" in policy_markers
        assert "try std.testing.expectError(error.AddressOverflow, narrow.scopedConstSliceAt(u32, .raw_pointer_bridge, 4, max));" in policy_markers

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
        policy_unsafe_check.write_text(
            "#!/usr/bin/env python3\n"
            "print('PHASE3_POLICY_UNSAFE_SURVEY=fail')\n"
            "print('surveyed_blob_drift:zigux/helpers/mmio.zig')\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_policy_unsafe_boundary(root) == [
            "policy-unsafe-gate: surveyed_blob_drift:zigux/helpers/mmio.zig"
        ]

    print("PHASE3_VALIDATOR_SELF_TEST=pass")
    return 0


def main() -> int:
    return run_self_test()


if __name__ == "__main__":
    raise SystemExit(main())
