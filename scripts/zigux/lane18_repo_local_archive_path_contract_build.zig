const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane18_repo_local_archive_path_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane18-repo-local-archive-path-contract",
        "Run the Lane 18 repo-local archive path contract tests.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 18 repo-local archive path contract tests.");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
