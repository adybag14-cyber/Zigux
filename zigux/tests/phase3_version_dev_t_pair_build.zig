const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version.addImport("abi_bindings", abi_bindings);

    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);

    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });

    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);

    const uapi_version_tests = b.addTest(.{
        .name = "phase3_uapi_version_pair_tests",
        .root_module = uapi_version,
    });
    const version_binding_tests = b.addTest(.{
        .name = "phase3_version_pair_tests",
        .root_module = version_binding,
    });
    const uapi_dev_t_tests = b.addTest(.{
        .name = "phase3_uapi_dev_t_pair_tests",
        .root_module = uapi_dev_t,
    });
    const dev_t_binding_tests = b.addTest(.{
        .name = "phase3_dev_t_pair_tests",
        .root_module = dev_t_binding,
    });

    const run_uapi_version_tests = b.addRunArtifact(uapi_version_tests);
    const run_version_binding_tests = b.addRunArtifact(version_binding_tests);
    const run_uapi_dev_t_tests = b.addRunArtifact(uapi_dev_t_tests);
    const run_dev_t_binding_tests = b.addRunArtifact(dev_t_binding_tests);

    const pair_test_step = b.step(
        "phase3-version-dev-t-pair-test",
        "Run the focused Phase 3 version/dev_t pair replay",
    );
    pair_test_step.dependOn(&run_uapi_version_tests.step);
    pair_test_step.dependOn(&run_version_binding_tests.step);
    pair_test_step.dependOn(&run_uapi_dev_t_tests.step);
    pair_test_step.dependOn(&run_dev_t_binding_tests.step);
}
