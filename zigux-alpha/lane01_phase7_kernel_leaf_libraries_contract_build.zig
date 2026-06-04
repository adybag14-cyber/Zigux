const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const lane01_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_phase7_kernel_leaf_libraries_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_lane01_tests = b.addRunArtifact(lane01_tests);

    const phase7_step = b.step(
        "lane01-phase7-kernel-leaf-libraries-contract",
        "Validate Lane 01 Phase 7 in-kernel leaf-library roadmap packet",
    );
    phase7_step.dependOn(&run_lane01_tests.step);

    const test_step = b.step("test", "Run Lane 01 Phase 7 contract tests");
    test_step.dependOn(&run_lane01_tests.step);
}
