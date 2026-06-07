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

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_owner_rotation_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("slab", slab_module);
    replay_module.addImport("str_error_r", str_error_r_module);
    replay_module.addImport("vsprintf", vsprintf_module);
    replay_module.addImport("zalloc", zalloc_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-c-owner-rotation-replay-tests",
        .root_module = replay_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-helper-ports-c-owner-rotation-replay",
        "Run the focused Phase 1 helper ports C owner rotation replay.",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 helper ports C owner rotation replay tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
