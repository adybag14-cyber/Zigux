const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "Path to check-lane05-local-first-archive-workflow.py",
    ) orelse "check-lane05-local-first-archive-workflow.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_local_first_archive_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "lane05-local-first-archive-checker-contract",
        "Run the Lane 05 local-first archive checker source contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 05 local-first archive checker source contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
