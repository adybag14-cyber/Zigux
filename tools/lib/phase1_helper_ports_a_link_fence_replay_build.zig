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

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_a_link_fence_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("bitmap", bitmap_module);
    tests.root_module.addImport("find_bit", find_bit_module);
    tests.root_module.addImport("string", b.createModule(.{
        .root_source_file = b.path("string.zig"),
        .target = target,
        .optimize = optimize,
    }));
    tests.root_module.addImport("rbtree", b.createModule(.{
        .root_source_file = b.path("rbtree.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const run_tests = b.addRunArtifact(tests);

    const named = b.step("phase1-helper-ports-a-link-fence-replay", "Run the Lane 06 link-fence helper replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 06 link-fence helper replay");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
