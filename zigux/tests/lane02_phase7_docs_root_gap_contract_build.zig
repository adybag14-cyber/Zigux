const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.path("../..");

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane02_phase7_docs_root_gap_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(repo_root);

    const contract_step = b.step(
        "lane02-phase7-docs-root-gap-contract",
        "Run the Lane 02 Phase 7 docs-root gap contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 02 Phase 7 docs-root gap contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
