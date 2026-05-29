const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_bootstrap_phase5_scheduling_boundary_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane01-bootstrap-phase5-scheduling-boundary-contract",
        "Validate the Lane 01 roadmap Phase 5 scheduling-boundary contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 roadmap Phase 5 scheduling-boundary contract");
    test_step.dependOn(contract_step);
}
