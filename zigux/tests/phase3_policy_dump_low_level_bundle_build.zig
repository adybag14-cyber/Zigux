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
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow);
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
    mmio.addImport("narrow_unsafe", narrow);

    const dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    dump_module.addImport("abi_bindings", abi_bindings);
    dump_module.addImport("panic_policy", panic_policy);
    dump_module.addImport("allocator_policy", allocator_policy);
    dump_module.addImport("unsafe_policy", unsafe_policy);
    dump_module.addImport("narrow_surface", narrow);

    const dump_exe = b.addExecutable(.{
        .name = "phase3-policy-dump",
        .root_module = dump_module,
    });
    const run_dump = b.addRunArtifact(dump_exe);

    const low_level_module = b.createModule(.{
        .root_source_file = b.path("phase3_low_level_wrappers.zig"),
        .target = target,
        .optimize = optimize,
    });
    low_level_module.addImport("atomic", atomic);
    low_level_module.addImport("abi_bindings", abi_bindings);
    low_level_module.addImport("barrier", barrier);
    low_level_module.addImport("allocator_policy", allocator_policy);
    low_level_module.addImport("layout_assert", layout_assert);
    low_level_module.addImport("mmio", mmio);
    low_level_module.addImport("panic_policy", panic_policy);
    low_level_module.addImport("unsafe_policy", unsafe_policy);
    low_level_module.addImport("narrow", narrow);

    const low_level_tests = b.addTest(.{
        .root_module = low_level_module,
    });
    const run_low_level_tests = b.addRunArtifact(low_level_tests);

    const bundle_step = b.step(
        "phase3-policy-dump-low-level-bundle",
        "Run the Phase 3 policy dump and low-level wrapper packets together",
    );
    bundle_step.dependOn(&run_dump.step);
    bundle_step.dependOn(&run_low_level_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 policy dump and low-level wrapper bundle",
    );
    test_step.dependOn(bundle_step);
    b.default_step.dependOn(test_step);
}
