const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const narrow_surface = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface.addImport("abi_bindings", abi_bindings);
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
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy.addImport("abi_bindings", abi_bindings);
    unsafe_policy.addImport("narrow", narrow_surface);
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);
    const header_family = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family.addImport("abi_bindings", abi_bindings);
    header_family.addImport("dev_t_binding", dev_t_binding);
    header_family.addImport("version_binding", version_binding);
    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view.addImport("abi_bindings", abi_bindings);
    bitmap_view.addImport("narrow_unsafe", narrow_surface);
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_view.addImport("abi_bindings", abi_bindings);
    ida_bitmap_view.addImport("bitmap_view", bitmap_view);
    ida_bitmap_view.addImport("narrow_unsafe", narrow_surface);
    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("abi_bindings", abi_bindings);
    ida_alloc_view.addImport("bitmap_view", bitmap_view);
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);
    ida_alloc_view.addImport("narrow_unsafe", narrow_surface);

    const ida_alloc_packet = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_packet.addImport("ida_alloc_view", ida_alloc_view);
    ida_alloc_packet.addImport("ida_bitmap_view", ida_bitmap_view);

    const abi_packet = b.createModule(.{
        .root_source_file = b.path("phase3_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_packet.addImport("abi_bindings", abi_bindings);
    abi_packet.addImport("allocator_policy", allocator_policy);
    abi_packet.addImport("export_shim", export_shim);
    abi_packet.addImport("header_family_binding", header_family);
    abi_packet.addImport("layout_assert", layout_assert);
    abi_packet.addImport("panic_policy", panic_policy);
    abi_packet.addImport("unsafe_policy", unsafe_policy);

    const ida_alloc_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = ida_alloc_packet,
    });
    const abi_tests = b.addTest(.{
        .name = "phase3-abi-packet",
        .root_module = abi_packet,
    });
    const run_ida_alloc = b.addRunArtifact(ida_alloc_tests);
    const run_abi = b.addRunArtifact(abi_tests);

    const ida_alloc_abi_step = b.step(
        "phase3-ida-alloc-abi-test",
        "Run the shared Phase 3 IDA allocation starter packet beside the shared Phase 3 ABI packet",
    );
    ida_alloc_abi_step.dependOn(&run_ida_alloc.step);
    ida_alloc_abi_step.dependOn(&run_abi.step);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation plus ABI standalone shard");
    test_step.dependOn(ida_alloc_abi_step);
}
