const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const string_helpers = b.createModule(.{
        .root_source_file = b.path("../../lib/string_helpers.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline = b.createModule(.{
        .root_source_file = b.path("../../lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split = b.createModule(.{
        .root_source_file = b.path("../../lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree = b.createModule(.{
        .root_source_file = b.path("../../lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase7_leaf_libraries_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("string_helpers", string_helpers);
    root_module.addImport("cmdline", cmdline);
    root_module.addImport("argv_split", argv_split);
    root_module.addImport("rbtree", rbtree);

    const tests = b.addTest(.{
        .name = "phase7-leaf-libraries-starter-packet",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase7-leaf-libraries-starter-packet",
        "Run the shared Phase 7 leaf-libraries starter packet",
    );
    step.dependOn(&run.step);
}
