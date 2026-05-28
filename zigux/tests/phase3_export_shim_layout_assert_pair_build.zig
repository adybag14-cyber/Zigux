const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });

    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("uapi_version", uapi_version_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);
    export_shim_module.addImport("uapi_dev_t", uapi_dev_t_module);
    export_shim_module.addImport("uapi_version", uapi_version_module);

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const export_shim_tests = b.addTest(.{
        .name = "phase3_export_shim_pair_tests",
        .root_module = export_shim_module,
    });
    const layout_assert_tests = b.addTest(.{
        .name = "phase3_layout_assert_pair_tests",
        .root_module = layout_assert_module,
    });

    const run_export_shim_tests = b.addRunArtifact(export_shim_tests);
    const run_layout_assert_tests = b.addRunArtifact(layout_assert_tests);
    const test_step = b.step(
        "phase3-export-shim-layout-assert-pair-test",
        "Run the focused Phase 3 export shim and layout-assert pair replay",
    );
    test_step.dependOn(&run_export_shim_tests.step);
    test_step.dependOn(&run_layout_assert_tests.step);
}
