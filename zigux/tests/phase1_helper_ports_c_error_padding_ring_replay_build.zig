const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.step("test", "Run the Lane 10 error-padding ring replay");
    const replay_step = b.step(
        "phase1-helper-ports-c-error-padding-ring-replay",
        "Run the Lane 10 error-padding ring replay",
    );

    const replay_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_c_error_padding_ring_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    replay_tests.root_module.addImport("slab", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    }));
    replay_tests.root_module.addImport("str_error_r", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    }));
    replay_tests.root_module.addImport("vsprintf", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    }));
    replay_tests.root_module.addImport("zalloc", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const run_replay = b.addRunArtifact(replay_tests);
    replay_step.dependOn(&run_replay.step);
    test_step.dependOn(&run_replay.step);
}
