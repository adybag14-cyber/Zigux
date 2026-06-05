const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_missing_required_after_positionals_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-missing-required-after-positionals-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-missing-required-after-positionals",
        "Run genksyms missing-required after positionals tests",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run genksyms missing-required after positionals tests");
    test_step.dependOn(&run_tests.step);
}
