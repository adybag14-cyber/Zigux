const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_c_anchor_chain_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("slab", slab);
    tests.root_module.addImport("str_error_r", str_error_r);
    tests.root_module.addImport("vsprintf", vsprintf);
    tests.root_module.addImport("zalloc", zalloc);

    const run = b.addRunArtifact(tests);
    const named = b.step("phase1-helper-ports-c-anchor-chain-replay", "Run the Lane 10 anchor-chain helper replay");
    named.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 10 anchor-chain helper replay");
    test_step.dependOn(&run.step);
    b.default_step.dependOn(&run.step);
}
