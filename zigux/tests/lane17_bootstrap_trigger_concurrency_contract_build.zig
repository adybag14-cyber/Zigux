const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow file",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_bootstrap_trigger_concurrency_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane17-bootstrap-trigger-concurrency-contract",
        .root_module = root_module,
    });

    const run_contract = b.addRunArtifact(tests);
    const contract_step = b.step(
        "lane17-bootstrap-trigger-concurrency-contract",
        "Run the Lane 17 bootstrap trigger and concurrency workflow contract",
    );
    contract_step.dependOn(&run_contract.step);

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("test", "Run the Lane 17 bootstrap trigger and concurrency workflow contract");
    test_step.dependOn(&run_tests.step);
}
