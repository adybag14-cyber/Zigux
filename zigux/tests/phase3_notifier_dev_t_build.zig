const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view_module.addImport("notifier_abi", notifier_abi_module);

    const notifier_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_packet_module.addImport("notifier_abi", notifier_abi_module);
    notifier_packet_module.addImport("notifier_view", notifier_view_module);

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

    const dev_t_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_packet_module.addImport("uapi_dev_t", uapi_dev_t_module);
    dev_t_packet_module.addImport("dev_t_binding", dev_t_binding_module);
    dev_t_packet_module.addImport("version_binding", version_binding_module);
    dev_t_packet_module.addImport("export_shim", export_shim_module);

    const notifier_tests = b.addTest(.{
        .name = "phase3-notifier-starter-packet",
        .root_module = notifier_packet_module,
    });
    const dev_t_tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = dev_t_packet_module,
    });

    const run_notifier_tests = b.addRunArtifact(notifier_tests);
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const test_step = b.step(
        "phase3-notifier-dev-t-test",
        "Run the Phase 3 notifier and dev_t starter packets together",
    );
    test_step.dependOn(&run_notifier_tests.step);
    test_step.dependOn(&run_dev_t_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 notifier and dev_t starter packets");
    default_test_step.dependOn(test_step);
}
