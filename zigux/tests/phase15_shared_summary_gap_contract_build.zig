const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_shared_summary_gap_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-shared-summary-gap-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const test_step = b.step(
        "phase15-shared-summary-gap-contract",
        "Run the focused Phase 15 shared-summary gap contract",
    );
    test_step.dependOn(&run_unit_tests.step);
}
