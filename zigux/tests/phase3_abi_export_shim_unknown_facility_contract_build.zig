const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const export_shim_path = b.option(
        []const u8,
        "export-shim-path",
        "Path to export_shim.zig for focused validation",
    ) orelse "../kernel/export_shim.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings.addImport("notifier_abi.zig", notifier_abi);

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

    const export_shim = b.createModule(.{
        .root_source_file = b.path(export_shim_path),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_export_shim_unknown_facility_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("export_shim", export_shim);

    const tests = b.addTest(.{
        .name = "phase3-abi-export-shim-unknown-facility-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-abi-export-shim-unknown-facility-contract",
        "Run the Phase 3 ABI export-shim unknown-facility contract",
    );
    step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the Phase 3 ABI export-shim unknown-facility contract");
    default_step.dependOn(&run_tests.step);
}
