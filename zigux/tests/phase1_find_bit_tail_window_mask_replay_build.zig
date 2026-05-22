const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_find_bit_tail_window_mask_replay.zig"),
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
        .name = "phase1-find-bit-tail-window-mask-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step(
        "phase1-find-bit-tail-window-mask-replay",
        "Run the Phase 1 find_bit tail-window mask replay.",
    );
    step.dependOn(&run_tests.step);
}
