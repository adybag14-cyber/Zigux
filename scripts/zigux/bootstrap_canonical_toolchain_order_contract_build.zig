const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("bootstrap_canonical_toolchain_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "bootstrap-canonical-toolchain-order-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "bootstrap-canonical-toolchain-order-contract",
        "Run the Lane 03 bootstrap canonical toolchain order contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 03 bootstrap canonical toolchain order contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
