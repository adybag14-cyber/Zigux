const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_helper_smoke.zig"),
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
        .name = "phase1-find-bit-helper-smoke",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const helper_step = b.step(
        "phase1-find-bit-helper-smoke",
        "Run the standalone Phase 1 find_bit helper smoke shard",
    );
    helper_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the standalone Phase 1 find_bit helper smoke shard",
    );
    test_step.dependOn(&run.step);
}
