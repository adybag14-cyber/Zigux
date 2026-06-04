const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_make_policy_partition_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run = b.addRunArtifact(tests);
    const route = b.step(
        "phase2-cross-make-policy-partition-contract",
        "Run the Phase 2 cross Makefile/policy/fixture partition contract",
    );
    route.dependOn(&run.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run.step);
}
