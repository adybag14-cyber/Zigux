const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
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
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const ida_alloc_packet = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_packet.addImport("ida_alloc_view", ida_alloc_view);
    ida_alloc_packet.addImport("ida_bitmap_view", ida_bitmap_view);

    const dev_t_packet = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_packet.addImport("uapi_dev_t", uapi_dev_t);
    dev_t_packet.addImport("dev_t_binding", dev_t_binding);
    dev_t_packet.addImport("version_binding", version_binding);
    dev_t_packet.addImport("export_shim", export_shim);

    const ida_alloc_tests = b.addTest(.{ .root_module = ida_alloc_packet });
    const dev_t_tests = b.addTest(.{ .root_module = dev_t_packet });

    const run_ida_alloc_tests = b.addRunArtifact(ida_alloc_tests);
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const test_step = b.step(
        "phase3-ida-alloc-dev-t-test",
        "Run the Phase 3 IDA allocation and dev_t starter packet self-checks",
    );
    test_step.dependOn(&run_ida_alloc_tests.step);
    test_step.dependOn(&run_dev_t_tests.step);

    const default_step = b.step("test", "Run the Phase 3 IDA allocation and dev_t starter packet self-checks");
    default_step.dependOn(test_step);
}
