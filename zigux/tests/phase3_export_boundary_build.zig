const std = @import("std");

fn addExportSupportModules(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) struct {
    uapi_dev_t: *std.Build.Module,
    uapi_version: *std.Build.Module,
    abi_bindings: *std.Build.Module,
    dev_t_binding: *std.Build.Module,
    version_binding: *std.Build.Module,
    export_shim: *std.Build.Module,
} {
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    return .{
        .uapi_dev_t = uapi_dev_t,
        .uapi_version = uapi_version,
        .abi_bindings = abi_bindings,
        .dev_t_binding = dev_t_binding,
        .version_binding = version_binding,
        .export_shim = export_shim,
    };
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const modules = addExportSupportModules(b, target, optimize);

    const dev_t_root = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_root.addImport("uapi_dev_t", modules.uapi_dev_t);
    dev_t_root.addImport("dev_t_binding", modules.dev_t_binding);
    dev_t_root.addImport("version_binding", modules.version_binding);
    dev_t_root.addImport("export_shim", modules.export_shim);
    const dev_t_tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = dev_t_root,
    });
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const export_root = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi_layout.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_root.addImport("uapi_dev_t", modules.uapi_dev_t);
    export_root.addImport("uapi_version", modules.uapi_version);
    export_root.addImport("dev_t_binding", modules.dev_t_binding);
    export_root.addImport("version_binding", modules.version_binding);
    export_root.addImport("export_shim", modules.export_shim);
    const export_tests = b.addTest(.{
        .name = "phase3-export-uapi-layout",
        .root_module = export_root,
    });
    const run_export_tests = b.addRunArtifact(export_tests);

    const test_step = b.step(
        "phase3-export-boundary-test",
        "Run the Phase 3 export-boundary starter and layout replays",
    );
    test_step.dependOn(&run_dev_t_tests.step);
    test_step.dependOn(&run_export_tests.step);
}
