const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const sample_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/kobject_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    const test_module = b.createModule(.{
        .root_source_file = b.path("phase5_kobject_example.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("kobject_example_sample", sample_module);

    const tests = b.addTest(.{
        .name = "phase5-kobject-example-tests",
        .root_module = test_module,
    });
    const run = b.addRunArtifact(tests);

    const test_step = b.step("test", "Run focused Phase 5 kobject sample checks");
    test_step.dependOn(&run.step);
}
