const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_fixture_test.zig"),
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
        .name = "phase1-find-bit-fixture",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-find-bit-fixture",
        "Run the focused Phase 1 find_bit fixture replay",
    );
    step.dependOn(&run.step);
}
