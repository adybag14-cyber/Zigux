const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const decision_index_module = b.createModule(.{
        .root_source_file = b.path("phase15_architecture_council_decision_index.zig"),
        .target = target,
        .optimize = optimize,
    });

    const decision_index_tests = b.addTest(.{
        .name = "phase15-architecture-council-decision-index-tests",
        .root_module = decision_index_module,
    });
    const run_decision_index_tests = b.addRunArtifact(decision_index_tests);

    const decision_index_step = b.step(
        "phase15-architecture-council-decision-index",
        "Run the focused Phase 15 Architecture Council decision-index test",
    );
    decision_index_step.dependOn(&run_decision_index_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 Architecture Council decision-index test");
    test_step.dependOn(&run_decision_index_tests.step);

    b.default_step.dependOn(&run_decision_index_tests.step);
}
