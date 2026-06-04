const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    const header_family_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
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
    const narrow_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });

    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);
    header_family_binding_module.addImport("abi_bindings", abi_bindings_module);
    header_family_binding_module.addImport("dev_t_binding", dev_t_binding_module);
    header_family_binding_module.addImport("version_binding", version_binding_module);
    header_family_binding_module.addImport("uapi_version", uapi_version_module);
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);
    narrow_module.addImport("abi_bindings", abi_bindings_module);
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_module);
    version_binding_module.addImport("uapi_version", uapi_version_module);
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const abi_replay_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_replay_module.addImport("abi_bindings", abi_bindings_module);
    abi_replay_module.addImport("allocator_policy", allocator_policy_module);
    abi_replay_module.addImport("export_shim", export_shim_module);
    abi_replay_module.addImport("header_family_binding", header_family_binding_module);
    abi_replay_module.addImport("layout_assert", layout_assert_module);
    abi_replay_module.addImport("panic_policy", panic_policy_module);
    abi_replay_module.addImport("unsafe_policy", unsafe_policy_module);

    const abi_replay_tests = b.addTest(.{
        .name = "phase3-abi-replay-test",
        .root_module = abi_replay_module,
    });
    const core_binding_tests = b.addTest(.{
        .name = "phase3-abi-core-binding-test",
        .root_module = abi_bindings_module,
    });

    const run_abi_replay_tests = b.addRunArtifact(abi_replay_tests);
    const run_core_binding_tests = b.addRunArtifact(core_binding_tests);
    const pair_step = b.step(
        "phase3-abi-core-binding-pair-test",
        "Run the Phase 3 ABI replay beside the core ABI binding tests",
    );
    pair_step.dependOn(&run_abi_replay_tests.step);
    pair_step.dependOn(&run_core_binding_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI core binding pair tests");
    test_step.dependOn(pair_step);
}
