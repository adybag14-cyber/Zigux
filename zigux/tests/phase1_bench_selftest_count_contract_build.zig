const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const checker_path = b.option([]const u8, "checker-path", "Path to scripts/zigux/check-phase1-bench.py") orelse "scripts/zigux/check-phase1-bench.py";

    const config_options = b.addOptions();
    config_options.addOption([]const u8, "checker_path", checker_path);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_bench_selftest_count_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("config", config_options);

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step("phase1-bench-selftest-count-contract", "Run the Phase 1 bench checker self-test count contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bench checker self-test count contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
