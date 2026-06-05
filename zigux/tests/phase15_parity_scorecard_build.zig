const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_parity_scorecard.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-parity-scorecard-tests",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const parity_step = b.step(
        "phase15-parity-scorecard",
        "Run the focused Phase 15 parity-scorecard test",
    );
    parity_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 parity-scorecard test");
    test_step.dependOn(&run_unit_tests.step);
}
