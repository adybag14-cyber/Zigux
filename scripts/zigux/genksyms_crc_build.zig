const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const genksyms_crc_module = b.createModule(.{
        .root_source_file = b.path("genksyms_crc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const genksyms_crc_tests = b.addTest(.{
        .name = "lane19-genksyms-crc-helper-tests",
        .root_module = genksyms_crc_module,
    });

    const run_tests = b.addRunArtifact(genksyms_crc_tests);

    const lane_step = b.step(
        "lane19-genksyms-crc-helper-tests",
        "Run the focused Lane 19 genksyms CRC helper tests.",
    );
    lane_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Lane 19 genksyms CRC helper tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
