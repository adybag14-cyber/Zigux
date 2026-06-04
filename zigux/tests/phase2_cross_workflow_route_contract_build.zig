const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_workflow_route_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run = b.addRunArtifact(tests);
    const route = b.step(
        "phase2-cross-workflow-route-contract",
        "Run the Phase 2 cross workflow-route handoff contract",
    );
    route.dependOn(&run.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run.step);
}
