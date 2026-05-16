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

    const proof_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),
        .target = target,
        .optimize = optimize,
    });
    proof_module.addImport("layout_assert", layout_assert_module);

    const proof_tests = b.addTest(.{
        .name = "phase11-hvc-export-surface-layout-proof",
        .root_module = proof_module,
    });
    const run_proof_tests = b.addRunArtifact(proof_tests);

    const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");
    test_step.dependOn(&run_proof_tests.step);
}
