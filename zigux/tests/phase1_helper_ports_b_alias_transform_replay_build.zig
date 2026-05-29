const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_alias_transform_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("argv_split", argv_split_module);
    replay_module.addImport("cmdline", cmdline_module);
    replay_module.addImport("ctype", ctype_module);
    replay_module.addImport("hweight", hweight_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-b-alias-transform-replay-tests",
        .root_module = replay_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);

    const replay_step = b.step(
        "phase1-helper-ports-b-alias-transform-replay",
        "Run the Phase 1 helper ports B alias and transform replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 helper ports B alias and transform replay.");
    test_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(test_step);
}
