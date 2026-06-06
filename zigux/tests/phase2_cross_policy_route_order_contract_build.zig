const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_policy_route_order_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-cross-policy-route-order-contract-tests",
        .root_module = module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase2-cross-policy-route-order-contract",
        "Run the Phase 2 cross policy route-order contract.",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross policy route-order contract tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
