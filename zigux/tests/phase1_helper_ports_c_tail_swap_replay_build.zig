const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const test_step = b.step("phase1-helper-ports-c-tail-swap-replay", "Run the Lane 10 helper ports C tail-swap replay");
    const alias_step = b.step("test", "Run the Lane 10 helper ports C tail-swap replay");

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_helper_ports_c_tail_swap_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    tests.root_module.addImport("slab", b.createModule(.{ .root_source_file = b.path("../../tools/lib/slab.zig") }));
    tests.root_module.addImport("str_error_r", b.createModule(.{ .root_source_file = b.path("../../tools/lib/str_error_r.zig") }));
    tests.root_module.addImport("vsprintf", b.createModule(.{ .root_source_file = b.path("../../tools/lib/vsprintf.zig") }));
    tests.root_module.addImport("zalloc", b.createModule(.{ .root_source_file = b.path("../../tools/lib/zalloc.zig") }));

    const run_tests = b.addRunArtifact(tests);
    test_step.dependOn(&run_tests.step);
    alias_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
