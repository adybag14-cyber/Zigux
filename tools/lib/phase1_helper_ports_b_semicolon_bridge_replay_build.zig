const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-b-semicolon-bridge-replay-test",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_b_semicolon_bridge_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-helper-ports-b-semicolon-bridge-replay",
        "Run the Lane 08 helper ports B semicolon-bridge replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 08 helper ports B semicolon-bridge replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
