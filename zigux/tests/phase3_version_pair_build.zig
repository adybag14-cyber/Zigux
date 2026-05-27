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

    const uapi_version_tests = b.addTest(.{
        .name = "phase3_uapi_version_pair_tests",
        .root_module = uapi_version,
    });
    const version_binding_tests = b.addTest(.{
        .name = "phase3_version_pair_tests",
        .root_module = version_binding,
    });

    const run_uapi_version_tests = b.addRunArtifact(uapi_version_tests);
    const run_version_binding_tests = b.addRunArtifact(version_binding_tests);

    const pair_step = b.step(
        "phase3-version-pair-test",
        "Run the Phase 3 UAPI version and binding version surfaces together.",
    );
    pair_step.dependOn(&run_uapi_version_tests.step);
    pair_step.dependOn(&run_version_binding_tests.step);
}
