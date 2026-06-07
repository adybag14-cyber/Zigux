const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const debug_after_request_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("genksyms_debug_after_request_inputs_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_debug_after_request_tests = b.addRunArtifact(debug_after_request_tests);

    const debug_after_request_step = b.step(
        "lane23-genksyms-debug-after-request-inputs",
        "Run Lane 23 genksyms debug-after-request input proof",
    );
    debug_after_request_step.dependOn(&run_debug_after_request_tests.step);

    const test_step = b.step("test", "Run Lane 23 genksyms debug-after-request input proof");
    test_step.dependOn(&run_debug_after_request_tests.step);
    b.default_step.dependOn(&run_debug_after_request_tests.step);
}
