const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_current_reminder_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-closure-current-reminder-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-closure-current-reminder-contract",
        "Validate the Phase 1 closure current reminder packet from zigux/tests",
    );
    step.dependOn(&run_tests.step);
}
