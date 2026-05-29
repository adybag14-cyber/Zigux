const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const route_inventory_tests = b.addTest(.{
        .name = "phase2-cross-route-inventory-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_route_inventory_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_route_inventory_tests = b.addRunArtifact(route_inventory_tests);

    const route_inventory_step = b.step(
        "phase2-cross-route-inventory-contract",
        "Run the Phase 2 cross route inventory contract tests.",
    );
    route_inventory_step.dependOn(&run_route_inventory_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross route inventory contract tests.");
    test_step.dependOn(&run_route_inventory_tests.step);

    b.default_step.dependOn(test_step);
}
