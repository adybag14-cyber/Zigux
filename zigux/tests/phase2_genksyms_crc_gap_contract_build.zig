const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_crc_gap_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-genksyms-crc-gap-contract-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const test_step = b.step(
        "phase2-genksyms-crc-gap-contract",
        "Run the Phase 2 genksyms CRC gap contract",
    );
    test_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the Phase 2 genksyms CRC gap contract");
    default_step.dependOn(&run_tests.step);
}
