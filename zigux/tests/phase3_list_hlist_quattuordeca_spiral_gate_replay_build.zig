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
        .root_source_file = b.path("phase3_list_hlist_quattuordeca_spiral_gate_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "list_view", .module = list_view_module },
            .{ .name = "hlist_view", .module = hlist_view_module },
        },
    });

    const tests = b.addTest(.{ .root_module = root_module });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-list-hlist-quattuordeca-spiral-gate-replay",
        "Run the Lane 28 quattuordeca spiral-gate list/hlist replay.",
    );
    step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 28 quattuordeca spiral-gate list/hlist replay tests.");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
