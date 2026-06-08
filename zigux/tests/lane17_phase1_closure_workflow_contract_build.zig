const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the workflow YAML under test",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        workflow_path,
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_closure_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("workflow_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-closure-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-closure-workflow-contract",
        "Run the Lane 17 Phase 1 closure workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 closure workflow contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
