const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap = b.createModule(.{
        .root_source_file = b.path("bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    const find_bit = b.createModule(.{
        .root_source_file = b.path("find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string = b.createModule(.{
        .root_source_file = b.path("string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree = b.createModule(.{
        .root_source_file = b.path("rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline = b.createModule(.{
        .root_source_file = b.path("cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });

    bitmap.addImport("find_bit", find_bit);
    string.addImport("cmdline", cmdline);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_a_hinge_latch_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "bitmap", .module = bitmap },
                .{ .name = "find_bit", .module = find_bit },
                .{ .name = "string", .module = string },
                .{ .name = "rbtree", .module = rbtree },
            },
        }),
    });

    const run = b.addRunArtifact(tests);

    const named = b.step("phase1-helper-ports-a-hinge-latch-replay", "Run the Lane 06 hinge-latch helper replay");
    named.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 06 hinge-latch helper replay");
    test_step.dependOn(&run.step);

    b.default_step.dependOn(test_step);
}
