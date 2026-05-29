const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_freeze_map_governance.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-freeze-map-governance-tests",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const governance_step = b.step(
        "phase15-freeze-map-governance",
        "Run the focused Phase 15 freeze-map governance test",
    );
    governance_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 freeze-map governance test");
    test_step.dependOn(&run_unit_tests.step);
}
