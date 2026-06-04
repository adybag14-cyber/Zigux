const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_hweight_bench_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-hweight-bench-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const named = b.step(
        "phase1-hweight-bench-replay",
        "Run the Phase 1 hweight bench replay",
    );
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 hweight bench replay tests");
    test_step.dependOn(&run_tests.step);
}
