const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench.zig"),
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
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
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
    root_module.addImport("hweight", hweight_module);
    root_module.addImport("list_sort", list_sort_module);
    root_module.addImport("rbtree", rbtree_module);
    root_module.addImport("string", string_module);

    const exe = b.addExecutable(.{
        .name = "phase1-bench",
        .root_module = root_module,
    });
    const run_bench = b.addRunArtifact(exe);

    const bench_step = b.step(
        "bench",
        "Run the focused Phase 1 helper benchmark packet from zigux/tests",
    );
    bench_step.dependOn(&run_bench.step);

    const test_step = b.step(
        "test",
        "Run the focused Phase 1 helper benchmark packet from zigux/tests",
    );
    test_step.dependOn(&run_bench.step);

    b.default_step.dependOn(test_step);
}
