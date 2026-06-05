const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_phase4_tail_gate_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("config", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-phase4-tail-gate-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-phase4-tail-gate-contract",
        "Check Lane 17 Phase 1 to Phase 4 workflow tail gates",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 to Phase 4 workflow tail gate contract");
    test_step.dependOn(&run_tests.step);
}
