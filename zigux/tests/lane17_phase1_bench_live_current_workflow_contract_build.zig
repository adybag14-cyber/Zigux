const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", ".github/workflows/zigux-bootstrap.yml");

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_bench_live_current_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-bench-live-current-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane17-phase1-bench-live-current-workflow-contract",
        "Run the Lane 17 Phase 1 bench live current-workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 bench live current-workflow contract");
    test_step.dependOn(&run_tests.step);
}
