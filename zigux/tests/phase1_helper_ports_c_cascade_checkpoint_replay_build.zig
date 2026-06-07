const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_c_cascade_checkpoint_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "slab", .module = slab },
                .{ .name = "str_error_r", .module = str_error_r },
                .{ .name = "vsprintf", .module = vsprintf },
                .{ .name = "zalloc", .module = zalloc },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const named = b.step("phase1-helper-ports-c-cascade-checkpoint-replay", "Run the Lane 10 cascade checkpoint replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
