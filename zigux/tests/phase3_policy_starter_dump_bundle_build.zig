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

    const starter_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    starter_module.addImport("abi_bindings", abi_bindings);
    starter_module.addImport("panic_policy", panic_policy);
    starter_module.addImport("allocator_policy", allocator_policy);
    starter_module.addImport("unsafe_policy", unsafe_policy);
    starter_module.addImport("layout_assert", layout_assert);
    starter_module.addImport("narrow_surface", narrow_surface);

    const starter_tests = b.addTest(.{
        .root_module = starter_module,
    });
    const run_starter_tests = b.addRunArtifact(starter_tests);

    const dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    dump_module.addImport("abi_bindings", abi_bindings);
    dump_module.addImport("panic_policy", panic_policy);
    dump_module.addImport("allocator_policy", allocator_policy);
    dump_module.addImport("unsafe_policy", unsafe_policy);
    dump_module.addImport("narrow_surface", narrow_surface);

    const dump_exe = b.addExecutable(.{
        .name = "phase3-policy-dump",
        .root_module = dump_module,
    });
    const run_dump = b.addRunArtifact(dump_exe);

    const bundle_step = b.step(
        "phase3-policy-starter-dump-bundle",
        "Run the Phase 3 policy starter packet and dump packet together",
    );
    bundle_step.dependOn(&run_starter_tests.step);
    bundle_step.dependOn(&run_dump.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 policy starter and dump bundle",
    );
    test_step.dependOn(bundle_step);
    b.default_step.dependOn(test_step);
}
