const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings_module.addImport("notifier_abi", notifier_abi_module);

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("abi_bindings", abi_bindings_module);
    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const header_family_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding_module.addImport("abi_bindings", abi_bindings_module);
    header_family_binding_module.addImport("dev_t_binding", dev_t_binding_module);
    header_family_binding_module.addImport("version_binding", version_binding_module);
    header_family_binding_module.addImport("uapi_version", uapi_version_module);

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

    const panic_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);

    const allocator_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);

    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_unsafe_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_helpers_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const phase3_abi_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase3_abi_module.addImport("abi_bindings", abi_bindings_module);
    phase3_abi_module.addImport("allocator_policy", allocator_policy_helpers_module);
    phase3_abi_module.addImport("export_shim", export_shim_module);
    phase3_abi_module.addImport("header_family_binding", header_family_binding_module);
    phase3_abi_module.addImport("layout_assert", layout_assert_module);
    phase3_abi_module.addImport("panic_policy", panic_policy_helpers_module);
    phase3_abi_module.addImport("unsafe_policy", unsafe_policy_helpers_module);

    const phase3_abi_tests = b.addTest(.{
        .name = "phase3_abi_allocator_policy_pair_abi_tests",
        .root_module = phase3_abi_module,
    });
    const run_phase3_abi_tests = b.addRunArtifact(phase3_abi_tests);

    const allocator_policy_tests = b.addTest(.{
        .name = "phase3_abi_allocator_policy_pair_allocator_tests",
        .root_module = allocator_policy_helpers_module,
    });
    const run_allocator_policy_tests = b.addRunArtifact(allocator_policy_tests);

    const pair_step = b.step(
        "phase3-abi-allocator-policy-pair-test",
        "Run the Phase 3 ABI replay beside allocator-policy helper tests",
    );
    pair_step.dependOn(&run_phase3_abi_tests.step);
    pair_step.dependOn(&run_allocator_policy_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 ABI and allocator-policy pair tests",
    );
    test_step.dependOn(pair_step);
}
