const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_list_hlist = b.createModule(.{
        .root_source_file = b.path("../uapi/list_hlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_hlist_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/list_hlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    list_hlist_bindings.addImport("uapi_list_hlist", uapi_list_hlist);

    const list_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hlist_view_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_hlist_bindings", list_hlist_bindings);
    root_module.addImport("list_view", list_view_mod);
    root_module.addImport("hlist_view", hlist_view_mod);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-starter-packet",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    const step = b.step(
        "phase3-list-hlist-starter-packet-test",
        "Run the bounded Phase 3 list/hlist starter packet",
    );
    step.dependOn(&run_tests.step);
}
