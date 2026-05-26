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

    const tests = b.addTest(.{
        .name = "phase3-uapi-version-test",
        .root_module = uapi_version,
    });
    const run = b.addRunArtifact(tests);

    const phase3_uapi_version_step = b.step(
        "phase3-uapi-version-test",
        "Run the standalone Phase 3 UAPI version tests",
    );
    phase3_uapi_version_step.dependOn(&run.step);
}
