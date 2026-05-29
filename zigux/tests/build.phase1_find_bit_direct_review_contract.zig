const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_find_bit_direct_review_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));
    const test_step = b.step("phase1-find-bit-direct-review-contract", "Run the Phase 1 find_bit direct-review closure contract");
    test_step.dependOn(&run_unit_tests.step);
}
