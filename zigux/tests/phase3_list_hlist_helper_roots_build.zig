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

    const list_view_tests = b.addTest(.{
        .name = "phase3-list-view-helper-root",
        .root_module = list_view,
    });
    const run_list_view_tests = b.addRunArtifact(list_view_tests);

    const hlist_view_tests = b.addTest(.{
        .name = "phase3-hlist-view-helper-root",
        .root_module = hlist_view,
    });
    const run_hlist_view_tests = b.addRunArtifact(hlist_view_tests);

    const test_step = b.step(
        "phase3-list-hlist-helper-roots-test",
        "Run the Phase 3 list_view and hlist_view helper roots together",
    );
    test_step.dependOn(&run_list_view_tests.step);
    test_step.dependOn(&run_hlist_view_tests.step);
}
