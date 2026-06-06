const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const strerror_module = b.createModule(.{
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
        .root_source_file = b.path("phase1_helper_ports_c_handoff_chain_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("slab", slab_module);
    replay_module.addImport("str_error_r", strerror_module);
    replay_module.addImport("vsprintf", vsprintf_module);
    replay_module.addImport("zalloc", zalloc_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-c-handoff-chain-replay-tests",
        .root_module = replay_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-helper-ports-c-handoff-chain-replay",
        "Run the Lane 10 helper ports C handoff-chain replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the focused Lane 10 handoff-chain replay.");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}
