const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("confdata_bridge_auto_conf_escape_surface_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "confdata-bridge-auto-conf-escape-surface-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "confdata-bridge-auto-conf-escape-surface",
        "Run confdata bridge auto.conf escape-surface tests",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run confdata bridge auto.conf escape-surface tests");
    test_step.dependOn(&run_tests.step);
}
