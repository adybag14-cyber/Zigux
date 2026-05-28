const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "find_bit", .module = find_bit_module },
        },
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_a_subset_clump_prefix_cached_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "bitmap", .module = bitmap_module },
                .{ .name = "find_bit", .module = find_bit_module },
                .{ .name = "string", .module = string_module },
                .{ .name = "rbtree", .module = rbtree_module },
            },
        }),
    });

    const run_tests = b.addRunArtifact(unit_tests);
    const test_step = b.step(
        "phase1-helper-ports-a-subset-clump-prefix-cached-replay",
        "Run the Lane 06 subset/clump/prefix/cached replay.",
    );
    test_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the replay tests.");
    default_step.dependOn(&run_tests.step);
}
