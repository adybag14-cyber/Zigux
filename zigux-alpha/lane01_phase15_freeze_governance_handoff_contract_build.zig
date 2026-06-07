const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_phase15_freeze_governance_handoff_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const named_step = b.step(
        "lane01-phase15-freeze-governance-handoff-contract",
        "Run the Lane 01 Phase 15 freeze-governance handoff contract",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
