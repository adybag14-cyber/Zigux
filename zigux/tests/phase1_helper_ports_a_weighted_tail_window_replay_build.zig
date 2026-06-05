const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });

    const bitmap = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap.addImport("find_bit", find_bit);

    const cmdline = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });

    const string = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    string.addImport("cmdline", cmdline);

    const rbtree = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_weighted_tail_window_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap", bitmap);
    root_module.addImport("find_bit", find_bit);
    root_module.addImport("string", string);
    root_module.addImport("rbtree", rbtree);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-a-weighted-tail-window-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const route = b.step("phase1-helper-ports-a-weighted-tail-window-replay", "Run the Phase 1 helper ports A weighted tail-window replay");
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports A weighted tail-window replay");
    test_step.dependOn(&run_tests.step);
}
