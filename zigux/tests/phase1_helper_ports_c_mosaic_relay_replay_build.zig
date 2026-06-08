const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_mod = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_mosaic_relay_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_mod.addImport("slab", slab_mod);
    replay_mod.addImport("str_error_r", str_error_r_mod);
    replay_mod.addImport("vsprintf", vsprintf_mod);
    replay_mod.addImport("zalloc", zalloc_mod);

    const replay_tests = b.addTest(.{
        .root_module = replay_mod,
    });

    const run_replay = b.addRunArtifact(replay_tests);

    const replay_step = b.step("phase1-helper-ports-c-mosaic-relay-replay", "Run the Lane 10 helper ports C mosaic relay replay");
    replay_step.dependOn(&run_replay.step);

    const test_step = b.step("test", "Run the Lane 10 helper ports C mosaic relay replay tests");
    test_step.dependOn(&run_replay.step);

    b.default_step.dependOn(test_step);
}
