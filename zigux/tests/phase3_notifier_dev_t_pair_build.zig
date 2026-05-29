const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const notifier_tests = b.addTest(.{
        .name = "phase3_notifier_dev_t_pair_notifier_tests",
        .root_module = notifier_abi_module,
    });
    const dev_t_tests = b.addTest(.{
        .name = "phase3_notifier_dev_t_pair_dev_t_tests",
        .root_module = dev_t_binding_module,
    });

    const run_notifier_tests = b.addRunArtifact(notifier_tests);
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const test_step = b.step(
        "phase3-notifier-dev-t-pair-test",
        "Run the focused Phase 3 notifier ABI plus dev_t binding pair replay",
    );
    test_step.dependOn(&run_notifier_tests.step);
    test_step.dependOn(&run_dev_t_tests.step);
}
