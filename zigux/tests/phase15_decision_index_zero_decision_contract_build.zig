const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase15_decision_index_zero_decision_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step(
        "phase15-decision-index-zero-decision-contract",
        "Run the Phase 15 Architecture Council decision-index zero-decision contract",
    );
    step.dependOn(&run_tests.step);
}
