const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase15_freeze_map_governance_module = b.createModule(.{
        .root_source_file = b.path("phase15_freeze_map_governance.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase15_freeze_map_governance_tests = b.addTest(.{
        .name = "phase15-freeze-map-governance-tests",
        .root_module = phase15_freeze_map_governance_module,
    });
    const run_phase15_freeze_map_governance_tests = b.addRunArtifact(phase15_freeze_map_governance_tests);

    const test_step = b.step("test", "Run Phase 15 governance tests");
    test_step.dependOn(&run_phase15_freeze_map_governance_tests.step);
}
