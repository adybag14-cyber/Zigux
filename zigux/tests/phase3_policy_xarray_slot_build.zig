const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const xarray_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_root.addImport("err_ptr", err_ptr);
    xarray_root.addImport("xa_value", xa_value);
    xarray_root.addImport("xarray_slot_view", xarray_slot_view);

    const policy_tests = b.addTest(.{
        .root_module = policy_root,
    });
    const run_policy_tests = b.addRunArtifact(policy_tests);

    const xarray_tests = b.addTest(.{
        .root_module = xarray_root,
    });
    const run_xarray_tests = b.addRunArtifact(xarray_tests);

    const test_step = b.step(
        "phase3-policy-xarray-slot-test",
        "Run the Phase 3 policy plus xarray-slot starter-packet self-checks",
    );
    test_step.dependOn(&run_policy_tests.step);
    test_step.dependOn(&run_xarray_tests.step);

    const alias_step = b.step("test", "Run the Phase 3 policy plus xarray-slot self-checks");
    alias_step.dependOn(test_step);

    b.default_step.dependOn(test_step);
}
