const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase15_handoff_shared_summary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase15-handoff-shared-summary-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const focused_step = b.step(
        "phase15-handoff-shared-summary-contract",
        "Run the Phase 15 handoff/shared-summary contract",
    );
    focused_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 15 handoff/shared-summary contract");
    test_step.dependOn(&run_tests.step);
}
