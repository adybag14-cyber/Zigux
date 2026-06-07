const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_freeze_map_status_change_boundary.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-freeze-map-status-change-boundary",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const status_change_boundary = b.step(
        "phase15-freeze-map-status-change-boundary",
        "Run the focused Phase 15 freeze-map status-change boundary contract",
    );
    status_change_boundary.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the focused Phase 15 freeze-map status-change boundary contract");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
