const std = @import("std");

fn addPhase3PolicyStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);
    const narrow_surface = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow_surface);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("panic_policy", panic_policy);
    root_module.addImport("allocator_policy", allocator_policy);
    root_module.addImport("unsafe_policy", unsafe_policy);
    root_module.addImport("layout_assert", layout_assert);
    root_module.addImport("narrow_surface", narrow_surface);

    const tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3HeaderFamilyBinding(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
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
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);

    const root_module = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("dev_t_binding", dev_t_binding);
    root_module.addImport("version_binding", version_binding);
    root_module.addImport("uapi_version", uapi_version);

    const tests = b.addTest(.{
        .name = "phase3-header-family-binding",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const policy_tests = addPhase3PolicyStarterPacket(b, target, optimize);
    const header_family_tests = addPhase3HeaderFamilyBinding(b, target, optimize);

    const lane_step = b.step(
        "phase3-policy-header-family-test",
        "Run the Phase 3 policy starter packet with the header-family binding packet",
    );
    lane_step.dependOn(&policy_tests.step);
    lane_step.dependOn(&header_family_tests.step);

    const test_step = b.step("test", "Run the Phase 3 policy/header-family standalone shard");
    test_step.dependOn(lane_step);
}
