const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_fixture_manifest_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase1-fixture-manifest-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase1_fixture_manifest_contract = b.step(
        "phase1-fixture-manifest-contract",
        "Run the Phase 1 helper manifest fixture contract.",
    );
    phase1_fixture_manifest_contract.dependOn(&run_tests.step);

    const default_test = b.step("test", "Run the Phase 1 helper manifest fixture contract.");
    default_test.dependOn(&run_tests.step);
}
