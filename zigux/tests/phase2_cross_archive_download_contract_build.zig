const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_archive_download_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step("phase2-cross-archive-download-contract", "Run the Phase 2 cross archive download contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross archive download contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(contract_step);
}
