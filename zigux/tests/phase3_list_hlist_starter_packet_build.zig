const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_list_hlist = b.createModule(.{
        .root_source_file = b.path("../uapi/list_hlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    const binding_list_hlist = b.createModule(.{
        .root_source_file = b.path("../bindings/list_hlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    binding_list_hlist.addImport("uapi_list_hlist", uapi_list_hlist);

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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("binding_list_hlist", binding_list_hlist);
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    const run_artifact = b.addRunArtifact(tests);

    const starter_step = b.step(
        "phase3-list-hlist-starter-packet-test",
        "Run the Phase 3 list/hlist starter packet from zigux/tests",
    );
    starter_step.dependOn(&run_artifact.step);
}
