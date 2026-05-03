const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    bitmap_module.addImport("find_bit", find_bit_module);

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
    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });

    const bench_root_module = b.createModule(.{
        .root_source_file = b.path("phase1_bench.zig"),
        .target = target,
        .optimize = optimize,
    });
    bench_root_module.addImport("bitmap", bitmap_module);
    bench_root_module.addImport("find_bit", find_bit_module);
    bench_root_module.addImport("hweight", hweight_module);
    bench_root_module.addImport("list_sort", list_sort_module);
    bench_root_module.addImport("rbtree", rbtree_module);
    bench_root_module.addImport("string", string_module);

    const bench = b.addExecutable(.{
        .name = "phase1-bench",
        .root_module = bench_root_module,
    });
    const run_bench = b.addRunArtifact(bench);
    const bench_step = b.step("bench", "Run Phase 1 helper benchmark smoke");
    bench_step.dependOn(&run_bench.step);
}
