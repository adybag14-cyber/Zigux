const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase2-cross-workflow-make-route-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_workflow_make_route_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-cross-workflow-make-route-contract",
        "Run the Phase 2 cross workflow make-route contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross workflow make-route contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
