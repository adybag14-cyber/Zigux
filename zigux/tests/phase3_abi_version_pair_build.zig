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

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_version_pair_abi_tests",
        .root_module = abi_bindings,
    });
    const version_tests = b.addTest(.{
        .name = "phase3_abi_version_pair_version_tests",
        .root_module = uapi_version,
    });

    const abi_run = b.addRunArtifact(abi_tests);
    const version_run = b.addRunArtifact(version_tests);

    const pair_step = b.step(
        "phase3-abi-version-pair-test",
        "Run the focused Phase 3 ABI bindings and UAPI version pair replay.",
    );
    pair_step.dependOn(&abi_run.step);
    pair_step.dependOn(&version_run.step);
}
