const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase15_freeze_map_governance_module = b.createModule(.{
        .root_source_file = b.path("phase15_freeze_map_governance.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_parity_scorecard_module = b.createModule(.{
        .root_source_file = b.path("phase15_parity_scorecard.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_freeze_map_governance_tests = b.addTest(.{
        .name = "phase15-freeze-map-governance-tests",
        .root_module = phase15_freeze_map_governance_module,
    });
    const run_phase15_freeze_map_governance_tests = b.addRunArtifact(phase15_freeze_map_governance_tests);

    const phase15_parity_scorecard_tests = b.addTest(.{
        .name = "phase15-parity-scorecard-tests",
        .root_module = phase15_parity_scorecard_module,
    });
    const run_phase15_parity_scorecard_tests = b.addRunArtifact(phase15_parity_scorecard_tests);

    const phase15_architecture_council_review_process_module = b.createModule(.{
        .root_source_file = b.path("phase15_architecture_council_review_process.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_architecture_council_review_process_tests = b.addTest(.{
        .name = "phase15-architecture-council-review-process-tests",
        .root_module = phase15_architecture_council_review_process_module,
    });
    const run_phase15_architecture_council_review_process_tests = b.addRunArtifact(phase15_architecture_council_review_process_tests);

    const phase15_handoff_next_steps_module = b.createModule(.{
        .root_source_file = b.path("phase15_handoff_next_steps.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_handoff_next_steps_tests = b.addTest(.{
        .name = "phase15-handoff-next-steps-tests",
        .root_module = phase15_handoff_next_steps_module,
    });
    const run_phase15_handoff_next_steps_tests = b.addRunArtifact(phase15_handoff_next_steps_tests);

    const phase15_indefinite_c_policy_module = b.createModule(.{
        .root_source_file = b.path("phase15_indefinite_c_policy.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_indefinite_c_policy_tests = b.addTest(.{
        .name = "phase15-indefinite-c-policy-tests",
        .root_module = phase15_indefinite_c_policy_module,
    });
    const run_phase15_indefinite_c_policy_tests = b.addRunArtifact(phase15_indefinite_c_policy_tests);

    const phase15_indefinite_c_blocker_evidence_module = b.createModule(.{
        .root_source_file = b.path("phase15_indefinite_c_blocker_evidence.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_indefinite_c_blocker_evidence_tests = b.addTest(.{
        .name = "phase15-indefinite-c-blocker-evidence-tests",
        .root_module = phase15_indefinite_c_blocker_evidence_module,
    });
    const run_phase15_indefinite_c_blocker_evidence_tests = b.addRunArtifact(phase15_indefinite_c_blocker_evidence_tests);

    const phase15_indefinite_c_lane_owner_alignment_module = b.createModule(.{
        .root_source_file = b.path("phase15_indefinite_c_lane_owner_alignment.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_indefinite_c_lane_owner_alignment_tests = b.addTest(.{
        .name = "phase15-indefinite-c-lane-owner-alignment-tests",
        .root_module = phase15_indefinite_c_lane_owner_alignment_module,
    });
    const run_phase15_indefinite_c_lane_owner_alignment_tests = b.addRunArtifact(phase15_indefinite_c_lane_owner_alignment_tests);

    const phase15_readiness_gate_module = b.createModule(.{
        .root_source_file = b.path("phase15_readiness_gate.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_readiness_gate_tests = b.addTest(.{
        .name = "phase15-readiness-gate-tests",
        .root_module = phase15_readiness_gate_module,
    });
    const run_phase15_readiness_gate_tests = b.addRunArtifact(phase15_readiness_gate_tests);

    const phase15_governance_lane_sequencing_module = b.createModule(.{
        .root_source_file = b.path("phase15_governance_lane_sequencing.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_governance_lane_sequencing_tests = b.addTest(.{
        .name = "phase15-governance-lane-sequencing-tests",
        .root_module = phase15_governance_lane_sequencing_module,
    });
    const run_phase15_governance_lane_sequencing_tests = b.addRunArtifact(phase15_governance_lane_sequencing_tests);

    const test_step = b.step("test", "Run Phase 15 governance tests");
    test_step.dependOn(&run_phase15_freeze_map_governance_tests.step);
    test_step.dependOn(&run_phase15_parity_scorecard_tests.step);
    test_step.dependOn(&run_phase15_architecture_council_review_process_tests.step);
    test_step.dependOn(&run_phase15_handoff_next_steps_tests.step);
    test_step.dependOn(&run_phase15_indefinite_c_policy_tests.step);
    test_step.dependOn(&run_phase15_indefinite_c_blocker_evidence_tests.step);
    test_step.dependOn(&run_phase15_indefinite_c_lane_owner_alignment_tests.step);
    test_step.dependOn(&run_phase15_readiness_gate_tests.step);
    test_step.dependOn(&run_phase15_governance_lane_sequencing_tests.step);
}
