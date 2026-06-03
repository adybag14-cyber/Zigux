const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_shared_reminder_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-shared-reminder-checker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-shared-reminder-checker-contract",
        "Run the Lane 07 Phase 1 shared-reminder checker contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run this focused Lane 07 contract");
    test_step.dependOn(&run_tests.step);
}
