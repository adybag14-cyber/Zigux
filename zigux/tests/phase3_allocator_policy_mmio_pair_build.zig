const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);

    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const mmio_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_bindings_module);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);
    mmio_module.addImport("narrow_unsafe", unsafe_policy_module);

    const allocator_policy_tests = b.addTest(.{
        .name = "phase3_allocator_policy_mmio_pair_allocator_policy_tests",
        .root_module = allocator_policy_module,
    });
    const mmio_tests = b.addTest(.{
        .name = "phase3_allocator_policy_mmio_pair_mmio_tests",
        .root_module = mmio_module,
    });

    const run_allocator_policy_tests = b.addRunArtifact(allocator_policy_tests);
    const run_mmio_tests = b.addRunArtifact(mmio_tests);

    const test_step = b.step(
        "phase3-allocator-policy-mmio-pair-test",
        "Run the Phase 3 allocator-policy/MMIO helper pair shard",
    );
    test_step.dependOn(&run_allocator_policy_tests.step);
    test_step.dependOn(&run_mmio_tests.step);
}
