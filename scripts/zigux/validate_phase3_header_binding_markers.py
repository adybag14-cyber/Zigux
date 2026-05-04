#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent

HEADER_BINDING_MARKERS = {
    "include/zigux/abi.h": (
        "#define ZIGUX_ABI_VERSION 1U",
        "#define ZIGUX_STATUS_FLAG_ERROR 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_boundary_header {",
        "struct zigux_export_status {",
    ),
    "include/linux/zigux.h": (
        "#define ZIGUX_BITS_PER_LONG ((zigux_u32)(sizeof(unsigned long) * 8U))",
        "static inline struct zigux_export_status zigux_status_ok(zigux_u16 facility)",
        "static inline struct zigux_export_status zigux_status_err(zigux_s32 code,",
        "#define zigux_assert_layout(type, expected_size) \\",
        "zigux_bitmap_view_from_words(const unsigned long *words, zigux_u32 nbits)",
    ),
    "include/zigux/rbtree.h": (
        "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
        "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
        "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
        "struct zigux_rbtree_root_view {",
    ),
    "zigux/bindings/abi.zig": (
        "pub const ABI_VERSION: u16 = 1;",
        "pub const STATUS_FLAG_ERROR: u16 = 1;",
        "pub const Facility = enum(u16) {",
        "pub const PanicMode = enum(u8) {",
        "pub const AllocatorMode = enum(u8) {",
        "pub const UnsafeScope = enum(u8) {",
        "pub const CHRDEV_NOTIFY_MASK_SUCCESS: u32 = 1;",
        "pub const CHRDEV_NOTIFY_STATUS_DELIVERED: u32 = 1;",
        "pub const CHRDEV_NOTIFY_ACK_STATUS_ACKED: u32 = 1;",
    ),
    "zigux/bindings/rbtree.zig": (
        "pub const ROOT_FLAG_EMPTY: u32 = 1;",
        "pub const ROOT_FLAG_CACHED: u32 = 2;",
        "pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
        "pub const RootView = extern struct {",
        "pub fn isValid(view: RootView) bool {",
    ),
    "Documentation/zigux/phase3-abi-slice.md": (
        "PHASE3_CURRENT_INTEROP_FAMILIES=bitmap-cpumask-rbtree-list-hlist-errptr-xarray-idr-ida-minor-alloc-dev-region-cdev-chrdev",
        "PHASE3_CURRENT_INTEROP_GAP_DETAIL=live-build-graph-now-carries-deep-chrdev-tail-packets-while-the-curated-shared-include-zigux-abi-h-plus-zigux-bindings-abi-zig-rbtree-root-view-lift-is-landed-and-the-honest-remaining-gap-is-survey-and-validator-wording-that-still-describes-that-shared-lift-as-missing",
        "dedicated rbtree boundary packet plus minor-allocation, dev-region, cdev, and chrdev planning and notification chains",
    ),
    "zigux/tests/build.zig": (
        "const phase3_dump_module = b.createModule(.{",
        '.root_source_file = b.path("phase3_abi_dump.zig"),',
        'phase3_dump_module.addImport("abi_bindings", abi_bindings_module);',
        "const phase3_dump = b.addExecutable(.{",
        '.name = "phase3-abi-dump",',
        'const phase3_dump_step = b.step("phase3-dump", "Run Phase 3 ABI dump");',
        "phase3_dump_step.dependOn(&run_phase3_dump.step);",
        "const bitmap_view_module = b.createModule(.{",
        "const cpumask_view_module = b.createModule(.{",
        "const list_view_module = b.createModule(.{",
        "const hlist_view_module = b.createModule(.{",
        "const err_ptr_module = b.createModule(.{",
        "const xarray_slot_view_module = b.createModule(.{",
        "const idr_slot_view_module = b.createModule(.{",
        "const ida_policy_view_module = b.createModule(.{",
        "const dev_region_plan_module = b.createModule(.{",
        "const cdev_add_plan_module = b.createModule(.{",
        "const chrdev_open_plan_module = b.createModule(.{",
        "const chrdev_fops_plan_module = b.createModule(.{",
        "const chrdev_route_plan_module = b.createModule(.{",
        "const chrdev_io_plan_module = b.createModule(.{",
        "const chrdev_notify_plan_module = b.createModule(.{",
        "const chrdev_notify_policy_plan_module = b.createModule(.{",
        "const chrdev_notify_budget_plan_module = b.createModule(.{",
        "const chrdev_notify_ack_plan_module = b.createModule(.{",
        "const chrdev_notify_ack_policy_plan_module = b.createModule(.{",
        "const chrdev_notify_ack_budget_plan_module = b.createModule(.{",
        "const chrdev_notify_ack_window_plan_module = b.createModule(.{",
        "const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan_module = b.createModule(.{",
    ),
    "zigux/tests/phase3_export_uapi_build.zig": (
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("../uapi/version.zig"),',
        'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("phase3_export_uapi.zig"),',
        'export_shim_module.addImport("uapi_version", uapi_version_module);',
        'root_module.addImport("abi_bindings", abi_bindings_module);',
        'root_module.addImport("export_shim", export_shim_module);',
        'root_module.addImport("uapi_version", uapi_version_module);',
        '"phase3-export-uapi-test",',
    ),
    "zigux/tests/phase3_export_uapi_layout_build.zig": (
        '.root_source_file = b.path("../kernel/export_shim.zig"),',
        'export_shim_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("../uapi/version.zig"),',
        'uapi_version_module.addImport("abi_bindings", abi_bindings_module);',
        '.root_source_file = b.path("phase3_export_uapi_layout.zig"),',
        'export_shim_module.addImport("uapi_version", uapi_version_module);',
        'root_module.addImport("abi_bindings", abi_bindings_module);',
        'root_module.addImport("export_shim", export_shim_module);',
        'root_module.addImport("uapi_version", uapi_version_module);',
        '"phase3-export-uapi-layout-test",',
    ),
    "zigux/tests/phase3_export_uapi_layout.zig": (
        'test "phase3 export shim and uapi keep canonical boundary layout" {',
        "try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));",
        "try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));",
        'try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));',
        'try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));',
        'try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));',
        'try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));',
        "try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), @as(usize, header.size));",
        "try std.testing.expectEqual(header, uapi_header);",
        "try std.testing.expect(export_shim.isCanonicalHeader(header));",
        "try std.testing.expect(uapi_version.isCanonical(uapi_header));",
    ),
    "zigux/tests/fixtures/phase3_abi_manifest.json": (
        '"include/zigux/rbtree.h",',
        '"zigux/bindings/rbtree.zig",',
        '"zigux/tests/build.zig",',
        '"zigux/tests/phase3_export_uapi_build.zig",',
        '"zigux/tests/phase3_export_uapi.zig",',
        '"zigux/tests/phase3_export_uapi_layout_build.zig",',
        '"zigux/tests/phase3_export_uapi_layout.zig",',
        '"scripts/zigux/check-phase3-abi-layout-packet.py",',
    ),
    "scripts/zigux/validate-phase3.py": (
        '"check-phase3-abi-layout-packet.py",',
        '"PHASE3_ABI_LAYOUT_PACKET=fail",',
        '"abi-layout-packet-gate",',
        '"check-phase3-validation-flow.py",',
        '"PHASE3_VALIDATION_FLOW=fail",',
        '"validation-flow-gate",',
    ),
    "scripts/zigux/check-phase3-abi-layout-packet.py": (
        'EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"',
        'LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"',
        'PHASE3_ABI_C_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"',
        '("zigux_boundary_header", "BoundaryHeader", "assertBoundaryHeaderLayout")',
        'print("PHASE3_ABI_LAYOUT_PACKET=pass")',
    ),
    "scripts/zigux/validate-phase3-export-uapi-survey.py": (
        "REQUIRED_SURVEY_MARKERS = (",
        '"PHASE3_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",',
        '"PHASE3_UAPI_SCOPE=version-and-boundary-header",',
        "SURVEYED_PACKET_BLOB_MARKERS = {",
        '"PHASE3_EXPORT_UAPI_BUILD_BLOB_SHA": "zigux/tests/phase3_export_uapi_build.zig",',
        "def _packet_drift_by_blob_sha(root: Path, survey: str) -> list[str]:",
        'print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")',
    ),
}


def validate_header_binding_markers(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    for rel, markers in HEADER_BINDING_MARKERS.items():
        path = root / rel
        if not path.exists():
            issues.append(f"header-binding-marker: missing {rel}")
            continue

        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"header-binding-marker: {rel} missing {marker}")
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_header_binding_marker_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        for rel, markers in HEADER_BINDING_MARKERS.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8", newline="\n")

        assert validate_header_binding_markers(root) == []

        first_marker = HEADER_BINDING_MARKERS["include/zigux/abi.h"][0]
        abi_header = root / "include/zigux/abi.h"
        abi_header.write_text(
            abi_header.read_text(encoding="utf-8").replace(first_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: include/zigux/abi.h missing {first_marker}" in issues

        notify_ack_marker = HEADER_BINDING_MARKERS["zigux/bindings/abi.zig"][-1]
        bindings_file = root / "zigux/bindings/abi.zig"
        bindings_file.write_text(
            bindings_file.read_text(encoding="utf-8").replace(notify_ack_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: include/zigux/abi.h missing {first_marker}" in issues
        assert f"header-binding-marker: zigux/bindings/abi.zig missing {notify_ack_marker}" in issues

        rbtree_header_marker = HEADER_BINDING_MARKERS["include/zigux/rbtree.h"][-1]
        rbtree_header = root / "include/zigux/rbtree.h"
        rbtree_header.write_text(
            rbtree_header.read_text(encoding="utf-8").replace(rbtree_header_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: include/zigux/rbtree.h missing {rbtree_header_marker}" in issues

        rbtree_binding_marker = HEADER_BINDING_MARKERS["zigux/bindings/rbtree.zig"][3]
        rbtree_bindings = root / "zigux/bindings/rbtree.zig"
        rbtree_bindings.write_text(
            rbtree_bindings.read_text(encoding="utf-8").replace(rbtree_binding_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/bindings/rbtree.zig missing {rbtree_binding_marker}" in issues

        build_marker = HEADER_BINDING_MARKERS["zigux/tests/build.zig"][6]
        build_file = root / "zigux/tests/build.zig"
        build_file.write_text(
            build_file.read_text(encoding="utf-8").replace(build_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/tests/build.zig missing {build_marker}" in issues

        interop_build_marker = HEADER_BINDING_MARKERS["zigux/tests/build.zig"][-1]
        build_file.write_text(
            build_file.read_text(encoding="utf-8").replace(interop_build_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/tests/build.zig missing {interop_build_marker}" in issues

        export_uapi_build_marker = HEADER_BINDING_MARKERS["zigux/tests/phase3_export_uapi_build.zig"][3]
        export_uapi_build = root / "zigux/tests/phase3_export_uapi_build.zig"
        export_uapi_build.write_text(
            export_uapi_build.read_text(encoding="utf-8").replace(export_uapi_build_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/tests/phase3_export_uapi_build.zig missing {export_uapi_build_marker}" in issues

        export_uapi_survey_marker = HEADER_BINDING_MARKERS["scripts/zigux/validate-phase3-export-uapi-survey.py"][4]
        export_uapi_survey = root / "scripts/zigux/validate-phase3-export-uapi-survey.py"
        export_uapi_survey.write_text(
            export_uapi_survey.read_text(encoding="utf-8").replace(export_uapi_survey_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: scripts/zigux/validate-phase3-export-uapi-survey.py missing {export_uapi_survey_marker}" in issues

        abi_slice_marker = HEADER_BINDING_MARKERS["Documentation/zigux/phase3-abi-slice.md"][0]
        abi_slice_doc = root / "Documentation/zigux/phase3-abi-slice.md"
        abi_slice_doc.write_text(
            abi_slice_doc.read_text(encoding="utf-8").replace(abi_slice_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: Documentation/zigux/phase3-abi-slice.md missing {abi_slice_marker}" in issues

        manifest_marker = HEADER_BINDING_MARKERS["zigux/tests/fixtures/phase3_abi_manifest.json"][3]
        manifest_file = root / "zigux/tests/fixtures/phase3_abi_manifest.json"
        manifest_file.write_text(
            manifest_file.read_text(encoding="utf-8").replace(manifest_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/tests/fixtures/phase3_abi_manifest.json missing {manifest_marker}" in issues

        export_uapi_layout_build_marker = HEADER_BINDING_MARKERS["zigux/tests/phase3_export_uapi_layout_build.zig"][4]
        export_uapi_layout_build = root / "zigux/tests/phase3_export_uapi_layout_build.zig"
        export_uapi_layout_build.write_text(
            export_uapi_layout_build.read_text(encoding="utf-8").replace(export_uapi_layout_build_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/tests/phase3_export_uapi_layout_build.zig missing {export_uapi_layout_build_marker}" in issues

        export_uapi_layout_marker = HEADER_BINDING_MARKERS["zigux/tests/phase3_export_uapi_layout.zig"][7]
        export_uapi_layout = root / "zigux/tests/phase3_export_uapi_layout.zig"
        export_uapi_layout.write_text(
            export_uapi_layout.read_text(encoding="utf-8").replace(export_uapi_layout_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: zigux/tests/phase3_export_uapi_layout.zig missing {export_uapi_layout_marker}" in issues

        layout_packet_marker = HEADER_BINDING_MARKERS["scripts/zigux/check-phase3-abi-layout-packet.py"][0]
        layout_packet_file = root / "scripts/zigux/check-phase3-abi-layout-packet.py"
        layout_packet_file.write_text(
            layout_packet_file.read_text(encoding="utf-8").replace(layout_packet_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: scripts/zigux/check-phase3-abi-layout-packet.py missing {layout_packet_marker}" in issues

        linux_header_marker = HEADER_BINDING_MARKERS["include/linux/zigux.h"][1]
        linux_header = root / "include/linux/zigux.h"
        linux_header.write_text(
            linux_header.read_text(encoding="utf-8").replace(linux_header_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: include/linux/zigux.h missing {linux_header_marker}" in issues

        shared_validator_marker = HEADER_BINDING_MARKERS["scripts/zigux/validate-phase3.py"][1]
        shared_validator = root / "scripts/zigux/validate-phase3.py"
        shared_validator.write_text(
            shared_validator.read_text(encoding="utf-8").replace(shared_validator_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: scripts/zigux/validate-phase3.py missing {shared_validator_marker}" in issues

        validation_flow_marker = HEADER_BINDING_MARKERS["scripts/zigux/validate-phase3.py"][3]
        shared_validator.write_text(
            shared_validator.read_text(encoding="utf-8").replace(validation_flow_marker + "\n", "", 1),
            encoding="utf-8",
            newline="\n",
        )
        issues = validate_header_binding_markers(root)
        assert f"header-binding-marker: scripts/zigux/validate-phase3.py missing {validation_flow_marker}" in issues

    print("PHASE3_HEADER_BINDING_MARKER_SELF_TEST=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_self_test())
