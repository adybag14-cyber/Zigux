const std = @import("std");

fn addSaturationReplay(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_saturation_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
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

    root_module.addImport("argv_split", argv_split_module);
    root_module.addImport("cmdline", cmdline_module);
    root_module.addImport("ctype", ctype_module);
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-b-saturation-replay",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay = addSaturationReplay(b, target, optimize);

    const replay_step = b.step(
        "phase1-helper-ports-b-saturation-replay",
        "Run the Phase 1 helper ports B saturation and remainder replay",
    );
    replay_step.dependOn(&replay.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports B saturation replay");
    test_step.dependOn(&replay.step);
}
