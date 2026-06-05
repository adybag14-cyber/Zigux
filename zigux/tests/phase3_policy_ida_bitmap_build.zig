const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_surface_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface_module.addImport("abi_bindings", abi_bindings_module);

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);
    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);
    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_bindings_module);
    unsafe_policy_module.addImport("narrow", narrow_surface_module);
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path("../helpers/layout_assert.zig"),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const ida_bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const policy_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_policy_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    policy_packet_module.addImport("abi_bindings", abi_bindings_module);
    policy_packet_module.addImport("allocator_policy", allocator_policy_module);
    policy_packet_module.addImport("panic_policy", panic_policy_module);
    policy_packet_module.addImport("unsafe_policy", unsafe_policy_module);
    policy_packet_module.addImport("layout_assert", layout_assert_module);
    policy_packet_module.addImport("narrow_surface", narrow_surface_module);

    const ida_bitmap_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_packet_module.addImport("ida_bitmap_view", ida_bitmap_view_module);

    const policy_tests = b.addTest(.{
        .name = "phase3-policy-starter-packet",
        .root_module = policy_packet_module,
    });
    const ida_bitmap_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet",
        .root_module = ida_bitmap_packet_module,
    });

    const run_policy_tests = b.addRunArtifact(policy_tests);
    const run_ida_bitmap_tests = b.addRunArtifact(ida_bitmap_tests);

    const test_step = b.step(
        "phase3-policy-ida-bitmap-test",
        "Run the Phase 3 policy and IDA-bitmap starter packets together",
    );
    test_step.dependOn(&run_policy_tests.step);
    test_step.dependOn(&run_ida_bitmap_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 policy and IDA-bitmap starter packets");
    default_test_step.dependOn(test_step);
}
