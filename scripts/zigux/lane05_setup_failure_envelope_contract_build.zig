const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_setup_failure_envelope_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-setup-failure-envelope-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane05-setup-failure-envelope-contract",
        "Run the Lane 05 setup failure envelope contract.",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 05 setup failure envelope contract tests.");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
