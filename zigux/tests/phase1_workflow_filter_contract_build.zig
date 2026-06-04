const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        b.pathFromRoot("../../.github/workflows/zigux-bootstrap.yml"),
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "workflow", workflow);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_workflow_filter_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_workflow_filter_options", options);

    const tests = b.addTest(.{
        .name = "phase1-workflow-filter-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-workflow-filter-contract",
        "Run the Phase 1 workflow path-filter contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 workflow path-filter contract",
    );
    test_step.dependOn(&run_tests.step);
}
