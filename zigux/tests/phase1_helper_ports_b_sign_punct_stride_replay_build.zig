const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_sign_punct_stride_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("argv_split", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("cmdline", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("ctype", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("hweight", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase1-helper-ports-b-sign-punct-stride-replay",
        "Run the Phase 1 helper ports B sign/punctuation stride replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports B sign/punctuation stride replay");
    test_step.dependOn(&run_tests.step);
}
