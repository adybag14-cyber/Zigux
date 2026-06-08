const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow fixture",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_command_slot_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("lane17_options", options);

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-command-slot-workflow-contract",
        "Validate Lane 17 Phase 1 workflow immediate command slots",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 command-slot workflow contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
