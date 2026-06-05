const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_retry_delay_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named = b.step("install-zig-retry-delay-contract", "Run Lane 18 install-zig retry delay contract");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 18 install-zig retry delay contract tests");
    test_step.dependOn(&run_tests.step);
}
