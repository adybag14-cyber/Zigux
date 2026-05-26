const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);

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

    const tests_mod = b.createModule(.{
        .root_source_file = b.path("phase3_policy_gate_relay.zig"),
        .target = target,
        .optimize = optimize,
    });
    tests_mod.addImport("abi_bindings", abi_bindings);
    tests_mod.addImport("allocator_policy", allocator_policy);
    tests_mod.addImport("panic_policy", panic_policy);
    tests_mod.addImport("narrow", narrow);

    const tests = b.addTest(.{
        .name = "phase3-policy-gate-relay-test",
        .root_module = tests_mod,
    });
    const run = b.addRunArtifact(tests);

    const relay_step = b.step(
        "phase3-policy-gate-relay-test",
        "Run the standalone Phase 3 policy-gate relay tests",
    );
    relay_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the standalone Phase 3 policy-gate relay tests",
    );
    test_step.dependOn(&run.step);
}
