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

    const dump_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    dump_root_module.addImport("abi_bindings", abi_bindings);
    dump_root_module.addImport("panic_policy", panic_policy);
    dump_root_module.addImport("allocator_policy", allocator_policy);
    dump_root_module.addImport("unsafe_policy", unsafe_policy);
    dump_root_module.addImport("narrow_surface", narrow_surface);

    const dump_exe = b.addExecutable(.{
        .name = "phase3-policy-dump-unsafe-pair-dump",
        .root_module = dump_root_module,
    });
    const run_dump = b.addRunArtifact(dump_exe);

    const unsafe_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_unsafe.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_root_module.addImport("abi_bindings", abi_bindings);
    unsafe_root_module.addImport("panic_policy", panic_policy);
    unsafe_root_module.addImport("allocator_policy", allocator_policy);
    unsafe_root_module.addImport("unsafe_policy", unsafe_policy);
    unsafe_root_module.addImport("narrow", narrow_surface);

    const unsafe_tests = b.addTest(.{
        .name = "phase3-policy-dump-unsafe-pair-replay",
        .root_module = unsafe_root_module,
    });
    const run_unsafe_tests = b.addRunArtifact(unsafe_tests);

    const pair_step = b.step(
        "phase3-policy-dump-unsafe-pair-test",
        "Run the focused Phase 3 policy dump beside the dedicated policy and unsafe replay",
    );
    pair_step.dependOn(&run_dump.step);
    pair_step.dependOn(&run_unsafe_tests.step);
}
