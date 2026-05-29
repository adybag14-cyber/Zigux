const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_bitmap_direct_review_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("bitmap", bitmap_module);

    const contract_tests = b.addTest(.{
        .name = "phase1-bitmap-direct-review-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-bitmap-direct-review-contract",
        "Run the Phase 1 bitmap direct-review contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bitmap direct-review contract");
    test_step.dependOn(&run_contract_tests.step);
}
