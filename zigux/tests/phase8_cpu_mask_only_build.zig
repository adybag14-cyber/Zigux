const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const cpu_mask_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });

    const verify_root_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/cpu_mask_verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_options = b.addOptions();
    test_options.addOption([]const u8, "repo_root", b.pathFromRoot("../.."));

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase8_cpu_mask.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("cpu_mask", cpu_mask_module);
    root_module.addOptions("build_options", test_options);

    const packet_sync_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_cpu_mask_packet_sync.zig"),
        .target = target,
        .optimize = optimize,
    });
    packet_sync_root_module.addOptions("build_options", test_options);

    const unit_tests = b.addTest(.{
        .name = "phase8-cpu-mask-tests",
        .root_module = root_module,
    });

    const verify_tests = b.addTest(.{
        .name = "phase8-cpu-mask-verify-tests",
        .root_module = verify_root_module,
    });

    const packet_sync_tests = b.addTest(.{
        .name = "phase8-cpu-mask-packet-sync-tests",
        .root_module = packet_sync_root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const run_verify_tests = b.addRunArtifact(verify_tests);
    const run_packet_sync_tests = b.addRunArtifact(packet_sync_tests);
    // Legacy note marker: run the focused cpu-mask build shard.
    const test_step = b.step("test", "Run focused Phase 8 cpu-mask tests");
    test_step.dependOn(&run_unit_tests.step);
    test_step.dependOn(&run_verify_tests.step);
    test_step.dependOn(&run_packet_sync_tests.step);
}
