const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.option([]const u8, "repo-root", "Repository root for runtime file reads") orelse ".";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_kconfig_counts_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(.{ .cwd_relative = repo_root });

    const contract_step = b.step(
        "phase2-closure-kconfig-counts-contract",
        "Run the Lane 25 Phase 2 closure kconfig/confdata count contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 25 Phase 2 closure kconfig/confdata count contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
