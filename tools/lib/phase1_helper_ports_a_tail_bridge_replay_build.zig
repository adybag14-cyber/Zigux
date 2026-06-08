const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap = b.createModule(.{ .root_source_file = b.path("bitmap.zig") });
    const find_bit = b.createModule(.{ .root_source_file = b.path("find_bit.zig") });
    const string = b.createModule(.{ .root_source_file = b.path("string.zig") });
    const rbtree = b.createModule(.{ .root_source_file = b.path("rbtree.zig") });
    const cmdline = b.createModule(.{ .root_source_file = b.path("cmdline.zig") });

    bitmap.addImport("find_bit", find_bit);
    string.addImport("cmdline", cmdline);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_a_tail_bridge_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("bitmap", bitmap);
    tests.root_module.addImport("find_bit", find_bit);
    tests.root_module.addImport("string", string);
    tests.root_module.addImport("rbtree", rbtree);

    const run = b.addRunArtifact(tests);

    const step = b.step("phase1-helper-ports-a-tail-bridge-replay", "Run the Lane 06 tail bridge replay");
    step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 06 tail bridge replay");
    test_step.dependOn(&run.step);

    b.default_step.dependOn(&run.step);
}
