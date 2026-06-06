const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });

    uapi_version.addImport("abi_bindings", abi_bindings);
    version_binding.addImport("uapi_version", uapi_version);
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const bitmap_cpumask_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    bitmap_cpumask_tests.root_module.addImport("bitmap_view", bitmap_view);
    bitmap_cpumask_tests.root_module.addImport("cpumask_view", cpumask_view);

    const notifier_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    notifier_tests.root_module.addImport("notifier_abi", notifier_abi);
    notifier_tests.root_module.addImport("notifier_view", notifier_view);

    const dev_t_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    dev_t_tests.root_module.addImport("uapi_dev_t", uapi_dev_t);
    dev_t_tests.root_module.addImport("dev_t_binding", dev_t_binding);
    dev_t_tests.root_module.addImport("version_binding", version_binding);
    dev_t_tests.root_module.addImport("export_shim", export_shim);

    const run_bitmap_cpumask = b.addRunArtifact(bitmap_cpumask_tests);
    const run_notifier = b.addRunArtifact(notifier_tests);
    const run_dev_t = b.addRunArtifact(dev_t_tests);

    const packet_step = b.step(
        "phase3-bitmap-cpumask-notifier-dev-t-test",
        "Run Phase 3 bitmap/cpumask, notifier, and dev_t starter packets together",
    );
    packet_step.dependOn(&run_bitmap_cpumask.step);
    packet_step.dependOn(&run_notifier.step);
    packet_step.dependOn(&run_dev_t.step);

    const test_step = b.step("test", "Run the Lane 04 bitmap/cpumask notifier dev_t harness");
    test_step.dependOn(packet_step);
    b.default_step.dependOn(test_step);
}
