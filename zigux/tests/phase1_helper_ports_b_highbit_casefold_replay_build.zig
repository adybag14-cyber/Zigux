const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_b_highbit_casefold_replay.zig"),
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
        .name = "phase1-helper-ports-b-highbit-casefold-replay-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step("phase1-helper-ports-b-highbit-casefold-replay", "Run Lane 08 high-bit/casefold replay");
    step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 08 high-bit/casefold replay");
    test_step.dependOn(&run_tests.step);
}
