const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        ".github/workflows/zigux-bootstrap.yml",
        b.allocator,
        .limited(1024 * 1024),
    ) catch |err| {
        std.debug.panic("failed to read zigux-bootstrap workflow: {s}", .{@errorName(err)});
    };

    const workflow_options = b.addOptions();
    workflow_options.addOption([]const u8, "workflow_text", workflow_text);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_live_workflow_alignment.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("workflow_options", workflow_options);

    const run_tests = b.addRunArtifact(tests);
    const named_step = b.step(
        "lane17-phase1-bench-live-workflow-alignment",
        "Run the Lane 17 Phase 1 bench live workflow alignment contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 17 Phase 1 bench live workflow alignment contract",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(named_step);
}
