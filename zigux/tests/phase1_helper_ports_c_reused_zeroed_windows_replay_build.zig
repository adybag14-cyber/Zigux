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
        .root_source_file = b.path("phase1_helper_ports_c_reused_zeroed_windows_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_mod.addImport("slab", slab_mod);
    replay_mod.addImport("str_error_r", str_error_r_mod);
    replay_mod.addImport("vsprintf", vsprintf_mod);
    replay_mod.addImport("zalloc", zalloc_mod);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-c-reused-zeroed-windows-replay-tests",
        .root_module = replay_mod,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step("phase1-helper-ports-c-reused-zeroed-windows-replay", "Run the Lane 10 reused zeroed windows replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 10 reused zeroed windows replay");
    test_step.dependOn(&run_tests.step);
}
