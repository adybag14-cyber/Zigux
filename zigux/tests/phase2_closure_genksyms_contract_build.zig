const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_genksyms_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase2-closure-genksyms-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const test_step = b.step("test", "Run the focused Phase 2 genksyms closure contract.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
