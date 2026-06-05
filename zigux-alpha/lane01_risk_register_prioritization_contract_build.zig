const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_risk_register_prioritization_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step("lane01-risk-register-prioritization-contract", "Run the Lane 01 risk-register prioritization contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 risk-register prioritization contract");
    test_step.dependOn(&run_tests.step);
}
