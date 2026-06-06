const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane02_phase4_docs_root_exact_readback_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane02-phase4-docs-root-exact-readback-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane02-phase4-docs-root-exact-readback-contract",
        "Run the Lane 02 Phase 4 docs-root exact-readback contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 4 docs-root exact-readback contract");
    test_step.dependOn(&run_contract_tests.step);
}
