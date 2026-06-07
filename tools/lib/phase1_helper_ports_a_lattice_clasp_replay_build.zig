const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_mod = b.addModule("bitmap", .{
        .root_source_file = b.path("bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    const find_bit_mod = b.addModule("find_bit", .{
        .root_source_file = b.path("find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const string_mod = b.addModule("string", .{
        .root_source_file = b.path("string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_mod = b.addModule("rbtree", .{
        .root_source_file = b.path("rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    bitmap_mod.addImport("find_bit", find_bit_mod);
    string_mod.addImport("cmdline", b.addModule("cmdline", .{
        .root_source_file = b.path("cmdline.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_a_lattice_clasp_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("bitmap", bitmap_mod);
    tests.root_module.addImport("find_bit", find_bit_mod);
    tests.root_module.addImport("string", string_mod);
    tests.root_module.addImport("rbtree", rbtree_mod);

    const run_tests = b.addRunArtifact(tests);

    const named = b.step("phase1-helper-ports-a-lattice-clasp-replay", "Run the Lane 06 lattice clasp helper replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 06 lattice clasp helper replay");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}
