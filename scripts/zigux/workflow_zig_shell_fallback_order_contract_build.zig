const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("workflow_zig_shell_fallback_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .root_module = module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const named_step = b.step("workflow-zig-shell-fallback-order-contract", "Run the Zigux bootstrap workflow shell fallback order contract");
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Zigux bootstrap workflow shell fallback order contract");
    test_step.dependOn(&run_contract_tests.step);
}
