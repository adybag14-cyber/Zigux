const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);
    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);
    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("uapi_version", uapi_version_module);
    const header_family_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding_module.addImport("abi_bindings", abi_bindings_module);
    header_family_binding_module.addImport("dev_t_binding", dev_t_binding_module);
    header_family_binding_module.addImport("version_binding", version_binding_module);
    header_family_binding_module.addImport("uapi_version", uapi_version_module);

    const narrow_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_module.addImport("abi_bindings", abi_bindings_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);
    export_shim_module.addImport("uapi_dev_t", uapi_dev_t_module);
    export_shim_module.addImport("uapi_version", uapi_version_module);

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    bitmap_view_module.addImport("narrow_unsafe", narrow_module);

    const cpumask_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_module.addImport("bitmap_view", bitmap_view_module);

    const abi_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_root_module.addImport("abi_bindings", abi_bindings_module);
    abi_root_module.addImport("allocator_policy", allocator_policy_module);
    abi_root_module.addImport("export_shim", export_shim_module);
    abi_root_module.addImport("header_family_binding", header_family_binding_module);
    abi_root_module.addImport("layout_assert", layout_assert_module);
    abi_root_module.addImport("narrow_unsafe", narrow_module);
    abi_root_module.addImport("panic_policy", panic_policy_module);
    abi_root_module.addImport("unsafe_policy", unsafe_policy_module);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_cpumask_view_pair_abi_tests",
        .root_module = abi_root_module,
    });
    const cpumask_view_tests = b.addTest(.{
        .name = "phase3_abi_cpumask_view_pair_cpumask_view_tests",
        .root_module = cpumask_view_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_cpumask_view_tests = b.addRunArtifact(cpumask_view_tests);

    const pair_step = b.step(
        "phase3-abi-cpumask-view-pair-test",
        "Run the Phase 3 ABI and cpumask view pair tests",
    );
    pair_step.dependOn(&run_abi_tests.step);
    pair_step.dependOn(&run_cpumask_view_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI and cpumask view pair tests");
    test_step.dependOn(pair_step);
}
