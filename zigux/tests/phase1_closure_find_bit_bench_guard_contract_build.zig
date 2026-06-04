const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_find_bit_bench_guard_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const contract_step = b.step("phase1-closure-find-bit-bench-guard-contract", "Run the Phase 1 find_bit bench guard closure contract");
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 1 find_bit bench guard closure contract");
    test_step.dependOn(&run_unit_tests.step);
}
