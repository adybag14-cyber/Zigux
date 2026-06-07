const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version.addImport("abi_bindings", abi_bindings);

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

    const atomic = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow);
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);
    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);

    const dev_t_root = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_root.addImport("uapi_dev_t", uapi_dev_t);
    dev_t_root.addImport("dev_t_binding", dev_t_binding);
    dev_t_root.addImport("version_binding", version_binding);
    dev_t_root.addImport("export_shim", export_shim);

    const low_level_root = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_root.addImport("atomic", atomic);
    low_level_root.addImport("barrier", barrier);
    low_level_root.addImport("layout_assert", layout_assert);
    low_level_root.addImport("mmio", mmio);
    low_level_root.addImport("unsafe_policy", unsafe_policy);
    low_level_root.addImport("narrow", narrow);

    const dev_t_tests = b.addTest(.{
        .root_module = dev_t_root,
    });
    const low_level_tests = b.addTest(.{
        .root_module = low_level_root,
    });
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);
    const run_low_level_tests = b.addRunArtifact(low_level_tests);

    const test_step = b.step(
        "phase3-dev-t-low-level-test",
        "Run the Phase 3 dev_t starter and low-level wrapper packets",
    );
    test_step.dependOn(&run_dev_t_tests.step);
    test_step.dependOn(&run_low_level_tests.step);

    const default_step = b.step("test", "Run the Phase 3 dev_t starter and low-level wrapper packets");
    default_step.dependOn(test_step);
    b.default_step.dependOn(test_step);
}
