const std = @import("std");

fn addPhase3AbiDevTPair(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
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
    uapi_version.addImport("abi_bindings", abi_bindings);
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
    const header_family_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding.addImport("abi_bindings", abi_bindings);
    header_family_binding.addImport("dev_t_binding", dev_t_binding);
    header_family_binding.addImport("version_binding", version_binding);
    header_family_binding.addImport("uapi_version", uapi_version);
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);
    const layout_assert = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert.addImport("abi_bindings", abi_bindings);
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
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow);

    const abi_tests = b.addTest(.{
        .name = "phase3_abi_dev_t_pair_abi",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    abi_tests.root_module.addImport("abi_bindings", abi_bindings);
    abi_tests.root_module.addImport("allocator_policy", allocator_policy);
    abi_tests.root_module.addImport("export_shim", export_shim);
    abi_tests.root_module.addImport("header_family_binding", header_family_binding);
    abi_tests.root_module.addImport("layout_assert", layout_assert);
    abi_tests.root_module.addImport("panic_policy", panic_policy);
    abi_tests.root_module.addImport("unsafe_policy", unsafe_policy);

    const dev_t_tests = b.addTest(.{
        .name = "phase3_abi_dev_t_pair_dev_t",
        .root_module = uapi_dev_t,
    });

    const abi_run = b.addRunArtifact(abi_tests);
    const dev_t_run = b.addRunArtifact(dev_t_tests);
    const pair = b.step(
        "phase3-abi-dev-t-pair-test",
        "Run the Phase 3 ABI binding contract beside the uapi dev_t packet",
    );
    pair.dependOn(&abi_run.step);
    pair.dependOn(&dev_t_run.step);
    return pair;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const pair_step = addPhase3AbiDevTPair(b, target, optimize);
    const test_step = b.step("test", "Run the Phase 3 ABI plus uapi dev_t pair-build shard");
    test_step.dependOn(pair_step);
}
