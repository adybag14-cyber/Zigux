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

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings_module,
    });
    const layout_assert_tests = b.addTest(.{
        .name = "phase3_layout_assert_pair_tests",
        .root_module = layout_assert_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_layout_assert_tests = b.addRunArtifact(layout_assert_tests);

    const test_step = b.step(
        "phase3-abi-layout-assert-pair-test",
        "Run the focused Phase 3 ABI bindings and layout-assert pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_layout_assert_tests.step);
}
