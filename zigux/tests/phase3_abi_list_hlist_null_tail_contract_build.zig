const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings_module.addImport("notifier_abi", notifier_abi_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_list_hlist_null_tail_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", abi_bindings_module);
    contract_module.addImport("notifier_abi", notifier_abi_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-list-hlist-null-tail-contract-tests",
        .root_module = contract_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-list-hlist-null-tail-contract",
        "Run Phase 3 ABI list/hlist null-head and tail relay contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 3 ABI list/hlist null-tail contract tests");
    test_step.dependOn(&run_tests.step);
}
