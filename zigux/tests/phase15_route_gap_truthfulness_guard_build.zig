const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .name = "phase15-route-gap-truthfulness-guard",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase15_route_gap_truthfulness_guard.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step("phase15-route-gap-truthfulness-guard", "Run the focused Phase 15 route-gap truthfulness guard");
    test_step.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the focused Phase 15 route-gap truthfulness guard");
    aggregate.dependOn(&run_unit_tests.step);
}
