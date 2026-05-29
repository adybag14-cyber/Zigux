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

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });

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

    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);

    const abi_tests_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_tests_module.addImport("abi_bindings", abi_bindings_module);
    abi_tests_module.addImport("allocator_policy", allocator_policy_module);
    abi_tests_module.addImport("export_shim", export_shim_module);
    abi_tests_module.addImport("header_family_binding", header_family_binding_module);
    abi_tests_module.addImport("layout_assert", layout_assert_module);
    abi_tests_module.addImport("narrow_unsafe", unsafe_policy_module);
    abi_tests_module.addImport("panic_policy", panic_policy_module);
    abi_tests_module.addImport("unsafe_policy", unsafe_policy_module);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_allocator_policy_pair_abi_tests",
        .root_module = abi_tests_module,
    });
    const allocator_policy_tests = b.addTest(.{
        .name = "phase3_abi_allocator_policy_pair_allocator_policy_tests",
        .root_module = allocator_policy_module,
    });

    const run_abi_tests = b.addRunArtifact(abi_tests);
    const run_allocator_policy_tests = b.addRunArtifact(allocator_policy_tests);

    const test_step = b.step(
        "phase3-abi-allocator-policy-pair-test",
        "Run the focused Phase 3 ABI plus allocator policy pair replay",
    );
    test_step.dependOn(&run_abi_tests.step);
    test_step.dependOn(&run_allocator_policy_tests.step);
}
