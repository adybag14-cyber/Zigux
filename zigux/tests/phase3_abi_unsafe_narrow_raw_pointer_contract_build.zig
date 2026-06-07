const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings.addImport("notifier_abi", b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const unsafe_narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_narrow.addImport("abi_bindings", abi_bindings);

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_unsafe_narrow_raw_pointer_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("abi_bindings", abi_bindings);
    test_module.addImport("unsafe_narrow", unsafe_narrow);

    const tests = b.addTest(.{
        .name = "phase3_abi_unsafe_narrow_raw_pointer_contract",
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-unsafe-narrow-raw-pointer-contract",
        "Run the Phase 3 ABI unsafe narrow raw pointer bridge contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run this build shard's contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
