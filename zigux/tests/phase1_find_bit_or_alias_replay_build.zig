const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_or_alias_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("find_bit", find_bit_module);

    const tests = b.addTest(.{
        .name = "phase1-find-bit-or-alias-replay",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step("phase1-find-bit-or-alias-replay", "Run the lane06 find_bit OR-alias replay");
    step.dependOn(&run_tests.step);
}
