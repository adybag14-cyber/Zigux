const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_notifier_list_length_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("notifier_abi", notifier_abi_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-notifier-list-length-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-notifier-list-length-contract",
        "Run the Phase 3 ABI notifier list length contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI notifier list length contract");
    test_step.dependOn(contract_step);

    b.default_step.dependOn(&run_contract_tests.step);
}
