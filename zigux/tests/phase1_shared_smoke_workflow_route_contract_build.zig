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
        .root_source_file = b.path("phase1_shared_smoke_workflow_route_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("phase1_shared_smoke_workflow_route_options", options);

    const tests = b.addTest(.{
        .name = "phase1-shared-smoke-workflow-route-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase1-shared-smoke-workflow-route-contract",
        "Check the Phase 1 shared tests-root smoke workflow route",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 shared smoke workflow route contract");
    test_step.dependOn(&run_tests.step);
}
