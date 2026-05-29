const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hlist_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_bridge_pair_tail_claim_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hlist_view", hlist_view_module);
    root_module.addImport("list_view", list_view_module);

    const tests = b.addTest(.{ .root_module = root_module });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step("phase3-list-hlist-bridge-pair-tail-claim-replay", "Run the Phase 3 list/hlist bridge-pair tail-claim replay");
    step.dependOn(&run_tests.step);
}
