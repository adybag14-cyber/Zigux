const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow file to validate",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase9_phase7_phase10_phase11_workflow_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    contract_tests.root_module.addOptions("build_options", options);

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane17-phase9-phase7-phase10-phase11-workflow-contract",
        "Validate the Lane 17 Phase 9/7/10/11 workflow handoff contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 9/7/10/11 workflow contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
