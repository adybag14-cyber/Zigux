const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_genksyms_dual_survey_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase2-genksyms-dual-survey-contract",
        "Run the Phase 2 genksyms dual-implementation survey documentation contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 2 genksyms dual survey contract tests");
    test_step.dependOn(&run_tests.step);
}
