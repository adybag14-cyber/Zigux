const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane01_bootstrap_phase1_host_helpers_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane01-bootstrap-phase1-host-helpers-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "lane01-bootstrap-phase1-host-helpers-contract",
        "Run the Lane 01 Phase 1 host-helper roadmap contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 1 host-helper roadmap contract");
    test_step.dependOn(&run_tests.step);
}
