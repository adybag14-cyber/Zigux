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
        .root_source_file = b.path("lane17_phase1_bench_to_shared_reminder_handoff.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("workflow_options", options);

    const tests = b.addTest(.{
        .name = "lane17-phase1-bench-to-shared-reminder-handoff",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const handoff_step = b.step(
        "lane17-phase1-bench-to-shared-reminder-handoff",
        "Run the Lane 17 Phase 1 bench to shared-reminder workflow handoff contract",
    );
    handoff_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 1 bench to shared-reminder workflow handoff contract");
    test_step.dependOn(&run_tests.step);
}
