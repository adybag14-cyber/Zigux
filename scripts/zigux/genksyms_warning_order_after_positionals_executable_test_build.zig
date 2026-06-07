const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const warning_order_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_warning_order_after_positionals_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_warning_order_tests = b.addRunArtifact(warning_order_tests);

    const warning_order_step = b.step(
        "lane23-genksyms-warning-order-after-positionals-executable",
        "Run Lane 23 genksyms warning-order executable proof",
    );
    warning_order_step.dependOn(&run_warning_order_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms warning-order executable proof");
    test_step.dependOn(&run_warning_order_tests.step);
    b.default_step.dependOn(&run_warning_order_tests.step);
}
