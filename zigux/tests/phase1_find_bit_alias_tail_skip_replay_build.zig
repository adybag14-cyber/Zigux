const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_alias_tail_skip_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("find_bit", find_bit_module);

    const tests = b.addTest(.{
        .name = "phase1-find-bit-alias-tail-skip-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-find-bit-alias-tail-skip-replay",
        "Run the Phase 1 find_bit alias and tail-skip replay from zigux/tests",
    );
    step.dependOn(&run.step);
}
