const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("string.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "cmdline", .module = cmdline_module },
        },
    });
    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("bitmap.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "find_bit", .module = find_bit_module },
        },
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_ridge_walk_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "bitmap", .module = bitmap_module },
            .{ .name = "find_bit", .module = find_bit_module },
            .{ .name = "string", .module = string_module },
            .{ .name = "rbtree", .module = rbtree_module },
        },
    });

    const tests = b.addTest(.{ .root_module = replay_module });
    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step("phase1-helper-ports-a-ridge-walk-replay", "Run the Lane 06 ridge walk helper replay");
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 06 ridge walk helper replay");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
