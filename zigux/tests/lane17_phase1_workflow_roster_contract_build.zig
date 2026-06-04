const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow to validate",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_workflow_roster_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-workflow-roster-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const named_step = b.step(
        "lane17-phase1-workflow-roster-contract",
        "Run the Lane 17 Phase 1 workflow roster contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 17 Phase 1 workflow roster contract",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(named_step);
}
