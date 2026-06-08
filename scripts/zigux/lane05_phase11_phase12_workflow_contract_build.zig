const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow file",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_phase11_phase12_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("lane05_options", options);

    const contract_tests = b.addTest(.{
        .name = "lane05-phase11-phase12-workflow-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);
    run_contract.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane05-phase11-phase12-workflow-contract",
        "Run Lane 05 Phase 11/12 workflow handoff contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Lane 05 Phase 11/12 workflow handoff contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
