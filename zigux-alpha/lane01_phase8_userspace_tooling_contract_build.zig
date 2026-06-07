const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const lane01_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_phase8_userspace_tooling_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_lane01_tests = b.addRunArtifact(lane01_tests);

    const phase8_step = b.step(
        "lane01-phase8-userspace-tooling-contract",
        "Validate Lane 01 Phase 8 userspace-adjacent tooling roadmap packet",
    );
    phase8_step.dependOn(&run_lane01_tests.step);

    const test_step = b.step("test", "Run Lane 01 Phase 8 contract tests");
    test_step.dependOn(&run_lane01_tests.step);

    b.default_step.dependOn(&run_lane01_tests.step);
}
