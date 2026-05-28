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

    const idr_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view.addImport("xarray_slot_view", xarray_slot_view);
    idr_slot_view.addImport("xa_value", xa_value);

    const idr_slot_starter = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_starter.addImport("err_ptr", err_ptr);
    idr_slot_starter.addImport("xa_value", xa_value);
    idr_slot_starter.addImport("xarray_slot_view", xarray_slot_view);
    idr_slot_starter.addImport("idr_slot_view", idr_slot_view);

    const idr_slot_tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = idr_slot_starter,
    });
    const run_idr_slot_tests = b.addRunArtifact(idr_slot_tests);

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

    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);

    const narrow_surface = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface.addImport("abi_bindings", abi_bindings);

    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow_surface);

    const policy_starter = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_starter.addImport("abi_bindings", abi_bindings);
    policy_starter.addImport("panic_policy", panic_policy);
    policy_starter.addImport("allocator_policy", allocator_policy);
    policy_starter.addImport("unsafe_policy", unsafe_policy);
    policy_starter.addImport("layout_assert", layout_assert);
    policy_starter.addImport("narrow_surface", narrow_surface);

    const policy_tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = policy_starter,
    });
    const run_policy_tests = b.addRunArtifact(policy_tests);

    const test_step = b.step(
        "phase3-idr-slot-policy-test",
        "Run the Phase 3 idr-slot starter packet beside the policy starter packet",
    );
    test_step.dependOn(&run_idr_slot_tests.step);
    test_step.dependOn(&run_policy_tests.step);
}
