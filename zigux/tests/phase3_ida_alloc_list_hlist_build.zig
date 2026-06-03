const std = @import("std");

fn addIdaAllocListHlistTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ida_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_root.addImport("ida_alloc_view", ida_alloc_view);
    ida_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const list_root = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    list_root.addImport("list_view", list_view);
    list_root.addImport("hlist_view", hlist_view);

    const ida_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = ida_root,
    });
    const list_tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = list_root,
    });

    const step = b.step(
        "phase3-ida-alloc-list-hlist-test",
        "Run the Phase 3 IDA allocation and list/hlist starter packets together",
    );
    const ida_run = b.addRunArtifact(ida_tests);
    const list_run = b.addRunArtifact(list_tests);
    step.dependOn(&ida_run.step);
    step.dependOn(&list_run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = addIdaAllocListHlistTest(b, target, optimize);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation plus list/hlist harness");
    test_step.dependOn(tests);
}
