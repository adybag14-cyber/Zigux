const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_workflow_archive_cache_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract = b.addRunArtifact(contract);
    run_contract.setCwd(b.path("../.."));

    const test_step = b.step("phase2-cross-workflow-archive-cache-contract", "Run the Phase 2 cross workflow archive/cache contract");
    test_step.dependOn(&run_contract.step);

    const run_tests = b.addRunArtifact(contract);
    run_tests.setCwd(b.path("../.."));

    const test_alias = b.step("test", "Run Phase 2 cross workflow archive/cache contract tests");
    test_alias.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
