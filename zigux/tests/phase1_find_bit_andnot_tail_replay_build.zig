const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_andnot_tail_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("find_bit", find_bit_module);

    const tests = b.addTest(.{
        .name = "phase1-find-bit-andnot-tail-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-find-bit-andnot-tail-replay",
        "Run the standalone Phase 1 find_bit andnot tail replay",
    );
    step.dependOn(&run_tests.step);
}
