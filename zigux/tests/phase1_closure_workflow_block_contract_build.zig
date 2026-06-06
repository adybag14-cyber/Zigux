const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.option([]const u8, "repo-root", "repository root for runtime file checks") orelse "../..";
    const repo_root_path: std.Build.LazyPath = if (std.fs.path.isAbsolute(repo_root))
        .{ .cwd_relative = repo_root }
    else
        b.path(repo_root);

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_workflow_block_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(repo_root_path);

    const contract_step = b.step("phase1-closure-workflow-block-contract", "Validate the Phase 1 closure workflow block");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure workflow block contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
