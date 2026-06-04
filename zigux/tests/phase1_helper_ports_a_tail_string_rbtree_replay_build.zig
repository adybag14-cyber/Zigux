const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_mod = b.addModule("find_bit", .{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_mod = b.addModule("bitmap", .{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_mod.addImport("find_bit", find_bit_mod);

    const cmdline_mod = b.addModule("cmdline", .{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_mod = b.addModule("string", .{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_mod.addImport("cmdline", cmdline_mod);

    const rbtree_mod = b.addModule("rbtree", .{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_a_tail_string_rbtree_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("bitmap", bitmap_mod);
    tests.root_module.addImport("find_bit", find_bit_mod);
    tests.root_module.addImport("string", string_mod);
    tests.root_module.addImport("rbtree", rbtree_mod);

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step("phase1-helper-ports-a-tail-string-rbtree-replay", "Run the Phase 1 helper ports A tail/string/rbtree replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports A tail/string/rbtree replay");
    test_step.dependOn(&run_tests.step);
}
