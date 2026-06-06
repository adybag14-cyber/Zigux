const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_octant_spoke_relay_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view_module);
    root_module.addImport("hlist_view", hlist_view_module);

    const unit_tests = b.addTest(.{
        .name = "phase3-list-hlist-octant-spoke-relay-replay-tests",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const replay_step = b.step("phase3-list-hlist-octant-spoke-relay-replay", "Run the Lane 28 list/hlist octant spoke relay replay");
    replay_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 28 list/hlist octant spoke relay replay");
    test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(test_step);
}
