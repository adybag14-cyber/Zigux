const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    const replay_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_table_boundary_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_root_module.addImport("ctype", ctype_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-ctype-table-boundary-replay-tests",
        .root_module = replay_root_module,
    });
    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-ctype-table-boundary-replay",
        "Run the Phase 1 ctype table-boundary replay",
    );
    replay_step.dependOn(&run_replay_tests.step);
}
