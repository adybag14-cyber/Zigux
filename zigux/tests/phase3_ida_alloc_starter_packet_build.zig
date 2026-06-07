const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);
    root_module.addImport("ida_alloc_view", ida_alloc_view);

    const unit_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet-test",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-ida-alloc-starter-packet-test",
        "Run the Phase 3 ida allocation starter-packet self-check",
    );
    test_step.dependOn(&run_unit_tests.step);

    const default_step = b.step("test", "Run the Phase 3 ida allocation starter-packet self-check");
    default_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(default_step);
}
