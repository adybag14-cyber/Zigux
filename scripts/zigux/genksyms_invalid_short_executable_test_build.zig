const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_invalid_short_executable_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "lane23-genksyms-invalid-short-executable",
        "Run the Lane 23 genksyms invalid-short executable proof",
    );
    route_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 23 genksyms invalid-short executable proof");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}
