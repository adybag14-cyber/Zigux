const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_surface_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);
    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);
    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_surface_module);
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const err_ptr_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_module.addImport("err_ptr", err_ptr_module);

    const policy_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_packet_module.addImport("abi_bindings", abi_bindings_module);
    policy_packet_module.addImport("allocator_policy", allocator_policy_module);
    policy_packet_module.addImport("panic_policy", panic_policy_module);
    policy_packet_module.addImport("unsafe_policy", unsafe_policy_module);
    policy_packet_module.addImport("layout_assert", layout_assert_module);
    policy_packet_module.addImport("narrow_surface", narrow_surface_module);

    const errptr_xarray_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_packet_module.addImport("err_ptr", err_ptr_module);
    errptr_xarray_packet_module.addImport("xa_value", xa_value_module);

    const policy_tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = policy_packet_module,
    });
    const errptr_xarray_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_packet_module,
    });

    const run_policy_tests = b.addRunArtifact(policy_tests);
    const run_errptr_xarray_tests = b.addRunArtifact(errptr_xarray_tests);

    const test_step = b.step(
        "phase3-policy-errptr-xarray-test",
        "Run the Phase 3 policy and errptr/xarray starter packets together",
    );
    test_step.dependOn(&run_policy_tests.step);
    test_step.dependOn(&run_errptr_xarray_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 policy and errptr/xarray starter packets");
    default_test_step.dependOn(test_step);
}
