const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const alignment_module = b.createModule(.{
        .root_source_file = b.path("phase15_indefinite_c_lane_owner_alignment.zig"),
        .target = target,
        .optimize = optimize,
    });

    const alignment_tests = b.addTest(.{
        .name = "phase15-indefinite-c-lane-owner-alignment-tests",
        .root_module = alignment_module,
    });
    const run_alignment_tests = b.addRunArtifact(alignment_tests);
    run_alignment_tests.setCwd(b.path("../.."));

    const alignment_step = b.step(
        "phase15-indefinite-c-lane-owner-alignment",
        "Run the focused Phase 15 indefinite-C lane-owner alignment test",
    );
    alignment_step.dependOn(&run_alignment_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 indefinite-C lane-owner alignment test");
    test_step.dependOn(&run_alignment_tests.step);
}
