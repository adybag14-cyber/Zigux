const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_cr_suffix_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    module.addImport("argv_split", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    }));
    module.addImport("cmdline", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    }));
    module.addImport("ctype", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    }));
    module.addImport("hweight", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-b-cr-suffix-replay-tests",
        .root_module = module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-helper-ports-b-cr-suffix-replay",
        "Run the Lane 08 carriage-return suffix replay across argv_split, cmdline, ctype, and hweight",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 08 carriage-return suffix replay");
    test_step.dependOn(&run_tests.step);
}
