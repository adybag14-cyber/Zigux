const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_bench_live_step_patch_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{ .root_module = root_module });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane17-phase1-bench-live-step-patch-contract",
        "Run the Lane 17 Phase 1 bench live workflow patch contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 17 bench live workflow patch contract tests");
    test_step.dependOn(&run_unit_tests.step);
}
