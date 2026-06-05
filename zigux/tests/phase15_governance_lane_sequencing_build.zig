const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_governance_lane_sequencing.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-governance-lane-sequencing",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "phase15-governance-lane-sequencing",
        "Run the focused Phase 15 governance-lane sequencing test",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 governance-lane sequencing test");
    test_step.dependOn(&run_unit_tests.step);
}
