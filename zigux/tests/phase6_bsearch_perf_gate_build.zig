const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_perf_gate.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bsearch_module = b.createModule(.{
        .root_source_file = b.path("../../lib/bsearch.zig"),
        .target = target,
        .optimize = optimize,
    });

    root_module.addImport("bsearch", bsearch_module);

    const tests = b.addTest(.{
        .name = "phase6-bsearch-perf-gate",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("test", "Run the Phase 6 bsearch perf-gate test");
    test_step.dependOn(&run_tests.step);
}
