const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings_module.addImport("notifier_abi.zig", notifier_abi_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_notifier_result_relay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("notifier_abi", notifier_abi_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-notifier-result-relay-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const relay_step = b.step("phase3-abi-notifier-result-relay-test", "Run Phase 3 ABI notifier result relay tests");
    relay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 3 ABI notifier result relay tests");
    test_step.dependOn(&run_tests.step);
}
