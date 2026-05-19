const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_hweight_edges.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });

    root_module.addImport("ctype", ctype_module);
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-ctype-hweight-edges",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("phase1-ctype-hweight-edges", "Run the Phase 1 ctype+hweight edge replay");
    test_step.dependOn(&run_tests.step);
}
