const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const rbtree_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/rbtree_root.zig"),
        .target = target,
        .optimize = optimize,
    });
    rbtree_bindings.addImport("abi_bindings", abi_bindings);

    const rbtree_root_view = b.createModule(.{
        .root_source_file = b.path("../helpers/rbtree_root_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    rbtree_root_view.addImport("rbtree_bindings", rbtree_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_rbtree_root_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree_bindings", rbtree_bindings);
    root_module.addImport("rbtree_root_view", rbtree_root_view);

    const unit_tests = b.addTest(.{
        .name = "phase3-rbtree-root-starter-packet",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-rbtree-root-starter-packet",
        "Run the Phase 3 rbtree root starter packet",
    );
    test_step.dependOn(&run_unit_tests.step);
}
