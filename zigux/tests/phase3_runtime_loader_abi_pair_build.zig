const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_loader_contract_module = b.createModule(.{
        .root_source_file = b.path("../kernel/runtime_loader_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_loader_contract_module.addImport("abi_bindings", abi_bindings_module);

    const abi_tests = b.addTest(.{
        .name = "phase3-abi-binding-pair-tests",
        .root_module = abi_bindings_module,
    });
    const runtime_loader_contract_tests = b.addTest(.{
        .name = "phase3-runtime-loader-contract-pair-tests",
        .root_module = runtime_loader_contract_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);

    const test_step = b.step(
        "phase3-runtime-loader-abi-pair-test",
        "Run the focused Phase 3 ABI binding plus runtime-loader contract pair tests",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_runtime_loader_contract_tests.step);

    const all_tests = b.step("test", "Run the focused Phase 3 ABI pair build tests");
    all_tests.dependOn(test_step);
}
