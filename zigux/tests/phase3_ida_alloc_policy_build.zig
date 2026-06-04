const std = @import("std");

fn addIdaAllocPolicyTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
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
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);
    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);
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
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);

    const ida_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_root.addImport("ida_alloc_view", ida_alloc_view);
    ida_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const policy_root = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_root.addImport("abi_bindings", abi_bindings);
    policy_root.addImport("allocator_policy", allocator_policy);
    policy_root.addImport("panic_policy", panic_policy);
    policy_root.addImport("unsafe_policy", unsafe_policy);
    policy_root.addImport("layout_assert", layout_assert);
    policy_root.addImport("narrow_surface", narrow_surface);

    const ida_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = ida_root,
    });
    const policy_tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = policy_root,
    });

    const step = b.step(
        "phase3-ida-alloc-policy-test",
        "Run the Phase 3 IDA allocation and policy starter packets together",
    );
    const ida_run = b.addRunArtifact(ida_tests);
    const policy_run = b.addRunArtifact(policy_tests);
    step.dependOn(&ida_run.step);
    step.dependOn(&policy_run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = addIdaAllocPolicyTest(b, target, optimize);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation plus policy harness");
    test_step.dependOn(tests);
}
