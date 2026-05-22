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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("panic_policy", panic_policy);
    root_module.addImport("allocator_policy", allocator_policy);
    root_module.addImport("unsafe_policy", unsafe_policy);
    root_module.addImport("narrow_surface", narrow_surface);

    const exe = b.addExecutable(.{
        .name = "phase3-policy-dump",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(exe);

    const step = b.step(
        "phase3-policy-dump",
        "Dump the focused Phase 3 policy and unsafe substrate replay surface",
    );
    step.dependOn(&run.step);
}
