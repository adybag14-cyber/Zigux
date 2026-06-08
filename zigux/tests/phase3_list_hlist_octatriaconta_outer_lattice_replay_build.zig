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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_list_hlist_octatriaconta_outer_lattice_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_view", list_view);
    root_module.addImport("hlist_view", hlist_view);

    const tests = b.addTest(.{
        .name = "phase3-list-hlist-octatriaconta-outer-lattice-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-list-hlist-octatriaconta-outer-lattice-replay",
        "Run the Lane 28 octatriaconta outer-lattice list/hlist replay",
    );
    step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 28 octatriaconta outer-lattice replay tests");
    test_step.dependOn(&run.step);

    b.default_step.dependOn(&run.step);
}
