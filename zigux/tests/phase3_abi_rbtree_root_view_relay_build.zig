const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_rbtree_root_view_relay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-rbtree-root-view-relay-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const relay_step = b.step(
        "phase3-abi-rbtree-root-view-relay-test",
        "Run the focused Phase 3 ABI rbtree root view relay replay",
    );
    relay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 3 ABI rbtree root view relay replay");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(test_step);
}
