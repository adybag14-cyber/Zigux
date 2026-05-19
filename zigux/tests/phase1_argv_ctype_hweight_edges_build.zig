const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_ctype_hweight_edges.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
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
    root_module.addImport("ctype", ctype_module);
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-argv-ctype-hweight-edges",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step(
        "phase1-argv-ctype-hweight-edges",
        "Run the standalone Lane 07 argv/ctype/hweight edge replay",
    );
    replay_step.dependOn(&run_tests.step);
}
