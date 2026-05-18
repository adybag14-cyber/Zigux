const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const xarray_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view.addImport("err_ptr", err_ptr);
    xarray_slot_view.addImport("xa_value", xa_value);

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_surface = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface.addImport("abi_bindings", abi_bindings);
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
    const mmio = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio.addImport("abi_bindings", abi_bindings);
    mmio.addImport("unsafe_policy", unsafe_policy);

    const errptr_xarray_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_root.addImport("err_ptr", err_ptr);
    errptr_xarray_root.addImport("xa_value", xa_value);
    const errptr_xarray_tests = b.addTest(.{
        .root_module = errptr_xarray_root,
    });
    const run_errptr_xarray_tests = b.addRunArtifact(errptr_xarray_tests);

    const xarray_slot_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_root.addImport("err_ptr", err_ptr);
    xarray_slot_root.addImport("xa_value", xa_value);
    xarray_slot_root.addImport("xarray_slot_view", xarray_slot_view);
    const xarray_slot_tests = b.addTest(.{
        .root_module = xarray_slot_root,
    });
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);

    const errptr_xarray_dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_dump_root.addImport("err_ptr", err_ptr);
    errptr_xarray_dump_root.addImport("xa_value", xa_value);
    const errptr_xarray_dump = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = errptr_xarray_dump_root,
    });
    const run_errptr_xarray_dump = b.addRunArtifact(errptr_xarray_dump);

    const policy_root = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_root.addImport("abi_bindings", abi_bindings);
    policy_root.addImport("panic_policy", panic_policy);
    policy_root.addImport("allocator_policy", allocator_policy);
    policy_root.addImport("unsafe_policy", unsafe_policy);
    policy_root.addImport("layout_assert", layout_assert);
    policy_root.addImport("narrow_surface", narrow_surface);
    const policy_tests = b.addTest(.{
        .root_module = policy_root,
    });
    const run_policy_tests = b.addRunArtifact(policy_tests);

    const low_level_root = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_root.addImport("atomic", atomic);
    low_level_root.addImport("barrier", barrier);
    low_level_root.addImport("mmio", mmio);
    const low_level_tests = b.addTest(.{
        .root_module = low_level_root,
    });
    const run_low_level_tests = b.addRunArtifact(low_level_tests);

    const helper_local_step = b.step(
        "phase3-helper-local-test",
        "Run the bounded Phase 3 helper-local packet bundle",
    );
    helper_local_step.dependOn(&run_errptr_xarray_tests.step);
    helper_local_step.dependOn(&run_xarray_slot_tests.step);
    helper_local_step.dependOn(&run_errptr_xarray_dump.step);
    helper_local_step.dependOn(&run_policy_tests.step);
    helper_local_step.dependOn(&run_low_level_tests.step);
}
