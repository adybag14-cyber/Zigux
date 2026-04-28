const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("export_shim", export_shim_module);
    root_module.addImport("uapi_version", uapi_version_module);

    const tests = b.addTest(.{
        .name = "phase3-export-uapi-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("phase3-export-uapi-test", "Run Phase 3 export shim and uapi smoke tests");
    test_step.dependOn(&run_tests.step);
}
