const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_genksyms_crc_nul_first_exact_buffer_spillover_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step("phase2-genksyms-crc-nul-first-exact-buffer-spillover-contract", "Run the Phase 2 genksyms CRC NUL-first exact-buffer spillover contract");
    step.dependOn(&run_tests.step);
}
