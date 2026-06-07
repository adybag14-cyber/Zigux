const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_mod = b.createModule(.{
        .root_source_file = b.path("find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_mod = b.createModule(.{
        .root_source_file = b.path("bitmap.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "find_bit", .module = find_bit_mod },
        },
    });
    const string_mod = b.createModule(.{
        .root_source_file = b.path("string.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "cmdline", .module = b.createModule(.{
                .root_source_file = b.path("cmdline.zig"),
                .target = target,
                .optimize = optimize,
            }) },
        },
    });
    const rbtree_mod = b.createModule(.{
        .root_source_file = b.path("rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_mod = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_terrace_splice_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "bitmap", .module = bitmap_mod },
            .{ .name = "find_bit", .module = find_bit_mod },
            .{ .name = "string", .module = string_mod },
            .{ .name = "rbtree", .module = rbtree_mod },
        },
    });

    const tests = b.addTest(.{ .root_module = root_mod });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step("phase1-helper-ports-a-terrace-splice-replay", "Run the Lane 06 Phase 1 helper ports A terrace splice replay.");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 06 Phase 1 helper ports A terrace splice replay tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
