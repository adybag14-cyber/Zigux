const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_root = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_rebind_ring_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root.addImport("slab", slab_module);
    replay_root.addImport("str_error_r", str_error_r_module);
    replay_root.addImport("vsprintf", vsprintf_module);
    replay_root.addImport("zalloc", zalloc_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-c-rebind-ring-replay-tests",
        .root_module = replay_root,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    run_replay_tests.setCwd(b.path("../.."));

    const replay_step = b.step(
        "phase1-helper-ports-c-rebind-ring-replay",
        "Run Lane 10 Phase 1 helper ports C rebind-ring replay",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run Lane 10 Phase 1 helper ports C rebind-ring replay");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(&run_replay_tests.step);
}
