const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_unsafe_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_unsafe_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_unsafe_policy_bytes_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("unsafe_policy", unsafe_policy_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-unsafe-policy-bytes-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-unsafe-policy-bytes-contract",
        "Run the focused Phase 3 ABI unsafe-policy byte contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 3 ABI unsafe-policy byte contract");
    test_step.dependOn(&run_tests.step);
}
