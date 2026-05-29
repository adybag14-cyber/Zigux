const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const route_contract_tests = b.addTest(.{
        .name = "phase2-cross-makefile-route-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_makefile_route_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_route_contract_tests = b.addRunArtifact(route_contract_tests);
    run_route_contract_tests.setCwd(b.path("."));

    const route_contract_step = b.step(
        "phase2-cross-makefile-route-contract",
        "Run the Phase 2 cross Makefile route contract",
    );
    route_contract_step.dependOn(&run_route_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross Makefile route contract tests");
    test_step.dependOn(&run_route_contract_tests.step);
}
