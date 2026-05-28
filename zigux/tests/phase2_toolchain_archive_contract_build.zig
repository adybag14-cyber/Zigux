const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_toolchain_archive_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase2-toolchain-archive-contract-test",
        "Run the Phase 2 pinned Zig archive bootstrap contract test",
    );
    test_step.dependOn(&run_tests.step);
}
