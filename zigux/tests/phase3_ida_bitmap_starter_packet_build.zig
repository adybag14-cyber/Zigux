const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);

    const unit_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet-test",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-ida-bitmap-starter-packet-test",
        "Run the Phase 3 ida bitmap starter-packet self-check",
    );
    test_step.dependOn(&run_unit_tests.step);
}
