const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const test_module = b.createModule(.{
        .root_source_file = b.path("genksyms_delayed_positionals_request_executable_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane23-genksyms-delayed-positionals-request-executable-tests",
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "lane23-genksyms-delayed-positionals-request-executable",
        "Run the Lane 23 delayed-positionals genksyms executable proof.",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 23 delayed-positionals genksyms executable proof.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
