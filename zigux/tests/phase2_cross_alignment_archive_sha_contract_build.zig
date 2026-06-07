const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_alignment_archive_sha_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "phase2-cross-alignment-archive-sha-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase2-cross-alignment-archive-sha-contract",
        "Run the Phase 2 cross alignment archive SHA contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross alignment archive SHA contract tests");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(test_step);
}
