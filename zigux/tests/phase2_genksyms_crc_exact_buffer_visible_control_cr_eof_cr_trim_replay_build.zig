const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const genksyms_crc_module = b.createModule(.{
        .root_source_file = b.path("../../scripts/zigux/genksyms_crc.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_genksyms_crc_exact_buffer_visible_control_cr_eof_cr_trim_replay_validation.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("genksyms_crc", genksyms_crc_module);

    const replay_tests = b.addTest(.{
        .name = "phase2-genksyms-crc-exact-buffer-visible-control-cr-eof-cr-trim-replay-tests",
        .root_module = root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);

    const test_step = b.step("test", "Run focused Phase 2 genksyms CRC exact-buffer visible-control CR EOF CR-trim replay tests");
    test_step.dependOn(&run_replay_tests.step);
}
