const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_checker_selftest_count_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const named = b.step(
        "phase2-cross-checker-selftest-count-contract",
        "Run the Phase 2 cross checker self-test count contract",
    );
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run all tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
