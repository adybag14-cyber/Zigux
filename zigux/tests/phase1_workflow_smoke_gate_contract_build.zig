const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        ".github/workflows/zigux-bootstrap.yml",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| @panic(@errorName(err));

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_workflow_smoke_gate_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("workflow_options", options);

    const tests = b.addTest(.{
        .name = "phase1-workflow-smoke-gate-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase1-workflow-smoke-gate-contract",
        "Run the Phase 1 shared-smoke workflow gate contract",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 shared-smoke workflow gate contract");
    test_step.dependOn(&run_tests.step);
}
