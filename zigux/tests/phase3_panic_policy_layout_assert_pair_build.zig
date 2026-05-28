const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_tests = b.addTest(.{
        .root_module = panic_policy_module,
        .name = "phase3_panic_policy_pair_tests",
    });
    const layout_assert_tests = b.addTest(.{
        .root_module = layout_assert_module,
        .name = "phase3_layout_assert_pair_tests",
    });

    const run_panic_policy_tests = b.addRunArtifact(panic_policy_tests);
    const run_layout_assert_tests = b.addRunArtifact(layout_assert_tests);

    const pair_test = b.step(
        "phase3-panic-policy-layout-assert-pair-test",
        "Run the standalone Phase 3 panic-policy and layout-assert pair replay.",
    );
    pair_test.dependOn(&run_panic_policy_tests.step);
    pair_test.dependOn(&run_layout_assert_tests.step);
}
