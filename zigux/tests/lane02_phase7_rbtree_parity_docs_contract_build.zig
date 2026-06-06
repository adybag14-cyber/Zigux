const std = @import("std");

fn repoRootPath(b: *std.Build, repo_root: []const u8) std.Build.LazyPath {
    if (std.fs.path.isAbsolute(repo_root)) {
        return .{ .cwd_relative = repo_root };
    }
    return b.path(repo_root);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.option([]const u8, "repo-root", "Repository root for runtime reads") orelse "../..";

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane02_phase7_rbtree_parity_docs_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane02-phase7-rbtree-parity-docs-contract",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);
    run.setCwd(repoRootPath(b, repo_root));

    const contract_step = b.step(
        "lane02-phase7-rbtree-parity-docs-contract",
        "Run the Lane 02 Phase 7 rbtree parity docs contract",
    );
    contract_step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 7 rbtree parity docs contract");
    test_step.dependOn(&run.step);
}
