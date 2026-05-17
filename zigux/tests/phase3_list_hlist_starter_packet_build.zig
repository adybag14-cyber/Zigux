const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_list_hlist = b.createModule(.{
        .root_source_file = b.path("../uapi/list_hlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_hlist_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/list_hlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    list_hlist_binding.addImport("uapi_list_hlist", uapi_list_hlist);

    const list_view = b.createModule(.{
        .root_source_file = b.path("../helpers/list_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    list_view.addImport("list_hlist_binding", list_hlist_binding);

    const hlist_view = b.createModule(.{
        .root_source_file = b.path("../helpers/hlist_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    hlist_view.addImport("list_hlist_binding", list_hlist_binding);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_hlist_binding", list_hlist_binding);
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-list-hlist-starter-packet-test",
        "Run the Phase 3 list/hlist starter-packet self-check",
    );
    test_step.dependOn(&run_unit_tests.step);
}
