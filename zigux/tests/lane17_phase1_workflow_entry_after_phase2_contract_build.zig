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
        .root_source_file = b.path("lane17_phase1_workflow_entry_after_phase2_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_phase1_workflow_entry_after_phase2_options", options);
    const tests = b.addTest(.{
        .name = "lane17-phase1-workflow-entry-after-phase2-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane17-phase1-workflow-entry-after-phase2-contract",
        "Run the Lane 17 Phase 1 workflow entry after Phase 2 contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 17 Phase 1 workflow entry after Phase 2 contract",
    );
    test_step.dependOn(&run_tests.step);
}
