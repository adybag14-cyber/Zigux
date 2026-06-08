const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);

    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_module = b.createModule(.{
        .root_source_file = b.path("string.zig"),
        .target = target,
        .optimize = optimize,
    });
    string_module.addImport("cmdline", cmdline_module);

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_tail_echo_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap", bitmap_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("string", string_module);
    root_module.addImport("rbtree", rbtree_module);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-a-tail-echo-replay-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase1-helper-ports-a-tail-echo-replay",
        "Run the Lane 06 Phase 1 helper ports A tail echo replay",
    );
    test_step.dependOn(&run_tests.step);

    const alias_step = b.step("test", "Run the Lane 06 tail echo replay");
    alias_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
