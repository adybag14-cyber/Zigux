const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view.addImport("notifier_abi", notifier_abi);

    const notifier_root = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_root.addImport("notifier_abi", notifier_abi);
    notifier_root.addImport("notifier_view", notifier_view);

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
    const ida_range_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view.addImport("ida_bitmap_view", ida_bitmap_view);
    ida_range_view.addImport("ida_alloc_view", ida_alloc_view);

    const ida_range_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_root.addImport("ida_bitmap_view", ida_bitmap_view);
    ida_range_root.addImport("ida_range_view", ida_range_view);

    const notifier_tests = b.addTest(.{
        .root_module = notifier_root,
    });
    const run_notifier_tests = b.addRunArtifact(notifier_tests);

    const ida_range_tests = b.addTest(.{
        .root_module = ida_range_root,
    });
    const run_ida_range_tests = b.addRunArtifact(ida_range_tests);

    const test_step = b.step(
        "phase3-notifier-ida-range-test",
        "Run the Phase 3 notifier and IDA range starter packets",
    );
    test_step.dependOn(&run_notifier_tests.step);
    test_step.dependOn(&run_ida_range_tests.step);

    const default_step = b.step("test", "Run the Phase 3 notifier and IDA range starter packets");
    default_step.dependOn(&run_notifier_tests.step);
    default_step.dependOn(&run_ida_range_tests.step);
}
