const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_pair_tests",
        .root_module = abi_bindings_module,
    });
    const unsafe_policy_tests = b.addTest(.{
        .name = "phase3_unsafe_policy_pair_tests",
        .root_module = unsafe_policy_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_unsafe_policy_tests = b.addRunArtifact(unsafe_policy_tests);

    const test_step = b.step(
        "phase3-abi-unsafe-policy-pair-test",
        "Run the focused Phase 3 ABI bindings and unsafe policy helper pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_unsafe_policy_tests.step);

    const default_test_step = b.step(
        "test",
        "Run the focused Phase 3 ABI bindings and unsafe policy helper pair tests",
    );
    default_test_step.dependOn(&run_abi_tests.step);
    default_test_step.dependOn(&run_unsafe_policy_tests.step);

    b.default_step.dependOn(test_step);
}
