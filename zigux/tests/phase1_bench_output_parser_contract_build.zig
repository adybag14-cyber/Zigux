const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-bench-output-parser-contract-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_bench_output_parser_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase1-bench-output-parser-contract",
        "Run the Phase 1 bench output parser contract",
    );
    test_step.dependOn(&run_tests.step);

    const alias_step = b.step("test", "Run the Phase 1 bench output parser contract");
    alias_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
