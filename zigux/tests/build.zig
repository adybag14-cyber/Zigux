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

fn addPhase1HostToolsSmoke(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_host_tools_smoke.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });

    bitmap_module.addImport("find_bit", find_bit_module);
    root_module.addImport("argv_split", argv_split_module);
    root_module.addImport("cmdline", cmdline_module);
    root_module.addImport("find_bit", find_bit_module);
    root_module.addImport("bitmap", bitmap_module);

    const tests = b.addTest(.{
        .name = "phase1-host-tools-smoke",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3DevTStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("dev_t_binding", dev_t_binding);
    root_module.addImport("uapi_version", uapi_version);

    const tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);
    const phase3_dev_t_starter_packet = addPhase3DevTStarterPacket(b, target, optimize);

    // Keep the shared tests root centered on anchors that are still present on
    // current master while reintroducing a compact Phase 1 host-tools smoke path.
    const phase12_virtio_net_survey = addSurveyTest(
        b,
        "phase12-virtio-net-survey",
        "phase12_virtio_net_survey.zig",
        target,
        optimize,
    );

    const phase1_step = b.step(
        "phase1-host-tools-smoke",
        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
    );
    phase1_step.dependOn(&phase1_host_tools_smoke.step);

    const phase3_step = b.step(
        "phase3-dev-t-starter-packet",
        "Run the shared Phase 3 dev_t starter packet from zigux/tests",
    );
    phase3_step.dependOn(&phase3_dev_t_starter_packet.step);

    const phase12_step = b.step(
        "phase12-virtio-net-survey",
        "Run the Phase 12 virtio net survey anchor from the shared tests root",
    );
    phase12_step.dependOn(&phase12_virtio_net_survey.step);

    const smoke_step = b.step(
        "smoke",
        "Run the currently live shared survey anchors from zigux/tests",
    );
    smoke_step.dependOn(&phase1_host_tools_smoke.step);
    smoke_step.dependOn(&phase3_dev_t_starter_packet.step);
    smoke_step.dependOn(&phase12_virtio_net_survey.step);

    const test_step = b.step(
        "test",
        "Run the shared Zigux tests-root survey smoke",
    );
    test_step.dependOn(&phase1_host_tools_smoke.step);
    test_step.dependOn(&phase3_dev_t_starter_packet.step);
    test_step.dependOn(&phase12_virtio_net_survey.step);
}
