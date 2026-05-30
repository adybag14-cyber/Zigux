const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-helper-manifest-lane-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_manifest_lane_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract = b.step(
        "phase1-helper-manifest-lane-contract",
        "Run the Phase 1 helper manifest lane contract",
    );
    contract.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper manifest lane contract");
    test_step.dependOn(&run_tests.step);
}
