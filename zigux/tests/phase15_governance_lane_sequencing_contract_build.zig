const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_governance_lane_sequencing_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-governance-lane-sequencing-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "phase15-governance-lane-sequencing-contract",
        "Run the focused Phase 15 governance lane sequencing contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 governance lane sequencing contract");
    test_step.dependOn(&run_unit_tests.step);
}
