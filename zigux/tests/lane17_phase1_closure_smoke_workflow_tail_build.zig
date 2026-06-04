const std = @import("std");

fn readRootFile(b: *std.Build, path: []const u8) []const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        b.pathFromRoot(path),
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| std.debug.panic("failed to read {s}: {}", .{ path, err });
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const sources = b.addOptions();
    sources.addOption([]const u8, "workflow_text", readRootFile(b, "../../.github/workflows/zigux-bootstrap.yml"));

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_closure_smoke_workflow_tail.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_phase1_closure_smoke_workflow_tail_sources", sources);

    const tests = b.addTest(.{
        .name = "lane17-phase1-closure-smoke-workflow-tail-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const lane_step = b.step(
        "lane17-phase1-closure-smoke-workflow-tail",
        "Validate Lane 17 Phase 1 closure-to-smoke workflow tail",
    );
    lane_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 17 Phase 1 closure-to-smoke workflow tail tests");
    test_step.dependOn(&run_tests.step);
}
