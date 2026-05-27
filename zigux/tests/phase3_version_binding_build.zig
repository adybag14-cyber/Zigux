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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_version_binding_relay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("uapi_version", uapi_version);
    root_module.addImport("version_binding", version_binding);

    const tests = b.addTest(.{
        .name = "phase3-version-binding-test",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const phase3_version_binding_step = b.step(
        "phase3-version-binding-test",
        "Run the focused Phase 3 version-binding relay tests",
    );
    phase3_version_binding_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 3 version-binding relay tests",
    );
    test_step.dependOn(&run.step);
}
