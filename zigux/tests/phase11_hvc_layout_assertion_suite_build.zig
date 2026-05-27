const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const hvc_console_module = b.createModule(.{
        .root_source_file = b.path("../../drivers/tty/hvc/hvc_console.zig"),
        .target = target,
        .optimize = optimize,
    });

    const hv_ops_proof_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),
        .target = target,
        .optimize = optimize,
    });
    hv_ops_proof_module.addImport("hvc_console", hvc_console_module);
    hv_ops_proof_module.addImport("layout_assert", layout_assert_module);

    const hv_ops_proof_tests = b.addTest(.{
        .name = "phase11-hvc-hv-ops-layout-proof-suite",
        .root_module = hv_ops_proof_module,
    });
    const run_hv_ops_proof_tests = b.addRunArtifact(hv_ops_proof_tests);

    const export_surface_proof_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_surface_proof_module.addImport("hvc_console", hvc_console_module);
    export_surface_proof_module.addImport("layout_assert", layout_assert_module);

    const export_surface_proof_tests = b.addTest(.{
        .name = "phase11-hvc-export-surface-layout-proof-suite",
        .root_module = export_surface_proof_module,
    });
    const run_export_surface_proof_tests = b.addRunArtifact(export_surface_proof_tests);

    const test_step = b.step("test", "Run the current Phase 11 HVC ABI layout assertion suite");
    test_step.dependOn(&run_hv_ops_proof_tests.step);
    test_step.dependOn(&run_export_surface_proof_tests.step);
}
