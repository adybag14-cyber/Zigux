const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_crc_midline_nul_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase2-genksyms-crc-midline-nul-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step("phase2-genksyms-crc-midline-nul-contract", "Run the focused Phase 2 genksyms CRC midline NUL contract.");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the focused Phase 2 genksyms CRC midline NUL contract.");
    test_step.dependOn(contract_step);

    b.default_step.dependOn(test_step);
}
