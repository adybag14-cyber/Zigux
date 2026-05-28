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
        .step_name = "phase15-freeze-map-shared-surface-inventory",
        .description = "Run the focused Phase 15 freeze-map shared-surface inventory test",
        .root_source_file = "phase15_freeze_map_shared_surface_inventory.zig",
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
