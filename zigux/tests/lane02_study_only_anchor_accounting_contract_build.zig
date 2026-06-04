const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("../../Documentation/zigux/lane02_study_only_anchor_accounting_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane02-study-only-anchor-accounting-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "test",
        "Run the Lane 02 Phase 15 study-only anchor accounting contract",
    );
    test_step.dependOn(&run_tests.step);

    const contract_step = b.step(
        "lane02-study-only-anchor-accounting-contract",
        "Run the Lane 02 Phase 15 study-only anchor accounting contract",
    );
    contract_step.dependOn(&run_tests.step);
}
