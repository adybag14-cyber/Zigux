const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const replay_path = b.option([]const u8, "replay-path", "Override replay root source") orelse
        "phase1_helper_ports_b_boundary_replay.zig";
    const argv_split_path = b.option([]const u8, "argv-split-path", "Override argv_split helper source") orelse
        "argv_split.zig";
    const cmdline_path = b.option([]const u8, "cmdline-path", "Override cmdline helper source") orelse
        "cmdline.zig";
    const ctype_path = b.option([]const u8, "ctype-path", "Override ctype helper source") orelse
        "ctype.zig";
    const hweight_path = b.option([]const u8, "hweight-path", "Override hweight helper source") orelse
        "hweight.zig";

    const root_module = b.createModule(.{
        .root_source_file = b.path(replay_path),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path(argv_split_path),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path(cmdline_path),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path(ctype_path),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path(hweight_path),
        .target = target,
        .optimize = optimize,
    });

    root_module.addImport("argv_split", argv_split_module);
    root_module.addImport("cmdline", cmdline_module);
    root_module.addImport("ctype", ctype_module);
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-b-boundary-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const route = b.step("phase1-helper-ports-b-boundary-replay", "Run the Lane 08 helper ports B boundary replay");
    route.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 08 helper ports B boundary replay");
    test_step.dependOn(&run.step);

    b.default_step.dependOn(&run.step);
}
