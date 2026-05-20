const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);
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
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);
    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);

    const errptr_xarray_starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_starter_root.addImport("err_ptr", err_ptr);
    errptr_xarray_starter_root.addImport("xa_value", xa_value);

    const low_level_root = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_root.addImport("atomic", atomic);
    low_level_root.addImport("barrier", barrier);
    low_level_root.addImport("mmio", mmio);
    low_level_root.addImport("unsafe_policy", unsafe_policy);
    low_level_root.addImport("narrow", narrow);

    const starter_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_starter_root,
    });
    const low_level_tests = b.addTest(.{
        .name = "phase3-low-level-wrappers",
        .root_module = low_level_root,
    });

    const run_starter_tests = b.addRunArtifact(starter_tests);
    const run_low_level_tests = b.addRunArtifact(low_level_tests);

    const test_step = b.step(
        "phase3-errptr-low-level-test",
        "Run the Phase 3 err_ptr plus low-level wrapper replay",
    );
    test_step.dependOn(&run_starter_tests.step);
    test_step.dependOn(&run_low_level_tests.step);
}
