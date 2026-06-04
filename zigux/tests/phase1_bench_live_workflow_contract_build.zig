const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        ".github/workflows/zigux-bootstrap.yml",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "workflow", workflow);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench_live_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_bench_live_workflow_options", options);

    const tests = b.addTest(.{
        .name = "phase1-bench-live-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-bench-live-workflow-contract",
        "Run the Phase 1 bench live-check workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 bench live-check workflow contract",
    );
    test_step.dependOn(&run_tests.step);
}
