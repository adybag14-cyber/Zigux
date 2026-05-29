const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_genksyms_crc_line_nul_consumption_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step("phase2-genksyms-crc-line-nul-consumption-contract", "Run the Phase 2 genksyms CRC line-NUL consumption contract");
    step.dependOn(&run_tests.step);
}
