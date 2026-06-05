const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_indefinite_c_lane_owner_alignment.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-indefinite-c-lane-owner-alignment-tests",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const lane_owner_step = b.step(
        "phase15-indefinite-c-lane-owner-alignment",
        "Run the focused Phase 15 indefinite-C lane-owner alignment test",
    );
    lane_owner_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 indefinite-C lane-owner alignment test");
    test_step.dependOn(&run_unit_tests.step);
}
