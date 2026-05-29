const std = @import("std");

fn addIdaRangePacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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
    const ida_range_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view.addImport("ida_bitmap_view", ida_bitmap_view);
    ida_range_view.addImport("ida_alloc_view", ida_alloc_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);
    root_module.addImport("ida_range_view", ida_range_view);

    const tests = b.addTest(.{
        .name = "phase3-ida-range-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPolicyPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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
    unsafe_policy.addImport("narrow_unsafe", narrow_surface);
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("allocator_policy", allocator_policy);
    root_module.addImport("panic_policy", panic_policy);
    root_module.addImport("unsafe_policy", unsafe_policy);
    root_module.addImport("layout_assert", layout_assert);
    root_module.addImport("narrow_surface", narrow_surface);

    const tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_range_packet = addIdaRangePacket(b, target, optimize);
    const policy_packet = addPolicyPacket(b, target, optimize);

    const test_step = b.step(
        "phase3-ida-range-policy-test",
        "Run the Phase 3 IDA range and policy starter packets together",
    );
    test_step.dependOn(&ida_range_packet.step);
    test_step.dependOn(&policy_packet.step);

    const default_step = b.step("test", "Run the Phase 3 IDA range and policy starter packets");
    default_step.dependOn(&ida_range_packet.step);
    default_step.dependOn(&policy_packet.step);
}
