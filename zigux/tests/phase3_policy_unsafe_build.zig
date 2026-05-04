const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    const rbtree_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);
    layout_assert_module.addImport("rbtree_bindings", rbtree_bindings_module);
    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const interop_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/interop_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    interop_policy_module.addImport("abi_bindings", abi_bindings_module);
    interop_policy_module.addImport("panic_policy", panic_policy_module);
    interop_policy_module.addImport("allocator_policy", allocator_policy_module);
    interop_policy_module.addImport("narrow_unsafe", narrow_unsafe_module);
    const mmio_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_bindings_module);
    mmio_module.addImport("interop_policy", interop_policy_module);
    mmio_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_unsafe.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("panic_policy", panic_policy_module);
    root_module.addImport("allocator_policy", allocator_policy_module);
    root_module.addImport("interop_policy", interop_policy_module);
    root_module.addImport("layout_assert", layout_assert_module);
    root_module.addImport("mmio", mmio_module);
    root_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const tests = b.addTest(.{
        .name = "phase3-policy-unsafe-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-policy-unsafe-test",
        "Run focused Phase 3 policy and unsafe substrate tests",
    );
    test_step.dependOn(&run_tests.step);
}
