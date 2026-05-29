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
    abi_bindings_module.addImport("notifier_abi", notifier_abi_module);

    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("uapi_version", uapi_version_module);

    const notifier_tests = b.addTest(.{
        .name = "phase3_notifier_version_pair_notifier_tests",
        .root_module = notifier_abi_module,
    });
    const version_tests = b.addTest(.{
        .name = "phase3_notifier_version_pair_version_tests",
        .root_module = version_binding_module,
    });

    const run_notifier_tests = b.addRunArtifact(notifier_tests);
    const run_version_tests = b.addRunArtifact(version_tests);

    const test_step = b.step(
        "phase3-notifier-version-pair-test",
        "Run the focused Phase 3 notifier ABI plus version binding pair replay",
    );
    test_step.dependOn(&run_notifier_tests.step);
    test_step.dependOn(&run_version_tests.step);
}
