const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_paths = [_][]const u8{
        "phase15_freeze_map_governance.zig",
        "phase15_parity_scorecard.zig",
        "phase15_architecture_council_review_process.zig",
        "phase15_indefinite_c_policy.zig",
        "phase15_handoff_next_steps.zig",
        "phase15_indefinite_c_blocker_evidence.zig",
        "phase15_indefinite_c_lane_owner_alignment.zig",
        "phase15_governance_lane_sequencing.zig",
        "phase15_readiness_gate.zig",
    };

    const test_step = b.step("test", "Run Phase 15 governance tests");

    for (test_paths) |test_path| {
        const unit_tests = b.addTest(.{
            .root_module = b.createModule(.{
                .root_source_file = b.path(test_path),
                .target = target,
                .optimize = optimize,
            }),
        });
        const run_unit_tests = b.addRunArtifact(unit_tests);
        test_step.dependOn(&run_unit_tests.step);
    }
}
