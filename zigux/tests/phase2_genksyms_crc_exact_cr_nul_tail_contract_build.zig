const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_crc_exact_cr_nul_tail_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-genksyms-crc-exact-cr-nul-tail-contract-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const focused_step = b.step(
        "phase2-genksyms-crc-exact-cr-nul-tail-contract",
        "Run the focused Phase 2 genksyms CRC exact-CR/NUL-tail contract",
    );
    focused_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 2 genksyms CRC exact-CR/NUL-tail contract");
    test_step.dependOn(&run_tests.step);
}
