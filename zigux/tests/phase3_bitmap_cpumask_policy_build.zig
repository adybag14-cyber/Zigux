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
    cpumask_view.addImport("bitmap_view", bitmap_view);

    const bitmap_cpumask_packet = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_cpumask_packet.addImport("bitmap_view", bitmap_view);
    bitmap_cpumask_packet.addImport("cpumask_view", cpumask_view);

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

    const policy_packet = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_packet.addImport("abi_bindings", abi_bindings);
    policy_packet.addImport("panic_policy", panic_policy);
    policy_packet.addImport("allocator_policy", allocator_policy);
    policy_packet.addImport("unsafe_policy", unsafe_policy);
    policy_packet.addImport("layout_assert", layout_assert);
    policy_packet.addImport("narrow_surface", narrow_surface);

    const bitmap_cpumask_tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-starter-packet",
        .root_module = bitmap_cpumask_packet,
    });
    const run_bitmap_cpumask_tests = b.addRunArtifact(bitmap_cpumask_tests);

    const policy_tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = policy_packet,
    });
    const run_policy_tests = b.addRunArtifact(policy_tests);

    const combined_step = b.step(
        "phase3-bitmap-cpumask-policy-test",
        "Run the Phase 3 bitmap/cpumask and policy starter packets together",
    );
    combined_step.dependOn(&run_bitmap_cpumask_tests.step);
    combined_step.dependOn(&run_policy_tests.step);

    const default_step = b.step(
        "test",
        "Run the Phase 3 bitmap/cpumask and policy starter-packet tests",
    );
    default_step.dependOn(combined_step);
    b.default_step.dependOn(default_step);
}
