const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane17_phase1_bench_live_step_patch_applier.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "lane17-phase1-bench-live-step-patch-applier",
        "Run the Lane 17 Phase 1 bench live-step patch-applier proof",
    );
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}
