const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_crc_newline_at_buffer_edge_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-crc-newline-at-buffer-edge-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-crc-newline-at-buffer-edge",
        "Run the genksyms CRC newline-at-buffer-edge proof",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the genksyms CRC newline-at-buffer-edge proof");
    test_step.dependOn(&run_tests.step);
}
