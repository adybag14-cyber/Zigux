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

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_bootstrap_preflight_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("build_options", options);

    const contract_tests = b.addTest(.{
        .name = "lane17-bootstrap-preflight-contract",
        .root_module = contract_module,
    });

    const run_contract = b.addRunArtifact(contract_tests);
    const contract_step = b.step("lane17-bootstrap-preflight-contract", "Run the Lane 17 bootstrap preflight contract");
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 17 bootstrap preflight contract");
    test_step.dependOn(&run_contract.step);
}
