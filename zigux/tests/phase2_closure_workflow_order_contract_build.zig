const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_workflow_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-closure-workflow-order-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase2-closure-workflow-order-contract",
        "Run the Phase 2 closure workflow order contract.",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 closure workflow order contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(route_step);
}
