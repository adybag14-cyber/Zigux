const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_decision_index_no_approval_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-decision-index-no-approval-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const contract = b.step(
        "phase15-decision-index-no-approval-contract",
        "Run the focused Phase 15 decision-index no-approval contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 decision-index no-approval contract");
    test_step.dependOn(&run_unit_tests.step);
}
