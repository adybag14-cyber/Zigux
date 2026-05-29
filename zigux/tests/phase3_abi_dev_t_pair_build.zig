const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_tests = b.addTest(.{
        .name = "phase3_abi_dev_t_pair_abi_tests",
        .root_module = abi_module,
    });
    const run_abi_tests = b.addRunArtifact(abi_tests);

    const dev_t_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_module.addImport("dev_t_bindings", dev_t_bindings_module);

    const dev_t_tests = b.addTest(.{
        .name = "phase3_abi_dev_t_pair_dev_t_tests",
        .root_module = dev_t_module,
    });
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const test_step = b.step(
        "phase3-abi-dev-t-pair-test",
        "Run the Phase 3 ABI and dev_t pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_dev_t_tests.step);
}
