const std = @import("std");

fn addSurveyTest(
    b: *std.Build,
    name: []const u8,
    root_source_file: []const u8,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path(root_source_file),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = name,
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // This shared root intentionally wires only survey tests that are still
    // present on current master, so the tests root remains runnable without
    // reviving older Phase 1 harness routes that are currently absent.
    const phase12_virtio_net_survey = addSurveyTest(
        b,
        "phase12-virtio-net-survey",
        "phase12_virtio_net_survey.zig",
        target,
        optimize,
    );

    const phase12_step = b.step(
        "phase12-virtio-net-survey",
        "Run the Phase 12 virtio net survey anchor from the shared tests root",
    );
    phase12_step.dependOn(&phase12_virtio_net_survey.step);

    const smoke_step = b.step(
        "smoke",
        "Run the currently live shared survey anchors from zigux/tests",
    );
    smoke_step.dependOn(&phase12_virtio_net_survey.step);

    const test_step = b.step(
        "test",
        "Run the shared Zigux tests-root survey smoke",
    );
    test_step.dependOn(&phase12_virtio_net_survey.step);
}
