const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view_module.addImport("notifier_abi", notifier_abi_module);

    const ida_bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const notifier_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_packet_module.addImport("notifier_abi", notifier_abi_module);
    notifier_packet_module.addImport("notifier_view", notifier_view_module);

    const ida_bitmap_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_packet_module.addImport("ida_bitmap_view", ida_bitmap_view_module);

    const notifier_tests = b.addTest(.{
        .name = "phase3-notifier-starter-packet",
        .root_module = notifier_packet_module,
    });
    const ida_bitmap_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet",
        .root_module = ida_bitmap_packet_module,
    });

    const run_notifier_tests = b.addRunArtifact(notifier_tests);
    const run_ida_bitmap_tests = b.addRunArtifact(ida_bitmap_tests);

    const test_step = b.step(
        "phase3-notifier-ida-bitmap-test",
        "Run the Phase 3 notifier and IDA-bitmap starter packets together",
    );
    test_step.dependOn(&run_notifier_tests.step);
    test_step.dependOn(&run_ida_bitmap_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 notifier and IDA-bitmap starter packets");
    default_test_step.dependOn(test_step);
}
