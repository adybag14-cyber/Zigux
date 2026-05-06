const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../../zigux/bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../../zigux/unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../../zigux/helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_module.addImport("abi_bindings", abi_bindings_module);
    bitmap_view_module.addImport("narrow_unsafe", narrow_unsafe_module);

    const runtime_bitmap_sample_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    runtime_bitmap_sample_module.addImport("bitmap_view", bitmap_view_module);

    const top_bit_contract_module = b.createModule(.{
        .root_source_file = b.path("runtime_bitmap_top_bit_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    top_bit_contract_module.addImport("runtime_bitmap_sample", runtime_bitmap_sample_module);

    const top_bit_contract_tests = b.addTest(.{
        .name = "phase9-runtime-bitmap-top-bit-contract-tests",
        .root_module = top_bit_contract_module,
    });
    const run_top_bit_contract_tests = b.addRunArtifact(top_bit_contract_tests);

    const test_step = b.step("test", "Run focused runtime bitmap top-bit sample contract");
    test_step.dependOn(&run_top_bit_contract_tests.step);
}
