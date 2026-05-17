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

fn addPhase3DevTStarterPacketTest(
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

fn addPhase3ErrPtrXarrayStarterPacketTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // This shared root intentionally wires only live survey and starter-packet
    // tests that current master already carries, so the tests root remains
    // runnable without reviving older Phase 1 harness routes that are absent.
    const phase12_virtio_net_survey = addSurveyTest(
        b,
        "phase12-virtio-net-survey",
        "phase12_virtio_net_survey.zig",
        target,
        optimize,
    );
    const phase3_dev_t_starter_packet = addPhase3DevTStarterPacketTest(
        b,
        target,
        optimize,
    );
    const phase3_errptr_xarray_starter_packet = addPhase3ErrPtrXarrayStarterPacketTest(
        b,
        target,
        optimize,
    );

    const phase12_step = b.step(
        "phase12-virtio-net-survey",
        "Run the Phase 12 virtio net survey anchor from the shared tests root",
    );
    phase12_step.dependOn(&phase12_virtio_net_survey.step);

    const phase3_dev_t_step = b.step(
        "phase3-dev-t-starter-packet",
        "Run the Phase 3 dev_t starter packet from the shared tests root",
    );
    phase3_dev_t_step.dependOn(&phase3_dev_t_starter_packet.step);

    const phase3_errptr_xarray_step = b.step(
        "phase3-errptr-xarray-starter-packet",
        "Run the Phase 3 err_ptr/xarray starter packet from the shared tests root",
    );
    phase3_errptr_xarray_step.dependOn(&phase3_errptr_xarray_starter_packet.step);

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
