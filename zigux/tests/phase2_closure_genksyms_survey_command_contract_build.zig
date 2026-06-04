const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_genksyms_survey_command_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-closure-genksyms-survey-command-contract-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase2-closure-genksyms-survey-command-contract",
        "Run the Phase 2 closure genksyms survey command contract.",
    );
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Phase 2 closure genksyms survey command contract.");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(default_test_step);
}
