const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const file_path_handle_bridge_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    const file_path_handle_bridge_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_file_path_handle_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    file_path_handle_bridge_root_module.addImport(
        "file_path_handle_bridge",
        file_path_handle_bridge_module,
    );

    const file_path_handle_bridge_tests = b.addTest(.{
        .name = "phase8-file-path-handle-bridge-tests",
        .root_module = file_path_handle_bridge_root_module,
    });
    const run_file_path_handle_bridge_tests = b.addRunArtifact(
        file_path_handle_bridge_tests,
    );

    const test_step = b.step("test", "Run focused Phase 8 file-path handle bridge tests");
    test_step.dependOn(&run_file_path_handle_bridge_tests.step);
    b.default_step.dependOn(test_step);
}
