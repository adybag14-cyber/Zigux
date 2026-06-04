const std = @import("std");

fn addAliasRoundtripReplay(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_alias_roundtrip_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    bitmap_module.addImport("find_bit", find_bit_module);
    string_module.addImport("cmdline", cmdline_module);
    root_module.addImport("bitmap", bitmap_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("rbtree", rbtree_module);
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-a-alias-roundtrip-replay",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const run_tests = addAliasRoundtripReplay(b, target, optimize);

    const replay_step = b.step("phase1-helper-ports-a-alias-roundtrip-replay", "Run the Lane 06 helper ports A alias roundtrip replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 06 helper ports A alias roundtrip replay");
    test_step.dependOn(&run_tests.step);
}
