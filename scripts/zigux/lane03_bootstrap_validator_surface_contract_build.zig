const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane03_bootstrap_validator_surface_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "lane03-bootstrap-validator-surface-contract",
        "Validate the Lane 03 bootstrap validator required-path, marker, workflow-line, and policy marker contract",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 03 bootstrap validator surface contract tests");
    test_step.dependOn(&run_tests.step);
}
