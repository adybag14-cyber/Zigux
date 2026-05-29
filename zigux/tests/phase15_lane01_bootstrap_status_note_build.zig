const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase15_lane01_bootstrap_status_note.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase15-lane01-bootstrap-status-note",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("phase15-lane01-bootstrap-status-note", "Run Lane 01 bootstrap status-note guard");
    test_step.dependOn(&run_tests.step);
}
