const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const list_hlist_root = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    list_hlist_root.addImport("list_view", list_view);
    list_hlist_root.addImport("hlist_view", hlist_view);

    const list_hlist_tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = list_hlist_root,
    });
    const run_list_hlist_tests = b.addRunArtifact(list_hlist_tests);

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ida_bitmap_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const ida_bitmap_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet",
        .root_module = ida_bitmap_root,
    });
    const run_ida_bitmap_tests = b.addRunArtifact(ida_bitmap_tests);

    const shard = b.step(
        "phase3-list-hlist-ida-bitmap-test",
        "Run the Phase 3 list/hlist starter packet beside the IDA bitmap starter packet",
    );
    shard.dependOn(&run_list_hlist_tests.step);
    shard.dependOn(&run_ida_bitmap_tests.step);

    const test_step = b.step("test", "Run the Phase 3 list/hlist plus IDA bitmap shard");
    test_step.dependOn(shard);
}
