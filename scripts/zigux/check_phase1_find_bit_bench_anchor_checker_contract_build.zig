const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const source_path = b.option(
        []const u8,
        "source-path",
        "path to scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    ) orelse "scripts/zigux/check-phase1-find-bit-bench-anchors.py";

    const options = b.addOptions();
    options.addOption([]const u8, "source_path", source_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_find_bit_bench_anchor_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "check-phase1-find-bit-bench-anchor-checker-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-phase1-find-bit-bench-anchor-checker-contract",
        "Run the Lane 07 find-bit bench-anchor checker source contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 07 find-bit bench-anchor checker source contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
