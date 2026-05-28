const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_scnprintf_clump_lookup_cachedleftmost_replay.zig"),
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
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    bitmap_module.addImport("find_bit", find_bit_module);
    root_module.addImport("bitmap", bitmap_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("rbtree", rbtree_module);
    root_module.addImport("string", string_module);

    const tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase1-helper-ports-a-scnprintf-clump-lookup-cachedleftmost-replay",
        "Run the focused Lane 06 helper replay packet from zigux/tests",
    );
    test_step.dependOn(&run_tests.step);

    const alias_step = b.step(
        "test",
        "Run the focused Lane 06 helper replay packet from zigux/tests",
    );
    alias_step.dependOn(&run_tests.step);

    b.default_step.dependOn(alias_step);
}
