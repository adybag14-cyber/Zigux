const std = @import("std");

const Phase15Target = struct {
    step_name: []const u8,
    description: []const u8,
    root_source_file: []const u8,
};

const phase15_targets = [_]Phase15Target{
    .{
        .step_name = "phase15-freeze-map-governance",
        .description = "Run the focused Phase 15 freeze-map governance test",
        .root_source_file = "phase15_freeze_map_governance.zig",
    },
    .{
        .step_name = "phase15-freeze-map-status-change-boundary",
        .description = "Run the focused Phase 15 freeze-map status-change boundary contract",
        .root_source_file = "phase15_freeze_map_status_change_boundary.zig",
    },
    .{
        .step_name = "phase15-architecture-council-review-process",
        .description = "Run the focused Phase 15 Architecture Council review-process test",
        .root_source_file = "phase15_architecture_council_review_process.zig",
    },
    .{
        .step_name = "phase15-architecture-council-decision-index",
        .description = "Run the focused Phase 15 Architecture Council decision-index test",
        .root_source_file = "phase15_architecture_council_decision_index.zig",
    },
    .{
        .step_name = "phase15-governance-lane-sequencing",
        .description = "Run the focused Phase 15 governance-lane sequencing test",
        .root_source_file = "phase15_governance_lane_sequencing.zig",
    },
    .{
        .step_name = "phase15-parity-scorecard",
        .description = "Run the focused Phase 15 parity-scorecard test",
        .root_source_file = "phase15_parity_scorecard.zig",
    },
    .{
        .step_name = "phase15-indefinite-c-policy",
        .description = "Run the focused Phase 15 indefinite-C policy test",
        .root_source_file = "phase15_indefinite_c_policy.zig",
    },
    .{
        .step_name = "phase15-handoff-next-steps",
        .description = "Run the focused Phase 15 handoff next-steps test",
        .root_source_file = "phase15_handoff_next_steps.zig",
    },
    .{
        .step_name = "phase15-indefinite-c-lane-owner-alignment",
        .description = "Run the focused Phase 15 indefinite-C lane-owner alignment test",
        .root_source_file = "phase15_indefinite_c_lane_owner_alignment.zig",
    },
    .{
        .step_name = "phase15-readiness-gate",
        .description = "Run the focused Phase 15 readiness-gate test",
        .root_source_file = "phase15_readiness_gate.zig",
    },
    .{
        .step_name = "phase15-route-recovery",
        .description = "Run the focused Phase 15 route-recovery contract",
        .root_source_file = "phase15_route_recovery.zig",
    },
    .{
        .step_name = "phase15-decision-index-no-approval-contract",
        .description = "Run the Phase 15 zero-approval decision-index contract",
        .root_source_file = "phase15_decision_index_no_approval_contract.zig",
    },
    .{
        .step_name = "phase15-deep-core-blocker-contract",
        .description = "Run the Phase 15 deep-core blocker contract",
        .root_source_file = "phase15_deep_core_blocker_contract.zig",
    },
    .{
        .step_name = "phase15-docs-readme-alignment-contract",
        .description = "Run the Phase 15 docs-root alignment contract",
        .root_source_file = "phase15_docs_readme_alignment_contract.zig",
    },
    .{
        .step_name = "phase15-docs-root-approval-boundary-contract",
        .description = "Run the Phase 15 docs-root approval boundary contract",
        .root_source_file = "phase15_docs_root_approval_boundary_contract.zig",
    },
    .{
        .step_name = "phase15-docs-root-route-gap-contract",
        .description = "Run the Phase 15 recovered route contract",
        .root_source_file = "phase15_docs_root_route_gap_contract.zig",
    },
    .{
        .step_name = "phase15-governance-lane-sequencing-contract",
        .description = "Run the Phase 15 governance sequencing contract",
        .root_source_file = "phase15_governance_lane_sequencing_contract.zig",
    },
    .{
        .step_name = "phase15-handoff-shared-summary-contract",
        .description = "Run the Phase 15 handoff summary contract",
        .root_source_file = "phase15_handoff_shared_summary_contract.zig",
    },
    .{
        .step_name = "phase15-phase9-freeze-boundary-scope-contract",
        .description = "Run the Phase 15 Phase 9 freeze-boundary contract",
        .root_source_file = "phase15_phase9_freeze_boundary_scope_contract.zig",
    },
    .{
        .step_name = "phase15-readiness-release-evidence-contract",
        .description = "Run the Phase 15 release-evidence contract",
        .root_source_file = "phase15_readiness_release_evidence_contract.zig",
    },
    .{
        .step_name = "phase15-review-checklist-architecture-owner-contract",
        .description = "Run the Phase 15 checklist owner contract",
        .root_source_file = "phase15_review_checklist_arch_council_owner_contract.zig",
    },
    .{
        .step_name = "phase15-scripts-readme-alignment-contract",
        .description = "Run the Phase 15 scripts-root alignment contract",
        .root_source_file = "phase15_scripts_readme_alignment_contract.zig",
    },
    .{
        .step_name = "phase15-shared-reminder-ownership-contract",
        .description = "Run the Phase 15 shared reminder ownership contract",
        .root_source_file = "phase15_shared_reminder_ownership_contract.zig",
    },
    .{
        .step_name = "phase15-validator-governance-contract",
        .description = "Run the Phase 15 validator governance contract",
        .root_source_file = "phase15_validator_governance_contract.zig",
    },
};

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const aggregate = b.step("test", "Run the shared Phase 15 governance test packet");

    inline for (phase15_targets) |entry| {
        const module = b.createModule(.{
            .root_source_file = b.path(entry.root_source_file),
            .target = target,
            .optimize = optimize,
        });

        const unit_tests = b.addTest(.{
            .name = entry.step_name,
            .root_module = module,
        });
        const run_unit_tests = b.addRunArtifact(unit_tests);

        const step = b.step(entry.step_name, entry.description);
        step.dependOn(&run_unit_tests.step);
        aggregate.dependOn(&run_unit_tests.step);
    }
}
